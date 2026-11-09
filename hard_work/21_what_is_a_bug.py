# 1.1. Это не баг [, а плохой дизайн API] - нулевой swap превращается в пустую строку.
# В compute-api размер swap хранится числом, но клиент получает либо число,
# либо строку :)
# Выглядит плохо, но такой формат закреплён в API-контракте и тестах

class FlavorDetailResponse(BaseModel):
    ...
    swap: int | str = ''

    @classmethod
    def from_domain(cls, flavor, href):
        return cls(
            id=flavor.flavorid,
            name=flavor.name,
            ram=flavor.memory_mb,
            vcpus=flavor.vcpus,
            disk=flavor.root_gb,
            swap=flavor.swap or '',
            ephemeral_gb=flavor.ephemeral_gb or 0,
            is_public=flavor.is_public,
            disabled=flavor.disabled,
            rxtx_factor=flavor.rxtx_factor,
            extra_specs=flavor.extra_specs or {},
            links=[
                LinkElement(href=href, rel='self'),
                LinkElement(href=href, rel='bookmark'),
            ],
        )


# 1.2. Это не баг - снова типы. Тип agent_id зависит от операции.
# В списке агентов Nova возвращает числовой id из объекта, а при update —
# строковый id из URL. validate_integer проверяет значение, но результат
# проверки не присваивается полю. Несогласованность сохранена
# ради обратно совместимости. Здесь, мне кажется, можно было бы просто более выразительно это написать.
# Ну или хотя бы комментарий оставить.

class AgentController:
    def index(self, req):
        ...
        agents = []
        builds = objects.AgentList.get_all(context, hypervisor=hypervisor)
        for agent_build in builds:
            agents.append({
                'hypervisor': agent_build.hypervisor,
                'os': agent_build.os,
                'architecture': agent_build.architecture,
                'version': agent_build.version,
                'md5hash': agent_build.md5hash,
                'agent_id': agent_build.id,
                'url': agent_build.url,
            })
        return {'agents': agents}

    def update(self, req, id, body):
        ...
        try:
            utils.validate_integer(id, 'id')
        except exception.InvalidInput as exc:
            raise webob.exc.HTTPBadRequest(explanation=exc.format_message())
        ...
        return {
            'agent': {
                'agent_id': id,
                'version': version,
                'url': url,
                'md5hash': md5hash,
            }
        }


# 2.1. Не баг, а технический долг и хрупкость. Преобразование Flavor продублировано.
# Два метода FlavorsRepo вручную перечисляют одинаковые поля модели.
# Отличается только extra_specs. То есть надо помнить, что менять надо в двух местах.
# А репозиторий большой...
# Здесь на самом деле вопрос в другом - зачем делать отдельный метод для получения extra specs, если
# в итоге это поле все равно nullable?

class FlavorsRepo:
    async def get_all(
        self, conn, project_id, filters, sort_key, sort_dir, limit, marker
    ):
        ...
        result = await conn.execute(query)
        rows = result.all()
        return [
            models.Flavor(
                id=row.id,
                name=row.name,
                memory_mb=row.memory_mb,
                vcpus=row.vcpus,
                root_gb=row.root_gb,
                ephemeral_gb=row.ephemeral_gb,
                flavorid=row.flavorid,
                swap=row.swap,
                vcpu_weight=row.vcpu_weight,
                disabled=row.disabled,
                is_public=row.is_public,
                rxtx_factor=row.rxtx_factor,
                extra_specs=None,
            )
            for row in rows
        ]

    async def get_all_with_extra_specs(
        self, conn, project_id, filters, sort_key, sort_dir, limit, marker
    ):
        ...
        result = await conn.execute(query)
        rows = result.all()
        return [
            models.Flavor(
                id=row.id,
                name=row.name,
                memory_mb=row.memory_mb,
                vcpus=row.vcpus,
                root_gb=row.root_gb,
                ephemeral_gb=row.ephemeral_gb,
                flavorid=row.flavorid,
                swap=row.swap,
                vcpu_weight=row.vcpu_weight,
                disabled=row.disabled,
                is_public=row.is_public,
                rxtx_factor=row.rxtx_factor,
                extra_specs=None
                if row.extra_specs is None
                else json.loads(row.extra_specs),
            )
            for row in rows
        ]


# 2.2. Не баг, а смешивание ответственности.
# Работа со временем и генерация ключей находятся в одном модуле (и смех и грех).
# Даже импорт now загружает Crypto.PublicKey.RSA.

