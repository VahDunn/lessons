# 1. Запрещаем ошибочное поведение на уровне интерфейса


# 1.1. Жизненный цикл task_state во время swap volume
#
# Сейчас SWAPPING_VOLUME приходится выставлять и снимать вручную. Обе записи
# это сравнить + присвоить: первая разрешена только из None, вторая - только
# из SWAPPING_VOLUME. Так параллельная операция не будет незаметно затёрта.
# Существующий reverts_task_state здесь недостаточен: он очищает state только
# при исключении, не занимает его в начале и не обслуживает успешный путь.


# Было (реальный код дополнительно сохраняет исходное исключение)

class ComputeManager(manager.Manager):

    def swap_volume(self, context, old_volume_id, new_volume_id, instance):
        instance.task_state = task_states.SWAPPING_VOLUME
        instance.save(expected_task_state=[None])

        def clear_task_state():
            instance.task_state = None
            instance.save(
                expected_task_state=[task_states.SWAPPING_VOLUME],
            )

        try:
            self._do_swap_volume(
                context, old_volume_id, new_volume_id, instance,
            )
            self.update_instance_metadata(context, instance)
        except Exception:
            # Здесь ещё надо не скрыть исходную ошибку ошибкой cleanup.
            clear_task_state()
            raise

        clear_task_state()


# Пользователь низкоуровневого интерфейса должен помнить, что нужно:
#
# 1. взять instance-lock и volume-lock в правильном порядке
# 2. выставить состояние с expected_task_state=None
# 3. выполнить операцию
# 4. снять именно своё состояние и на успешном, и на ошибочном пути
# 5. при двух исключениях сохранить исходное исключение операции
#
# Обычная проверка с raise не решит проблему - ошибка просто позднее обнаружится

# Стало

class InstanceTaskRunner(object):
    """Единственный публичный вход в lifecycle конкретной операции."""

    def run_volume_swap(self, context, instance, old_volume_id, operation):
        return self._run_exclusive(
            context=context,
            instance=instance,
            lock_keys=(instance.uuid, old_volume_id),
            task_state=task_states.SWAPPING_VOLUME,
            operation=operation,
        )

    def _run_exclusive(self, context, instance, lock_keys, task_state,
                       operation):
        # Внутри лежат локи, оба сопоставления и клинап
        # Методы изменения task_state принадлежат приватному store и наружу
        # не выдаются.
        ...


class ComputeManager(manager.Manager):

    def swap_volume(self, context, old_volume_id, new_volume_id, instance):
        def operation():
            self._do_swap_volume(
                context, old_volume_id, new_volume_id, instance,
            )
            self.update_instance_metadata(context, instance)

        return self.instance_tasks.run_volume_swap(
            context, instance, old_volume_id, operation,
        )


# У пользователя InstanceTaskRunner остался один атомарный метод.
# Он не может перепутать claim и release, очистить чужое состояние или забыть
# cleanup. Всё ещё быть ошибка из-за реальной распределённой гонки,
# но ошибочную комбинацию вызовов написать больше нельзя. Декоратор или context
# manager тоже сократил бы дублирование, но здесь вроде бы строже - из него нельзя
# получить guard и забыть войти в него.


# 1.2. Протокол отсоединения Cinder volume
#
#
# API публикует все технические шаги протокола отдельно. Поэтому вызывающий
# код может начать детач без проверки, отсоединить том не от того
# инстанса или забыть roll_detaching после ошибки.


# Было

volume = volume_api.get(context, volume_id)
volume_api.check_detach(context, volume, instance=instance)
volume_api.begin_detaching(context, volume_id)

try:
    compute_rpcapi.detach_volume(
        context,
        instance=instance,
        volume_id=volume_id,
    )
except Exception:
    volume_api.roll_detaching(context, volume_id)
    raise


# Все эти вызовы допустимы синтаксически, хотя не имеют смысла:
#
# volume_api.begin_detaching(context, available_volume_id)
# volume_api.detach(context, volume_attached_to_another_instance_id)
# volume_api.roll_detaching(context, volume_that_was_never_detaching_id)


# Стало

class VolumeCatalog(object):

    def find_attachment(self, context, instance, volume_id):
        volume = self._volume_api.get(context, volume_id)
        attachment = volume.get("attachments", {}).get(instance.uuid)

        if attachment is None:
            return None

        return AttachedVolume(
            detachment_protocol=self._detachment_protocol,
            attachment_id=attachment["attachment_id"],
            instance_uuid=instance.uuid,
            volume_id=volume_id,
        )

# Вот здесь получается связано и инкапсулировано все, что нужно для детача
# Таким образом резко уменьшается вероятность ошибки в рантайме - мы лишаем программиста возможности
# перепутать анализируемые и отсоединяемые тома, а также выбрать не тот протокол детача
class AttachedVolume(object):
    """Создаётся только VolumeCatalog для реально найденного аттача."""

    def __init__(self, detachment_protocol, attachment_id,
                 instance_uuid, volume_id):
        self._detachment_protocol = detachment_protocol
        self.attachment_id = attachment_id
        self.instance_uuid = instance_uuid
        self.volume_id = volume_id

    #  а конкретно здесь еще и реализован стандартный фолбек, если по протоколу что-то не так пойдет
    def detach(self, context, attachment, compute_rpcapi):
        try:
            self._volume_api.begin_detaching(
                context,
                attachment.volume_id,
            )

            compute_rpcapi.detach_volume(
                context,
                instance_uuid=attachment.instance_uuid,
                volume_id=attachment.volume_id,
                attachment_id=attachment.attachment_id,
            )
        except exception.VolumeUnattached:
            return DetachResult.already_detached(
                attachment.volume_id,
            )
        except Exception:
            self._volume_api.roll_detaching(
                context,
                attachment.volume_id,
            )
            raise

        return DetachResult.started(attachment.volume_id)

# и в итоге

attachment = volume_catalog.find_attachment(
    context, instance, volume_id,
)
if attachment is None:
    result = DetachResult.already_detached(volume_id)
else:
    result = attachment.detach(context, compute_rpcapi)


# Получается, что выбор варианта из достаточно комплексного ветвления делегируется автоматике почти целиком
# Множество вариантов сведено к двум


# 2. Не оставляем публичный конструктор без обязательных аргументов


# 2.1. Migration
#
#
# Migration можно создать пустым, а обязательность migration_type проверяется
# только в create(). Между конструктором и create() объект находится в
# недопустимом состоянии.


# Было

migration = objects.Migration(context=context.elevated())
migration.dest_compute = destination
migration.status = "accepted"
migration.instance_uuid = instance.uuid
migration.source_compute = instance.host
migration.migration_type = "live-migration"
migration.old_instance_type_id = instance.flavor.id
migration.new_instance_type_id = instance.flavor.id
migration.create()


# Такой код тоже разрешён конструктором и падает только в create():
broken_migration = objects.Migration(context=context)
broken_migration.create()


# Стало

class Migration(base.NovaObject):

    def __init__(self, context, migration_type, instance_uuid,
                 source_compute, old_flavor_id, new_flavor_id,
                 initial_status, dest_compute=None):
        super(Migration, self).__init__(context=context)
        self.migration_type = migration_type
        self.instance_uuid = instance_uuid
        self.source_compute = source_compute
        self.dest_compute = dest_compute
        self.old_instance_type_id = old_flavor_id
        self.new_instance_type_id = new_flavor_id
        self.status = initial_status

    @classmethod
    def live(cls, context, instance, destination, initial_status):
        return cls(
            context=context,
            migration_type=MigrationType.LIVE,
            instance_uuid=instance.uuid,
            source_compute=instance.host,
            dest_compute=destination,
            old_flavor_id=instance.flavor.id,
            new_flavor_id=instance.flavor.id,
            initial_status=initial_status,
        )


migration = Migration.live(
    context.elevated(),
    instance,
    destination,
    initial_status=MigrationStatus.ACCEPTED,
)
migration.create()


# Здесь достаточно наглядно - почему-то сначала init, а потом присвоение атрибутов
# Это недоразумение было исправлено :)

# 2.2. BuildRequest
#
#
# create() отдельно проверяет наличие instance_uuid, но конструктор разрешает
# пустой объект. Даже полный текущий вызов принимает instance, instance_uuid и
# project_id независимо, поэтому можно случайно собрать противоречивый запрос.


# Было

# Первый вариант ошибки: конструктор разрешает не передать обязательные поля.
# Исключения здесь ещё нет -- оно появится только в create().
empty_build_request = objects.BuildRequest(context)
empty_build_request.create()


# Второй вариант: связанные поля передаются независимо и могут противоречить
# друг другу. Конструктор этого тоже не запрещает.
build_request = objects.BuildRequest(
    context,
    instance=instance,
    instance_uuid=another_instance.uuid,
    project_id=instance.project_id,
    block_device_mappings=block_device_mapping,
    tags=instance_tags,
)
build_request.create()


# Стало

class BuildRequest(base.NovaObject):

    def __init__(self, context, instance, block_device_mappings, tags=None):
        super(BuildRequest, self).__init__(context=context)
        self.instance = instance
        self.instance_uuid = instance.uuid
        self.project_id = instance.project_id
        self.block_device_mappings = block_device_mappings
        self.tags = tags if tags is not None else objects.TagList()


build_request = BuildRequest(
    context=context,
    instance=instance,
    block_device_mappings=block_device_mapping,
    tags=instance_tags,
)
build_request.create()


# Что улучшено: обязательные данные задаются одной операцией, а дублирующиеся
# instance_uuid и project_id выводятся из единственного источника истины -
# Instance. Нельзя получить BuildRequest без instance/BDM или сохранить
# сериализованный Instance под UUID другого инстанса.


# 3. Заменяем примитивы типами предметной области