import datetime

from Crypto.PublicKey import RSA


def now():
    return datetime.datetime.now(tz=datetime.UTC)


def generate_rsa_keypair(bits=2048):
    key = RSA.generate(bits)
    private_key = key.export_key().decode('utf-8')

    pub_key = key.publickey()
    public_key_bytes = pub_key.export_key(format='OpenSSH')
    public_key = public_key_bytes.decode('utf-8')

    return public_key, private_key


# 3.1. Это сбивает с толку - extract_attrs в докстринге обещает игнорировать отсутствующие поля.
# По описанию можно ожидать, что метод соберёт только доступные атрибуты.
# По факту отсутствие поля вызывает AttributeError, если его имя заранее не перечислено в константе или в самом
# объекте, из которого мы вытаскиваем атрибуты.

from dataclasses import fields as _fields


class BaseComputeModel:
    @classmethod
    def extract_attrs(cls, something, ignore_missing=(), **kwargs):
        """Взять атрибуты из произвольного объекта, игнорируя отсутствующие."""
        for field in _fields(cls):
            if field.name in kwargs:
                continue
            if field.name in SKIP_FIELDS_FOR_EXTRACTION:
                continue

            try:
                value = getattr(something, field.name)
            except AttributeError:
                if field.name in ignore_missing:
                    continue
                raise

            kwargs[field.name] = value

        return kwargs


# 3.2. Это сбивает с толку - описание isDisabled переворачивает смысл флага.
# Так-то база с курса "Ясный код" (за который в очередной и не последний раз говорю спасибо :)


class FlavorActionSwitchDisabledRequest(BaseModel):
    disabled: Annotated[
        bool,
        Field(
            alias='isDisabled',
            description=(
                'Сделать ли флейвор активным или неактивным. '
                'true - может быть использован, '
                'false - не может быть использован'
            ),
        ),
    ]


class SwitchDisabledForFlavorUseCase(BaseFlavorUseCase):
    async def execute(self, flavor_uuid, *, disabled):
        ...
        async with self.database.transaction() as conn:
            flavor = await self.flavors.get_by_uuid(
                conn=conn,
                flavor_uuid=flavor_uuid,
                project_id=self._get_current_project_id(),
            )
            flavor.disabled = disabled
            await self.flavors.save(conn, flavor)


# 4.1. Это хрупкость - сериализация времени предполагает, что оно уже в UTC.
# Я как-то раньше недооценивал проблемы времени (хотя неоднократно читал на курсах и в
# книгах, что это очень часто проблема. Казалось бы, почему не хранить сразу в нормализованном виде?
# А вот, легаси передает привет.

def serialize_object(obj, namespace='nova'):
    ...
    if isinstance(obj, datetime.datetime):
        return obj.replace(tzinfo=None).isoformat()
    ...


moment = datetime.datetime(
    2026, 11, 9, 10, tzinfo=datetime.timezone(datetime.timedelta(hours=3))
)
serialized = serialize_object(moment)
normalized = moment.astimezone(datetime.UTC).replace(tzinfo=None).isoformat()


# 4.2. Это хрупкость - учёт изменений не замечает изменения внутри словаря.
# Метаданные хранятся в конкретном поле, их изменения не фиксируются. При этом там хранятся зоны доступности.
# То есть если мы захотим в будущем опереться на неизменность объекта как на гарантию сохранения
# старой зоны доступности (а мы вполне можем захотеть), будет трудноотлавливаемый баг.


@dataclass
class BaseComputeModel:
    track_changes: ClassVar[bool] = True

    def __post_init__(self):
        self._changes = set()

    def __setattr__(self, attr, value):
        if attr != '_changes' and type(self).track_changes:
            _changes = self.__dict__.setdefault('_changes', set())
            _changes.add(attr)
        super().__setattr__(attr, value)

    def obj_reset_changes(self, fields=None):
        if fields is None:
            self._changes.clear()
        else:
            self._changes = self._changes - set(fields)

    def obj_get_changes(self, ignore=()):
        return {
            key: getattr(self, key)
            for key in self._changes
            if key not in ignore
        }


# Что-то такое, например

def change_availability_zone(aggregate):
    aggregate.obj_reset_changes()
    aggregate.metadata['availability_zone'] = 'zone-b'
    return aggregate.obj_get_changes()