# 3.1. Статус миграции
#
# Тип миграции в оригинале уже ограничен EnumField, а статус всё ещё StringField.
# рядом с выборкой миграций даже есть комментарий,
# что статусы разбросаны по проекту, а done и completed дублируют друг друга.


# Было

class Migration(base.NovaObject):
    fields = {
        "status": fields.StringField(nullable=True),
        "migration_type": fields.EnumField(
            ["migration", "resize", "live-migration", "evacuation"],
            nullable=False,
        ),
    }


migration.status = "post-migrtaфываываing"  # Опечатка является допустимой строкой.
migration.save()


# Стало

class MigrationStatus(fields.BaseNovaEnum):
    ACCEPTED = "accepted"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    CONFIRMED = "confirmed"
    CREATED = "created"
    DONE = "done"
    ERROR = "error"
    FAILED = "failed"
    FINISHED = "finished"
    MIGRATING = "migrating"
    POST_MIGRATING = "post-migrating"
    PRE_MIGRATING = "pre-migrating"
    PREPARING = "preparing"
    QUEUED = "queued"
    REVERTED = "reverted"
    RUNNING = "running"
    RUNNING_POST_COPY = "running (post-copy)"

    ALL = (
        ACCEPTED, CANCELLED, COMPLETED, CONFIRMED, CREATED, DONE, ERROR,
        FAILED, FINISHED, MIGRATING, POST_MIGRATING, PRE_MIGRATING,
        PREPARING, QUEUED, REVERTED, RUNNING, RUNNING_POST_COPY,
    )

    TERMINAL = (
        CANCELLED, COMPLETED, CONFIRMED, DONE, ERROR, FAILED, REVERTED,
    )


class MigrationStatusField(fields.BaseEnumField):
    AUTO_TYPE = MigrationStatus()


class Migration(base.NovaObject):
    fields = {
        "status": MigrationStatusField(nullable=True),
    }


migration.status = MigrationStatus.POST_MIGRATING
migration.save()


# Что улучшено: словарь допустимых значений и понятие terminal находятся в
# одном месте; опечатка отлавливается при присваивании/десериализации, а не
# превращается в миграцию, которую не потом и найти-то не получится. Код можно искать и
# безопасно переименовывать. Enum пока отвечает только за словарь значений,
# допустимые переходы между ними требуют машины состояний.


# 3.2. Шина блочного устройства
#

# В проекте уже определены прикладные DiskBus и DiskBusField с конечным набором
# fdc/ide/sata/scsi/usb/virtio/..., но BlockDeviceMapping продолжает принимать
# для disk_bus произвольную строку.


# Было

class BlockDeviceMapping(base.NovaObject):
    fields = {
        "device_type": fields.BlockDeviceTypeField(nullable=True),
        "disk_bus": fields.StringField(nullable=True),
    }


bdm = BlockDeviceMapping()

# StringField проверяет только то, что передана строка. Знаний о существующих
# шинах у него нет, поэтому все эти присваивания допустимы.
bdm.disk_bus = "virtio"
bdm.disk_bus = "virito"        # Опечатка тоже допустима.
bdm.disk_bus = "авлопрвадлпр"  # Произвольная строка тоже допустима.
bdm.save()

# Ошибка обнаружится позднее: после сохранения, RPC-вызова или уже внутри
# конкретного virt driver.


# Стало

# nova/objects/fields.py уже содержит словарь значений предметной области.
class DiskBus(fields.BaseNovaEnum):
    FDC = "fdc"
    IDE = "ide"
    SATA = "sata"
    SCSI = "scsi"
    USB = "usb"
    VIRTIO = "virtio"
    XEN = "xen"
    LXC = "lxc"
    UML = "uml"

    ALL = (
        FDC, IDE, SATA, SCSI, USB, VIRTIO, XEN, LXC, UML,
    )


class DiskBusField(fields.BaseEnumField):
    # BaseEnumField вызывает DiskBus.coerce() при каждом присваивании поля.
    # Значение, которого нет в DiskBus.ALL, отклоняется немедленно.
    AUTO_TYPE = DiskBus()


class BlockDeviceMapping(base.NovaObject):
    fields = {
        "device_type": fields.BlockDeviceTypeField(nullable=True),
        "disk_bus": fields.DiskBusField(nullable=True),
    }


bdm = BlockDeviceMapping()
bdm.disk_bus = fields.DiskBus.VIRTIO

# Теперь обе ошибки останавливаются на границе объекта, до save() и RPC:
bdm.disk_bus = "virito"        # ValueError: недопустимый DiskBus.
bdm.disk_bus = "авлопрвадлпр"  # ValueError: недопустимый DiskBus.



# Рефлексия
#
# Это почти откровение :)
# С помощью таких подходов можно решить колоссальное количество ошибок, которые в текущем виде стреляют регулярно
# Руки уже немного чешутся. Остро чувствуется необходимость в практике - одного занятия очевидно недостаточно,
# чтобы видеть подобное постоянно и уметь корректно это применять. Но перспективы открываются достаточно светлые.
# Спасибо.