# 5.1. Это опасное «упрощение» - замена выбора memcached-сервера обычным CRC32.
# Сочетание масок и сдвига воспроизводит алгоритм клиента другого репозитория (монолита со встроенным API).
# Оно выглядит как усложнение, которое можно заменить стандартным crc32.
# Но проекты читают общий кеш и должны выбирать одинаковый сервер.
# Для показанного ключа при двух серверах исходный алгоритм выбирает сервер 1,
# а «упрощённый» — сервер 0. Записанный heartbeat окажется в другом месте.
# Это реальный случай, который я ревьюил - разработчик хотел упростить.


class MemcacheDriver:
    @staticmethod
    def _server_hash(key):
        return ((binascii.crc32(key) & 0xFFFFFFFF) >> 16) & 0x7FFF or 1

    def _server_index_for_key(self, key):
        return self._server_hash(key) % len(self._connections)


class SimplifiedMemcacheDriver(MemcacheDriver):
    @staticmethod
    def _server_hash(key):
        return binascii.crc32(key)


# 5.2. Опасная «уборка» - удалить повторные определения метода update.
# Один класс трижды определяет метод с одинаковым именем. По обычным
# правилам питона последнее определение заменяет предыдущие, поэтому первые
# два легко принять за мёртвый код. Но декоратор api_version сохраняет каждую
# функцию в отдельном реестре до замены имени, а контроллер выбирает её
# по версии запроса. Удаление дублей уберёт обработчики старых
# версий API, которые необходимы для обратной совместимости.
# Здесь, на мой взгляд, снова слабовыразительный код. Вероятно это tradeoff, но как будто
# было бы логичнее оставить в интерфейсе один метод-диспетчер, в который контроллер
# бы передавал версию. Это бы упростило жизнь разработчику,
# оставив жизнь пользователя такой же простой, какой она была раньше.

class QuotaSetsController(wsgi.Controller):
    @wsgi.Controller.api_version('2.1', MAX_PROXY_API_SUPPORT_VERSION)
    @extensions.expected_errors(400)
    @validation.schema(quota_sets.update)
    def update(self, req, id, body):
        return self._update(req, id, body, VGPU_QUOTA)

    @wsgi.Controller.api_version(
        MIN_WITHOUT_PROXY_API_SUPPORT_VERSION,
        MAX_WITHOUT_VGPU_QUOTA_SUPPORT_VERSION,
    )
    @extensions.expected_errors(400)
    @validation.schema(quota_sets.update_v236)
    def update(self, req, id, body):
        return self._update(req, id, body, FILTERED_QUOTAS + VGPU_QUOTA)

    @wsgi.Controller.api_version(MIN_WITH_VGPU_QUOTA_SUPPORT_VERSION)
    @extensions.expected_errors(400)
    @validation.schema(quota_sets.update_v242)
    def update(self, req, id, body):
        return self._update(req, id, body, FILTERED_QUOTAS)


# Рефлексия.
# Очень полезно, причем с разных точек зрения.
# 1. Становится легче формализовать свои замечания на ревью. В первую очередь из-за более явной работы
# с вероятностями. Неоднократно сталкивался с логикой разработчиков, которые мне на подобные комментарии
# отвечали что-то вроде "это не стреляет и никак не относится к текущему состоянию системы, зачем править?".
# И было очень трудно как-то объяснить, почему это не мой субъективный взгляд на вещи, а реальная опасность.
# Это на мой взгляд большая проблема, в смысле, нежелание/неумение некоторых разработчиков думать наперед.
# Не утверждаю, что я это умею делать хорошо, но это не повод не стараться.
# 2. Становится удобнее оценивать собственный код с подобных точек зрения. Сам я, разумеется, неоднократно
# оказывался в ситуации (особенно в начале карьеры), когда вроде бы код хороший, мне он субъективно нравится
# и кажется оптимальным, однако опытный коллега видит те самые вероятности и указывает мне на них.
# Мне казалось, что это нарабатывается с опытом, и во многом так и есть. Но, как и любая формализация,
# данное занятие экономит сотни (если не тысячи) человеко-часов, спустя которые начинаешь видеть подобные вещи
# просто за счет насмотренности. Вообще конечно с подобными знаниями огромная беда в индустрии.
# Это как разрешать лечить людей врачам без качественного знания физиологии (хотя и это не редкость, к сожалению).
#
# Эти два пункта, конечно, являются двумя сторонами одной медали.
#
# 3. Ну и, разумеется, в ходе выполнения данного задания было найдено некоторое количество реальных багов.
# Продолжаю работу :)