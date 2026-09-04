# Ясный код 3


# 2. Уровень классов


# 2.1. Класс слишком большой
#
# Файл на 10 000+ строк, в классе больше 270 методов :')
# Он создает/удаляет инстансы, сетью и дисками управляет, снапшоты делает, ресайзы,
# лайв-миграции, и много чего еще. Переделал кусок, потому что все целиком даже без наполнения очень много места
# занимало. И рефакторить это откровенно страшновато. Но я все равно предложу :)


# Было

class ComputeManager(manager.Manager):
    def __init__(self, compute_driver=None, *args, **kwargs):
        self.network_api = network.API()
        self.volume_api = cinder.API()
        self.image_api = image.API()
        self.compute_api = compute.API()
        self.compute_rpcapi = compute_rpcapi.ComputeAPI()
        self.conductor_api = conductor.API()
        self.compute_task_api = conductor.ComputeTaskAPI()
        self.scheduler_client = scheduler_client.SchedulerClient()
        self.instance_events = InstanceEvents()
        ...

    def build_and_run_instance(self, *args, **kwargs):
        ...

    def terminate_instance(self, *args, **kwargs):
        ...

    def snapshot_instance(self, *args, **kwargs):
        ...

    def attach_volume(self, *args, **kwargs):
        ...

    def live_migration(self, *args, **kwargs):
        ...

    def update_available_resource(self, *args, **kwargs):
        ...


# Стало

class ComputeManager(manager.Manager):
    """Тонкий RPC-фасад: принимает команду и передает её одному use case."""

    def __init__(self, instance_lifecycle, volume_service,
                 migration_service, resource_service, *args, **kwargs):
        self.instance_lifecycle = instance_lifecycle
        self.volume_service = volume_service
        self.migration_service = migration_service
        self.resource_service = resource_service
        super(ComputeManager, self).__init__(*args, **kwargs)

    def build_and_run_instance(self, context, instance, request):
        return self.instance_lifecycle.build(context, instance, request)

    def terminate_instance(self, context, instance):
        return self.instance_lifecycle.terminate(context, instance)

    def attach_volume(self, context, instance, volume):
        return self.volume_service.attach(context, instance, volume)

    def live_migration(self, context, instance, destination):
        return self.migration_service.start(context, instance, destination)



# 2.2. Класс слишком маленький или делает слишком мало
#
# Два класса стратегий отличаются только одним булевым флагом. Один из них вообще пуст.
# А еще вот это вот reverse = not higher глаза режет.

# Было

class _OrderedWeighStrategy(BaseWeighStrategy):
    higher = True

    def weigh(self):
        ...
        sorted_pos_val = sorted(
            pos_val_mapping.items(),
            key=lambda item: item[1],
            reverse=(not self.higher),
        )
        ...


class LowerWeighStrategy(_OrderedWeighStrategy):
    higher = False


class HigherWeighStrategy(_OrderedWeighStrategy):
    pass


STRATEGIES = {
    "lower": LowerWeighStrategy,
    "higher": HigherWeighStrategy,
}


# Стало

class OrderedWeighStrategy(BaseWeighStrategy):
    def __init__(self, weighed_obj_list, path, reverse):
        super(OrderedWeighStrategy, self).__init__(weighed_obj_list, path)
        self.reverse = reverse

    def weigh(self):
        weights = [0] * len(self.weighed_obj_list)
        values_by_position = {}

        for position, weighed_obj in enumerate(self.weighed_obj_list):
            host_value = self._get_host_attr(weighed_obj.obj)
            if host_value is not None:
                values_by_position[position] = host_value

        values_from_worst_to_best = sorted(
            values_by_position.items(),
            key=lambda item: item[1],
            reverse=self.reverse,
        )

        if not values_from_worst_to_best:
            return weights

        previous_value = values_from_worst_to_best[0][1]
        rank = 0
        for position, value in values_from_worst_to_best[1:]:
            if value != previous_value:
                rank += 1
                previous_value = value
            weights[position] = rank

        return weights


REVERSE_BY_STRATEGY = {
    "lower": True,    # high -> low: the lowest value gets the highest rank
    "higher": False,  # low -> high: the highest value gets the highest rank
}

strategy_name = statement["host"]["strategy"]
strategy = OrderedWeighStrategy(
    weighed_obj_list,
    statement["host"]["path"],
    reverse=REVERSE_BY_STRATEGY[strategy_name],
)


# 2.3. Метод выглядит более подходящим для другого класса
#
# Пример: nova/compute/manager.py::_nil_out_instance_obj_host_and_node.
# Метод ComputeManager не читает и не изменяет self, зато знает про
# Instance и вручную меняет только его данные.

# Было

class ComputeManager(manager.Manager):
    def _nil_out_instance_obj_host_and_node(self, instance, nil_az=True):
        instance.host = None
        instance.node = None
        if nil_az:
            instance.availability_zone = None


# Стало

class Instance(base.NovaObject):
    def clear_host_placement(self, clear_availability_zone=True):
        self.host = None
        self.node = None
        if clear_availability_zone:
            self.availability_zone = None


class ComputeManager(manager.Manager):
    def _reschedule(self, instance):
        instance.clear_host_placement(clear_availability_zone=False)
        ...


# Операция названа в терминах модели, а правило о связанных полях теперь живёт рядом
# с самими полями. Если NovaObject принципиально должен быть анемичным DTO, то тот же
# метод можно поместить в узкий InstancePlacementService, но не в огромный ComputeManager.


# 2.4. Класс хранит данные, которые загоняются в него во множестве мест
#

# Было

# Compute API создал пустой контейнер и заполнил свою часть.
request_spec = RequestSpec()
request_spec.flavor = new_instance_type
request_spec.pci_requests = new_pci_requests
request_spec.numa_topology = hardware.numa_get_constraints(...)
request_spec.availability_zone = availability_zone

# Conductor получил тот же объект и дописал данные попытки.
request_spec.system_scheduler_hints = system_hints
request_spec.ignore_hosts = attempted_hosts

# Scheduler filter еще раз изменил тот же объект.
request_spec.requested_destination = objects.Destination(
    host=requested_host,
    node=requested_node,
)

# Здесь RequestSpec наконец готов. Но понять это можно только прочитав всю последовательность
# (которая еще и размазана по файлу).

destination = scheduler.select_destination(request_spec)


# Стало

class RequestSpec(object):

    def __init__(self, flavor, pci_requests, numa_topology,
                 availability_zone):
        self.flavor = flavor
        self.pci_requests = pci_requests
        self.numa_topology = numa_topology
        self.availability_zone = availability_zone


class SchedulingAttempt(object):

    def __init__(self, request_spec, ignored_hosts=(), system_hints=None):
        self.request_spec = request_spec
        self.ignored_hosts = tuple(ignored_hosts)
        self.system_hints = system_hints or {}


request_spec = RequestSpec(
    flavor=new_instance_type,
    pci_requests=new_pci_requests,
    numa_topology=hardware.numa_get_constraints(...),
    availability_zone=availability_zone,
)
attempt = SchedulingAttempt(
    request_spec=request_spec,
    ignored_hosts=attempted_hosts,
    system_hints=system_hints,
)
destination = scheduler.select_destination(attempt)


# RequestSpec сразу создается целиком. Кондуктор не меняет его, а создает отдельный
# SchedulingAttempt с краткоживущими данными. Шедулер не дописывает destination во входной
# объект, а возвращает его как результат.

# 2.5. Класс зависит от деталей реализации другого класса

# Compute API вызывает приватный метод Placement-клиента и знает его внутреннее исключение :)

# Было

class API(object):
    def _validate_host_or_node(self, context, host):
        try:
            self.placement._get_provider_by_name(context, host)
        except exception.ResourceProviderNotFound:
            raise exception.ComputeHostNotFound(host=host)


# Стало

class SchedulerReportClient(object):
    def resource_provider_exists(self, context, name):
        try:
            provider = self._get_provider_by_name(context, name)
        except exception.ResourceProviderNotFound:
            return False
        return provider is not None


class API(object):
    def _validate_host_or_node(self, context, host):
        if not self.placement.resource_provider_exists(context, host):
            raise exception.ComputeHostNotFound(host=host)


# Инкапсулировал все это безобразие в публичном методе, вызывающий метод проверяет и кидает исключение, если нужно.


# 2.6. Приведение типов вниз по иерархии
#
# Метод получает DeviceBus, но затем перебирает все известные дочерние типы,
# чтобы получить строковое имя шины для metadata API.

# Было

def _get_device_bus_metadata(device):
    bus = "none"
    address = "none"

    if "bus" in device:
        if isinstance(device.bus, PCIDeviceBus):
            bus = "pci"
        elif isinstance(device.bus, USBDeviceBus):
            bus = "usb"
        elif isinstance(device.bus, SCSIDeviceBus):
            bus = "scsi"
        elif isinstance(device.bus, IDEDeviceBus):
            bus = "ide"
        else:
            return None

        if "address" in device.bus:
            address = device.bus.address

    return {"bus": bus, "address": address}

# Стало

class DeviceBus(base.NovaObject):
    METADATA_TYPE = None

    def get_meta_type(self):
        return self.METADATA_TYPE


class PCIDeviceBus(DeviceBus):
    METADATA_TYPE = "pci"
    fields = {"address": fields.PCIAddressField()}


class USBDeviceBus(DeviceBus):
    METADATA_TYPE = "usb"
    fields = {"address": fields.USBAddressField()}


class SCSIDeviceBus(DeviceBus):
    METADATA_TYPE = "scsi"
    fields = {"address": fields.SCSIAddressField()}


class IDEDeviceBus(DeviceBus):
    METADATA_TYPE = "ide"
    fields = {"address": fields.IDEAddressField()}


def _get_device_bus_metadata(device):
    bus = "none"
    address = "none"

    if "bus" in device:
        bus = device.bus.get_meta_type()
        if bus is None:
            return None
        if "address" in device.bus:
            address = device.bus.address

    return {"bus": bus, "address": address}


# get_meta_type() определен один раз и не переопределяется. Наследники задают только данные:
# имя типа и валидатор адреса. Там кстати на это висел TODO :)


# 2.7. Параллельные иерархии наследования
#
# Рядом с Image -> LocalImage -> LocalFileImage/LocalBlockImage существует
# Mount -> LoopMount/NbdMount/BlockMount. Фабрика явно связывает эти две иерархии.

# Было

class Mount(object):
    @staticmethod
    def instance_for_format(image, mountdir, partition):
        if isinstance(image, LocalFileImage):
            if image.format == FORMAT_RAW:
                return LoopMount(image, mountdir, partition)
            return NbdMount(image, mountdir, partition)
        elif isinstance(image, LocalBlockImage):
            return BlockMount(image, mountdir, partition)
        raise UnsupportedImageModel(image.__class__.__name__)


class LoopMount(Mount):
    mode = "loop"

    def _inner_get_dev(self):
        return attach_with_losetup(self.image.path)


class NbdMount(Mount):
    mode = "nbd"

    def _inner_get_dev(self):
        return attach_with_qemu_nbd(self.image.path)


class BlockMount(Mount):
    mode = "block"

    def get_dev(self):
        self.device = self.image.path
        return True


# Если добавить новый вид локального image source, понадобятся новый Image-подкласс,
# новый Mount-подкласс и ещё одна ветка фабрики.

# Стало

class Image(object):
    def __init__(self, source, image_format, mounter):
        self.source = source
        self.format = image_format
        self.mounter = mounter

    def mount(self, mount_dir, partition):
        return self.mounter.mount(self, mount_dir, partition)


class LoopMounter(object):
    def mount(self, image, mount_dir, partition):
        # бывшая реализация LoopMount.
        ...


class BlockMounter(object):
    def mount(self, image, mount_dir, partition):
        # бывшая реализация BlockMount.
        ...


raw_file_image = Image(
    source="/var/lib/nova/instances/disk",
    image_format=FORMAT_RAW,
    mounter=LoopMounter(),
)

mount = raw_file_image.mount(mount_dir, partition)


# Тип источника и способ монтирования теперь комбинируются, а не растут двумя связанными
# деревьями. Конкретный Mounter выбирается сразу, поэтому код
# монтирования больше не должен знать все подклассы Image.


# 2.8. Дочерние классы не используют часть контракта родителя
#
# ComputeDriver — очень широкий интерфейс VM-гипервизора. Bare metal драйвер Ironic тоже наследует
# его, хотя pause/unpause, live migration и большая часть консолей для bare metal не имеют смысла.

# Было

class ComputeDriver(object):
    def pause(self, instance):
        raise NotImplementedError()

    def unpause(self, instance):
        raise NotImplementedError()

    def live_migration(self, context, instance, destination,
                       *args, **kwargs):
        raise NotImplementedError()

    def get_vnc_console(self, context, instance):
        raise NotImplementedError()

    def get_serial_console(self, context, instance):
        raise NotImplementedError()


class IronicDriver(ComputeDriver):
    capabilities = {
        "has_imagecache": False,
        "supports_recreate": False,
        "supports_migrate_to_same_host": False,
        "supports_attach_interface": False,
    }

    # pause(), live_migration() и get_vnc_console() не определены.
    ...


# Стало

class ComputeDriver(object):
    """Только общие операции: spawn, destroy, power state, resource report."""
    ...


class DriverOperations(object):
    def __init__(self, pause=None, migration=None, console=None):
        self.pause = pause
        self.migration = migration
        self.console = console


class IronicDriver(ComputeDriver):
    def __init__(self, ironic_client):
        self.operations = DriverOperations(
            console=SerialConsoleOperations(ironic_client),
        )


class LibvirtDriver(ComputeDriver):
    def __init__(self, host):
        self.operations = DriverOperations(
            pause=LibvirtPauseOperations(host),
            migration=LibvirtMigrationOperations(host),
            console=LibvirtConsoleOperations(host),
        )


# 3. Уровень приложения


# 3.1. Одна модификация требует изменений в нескольких классах
#
# Каждый дочерний драйвер целиком заменяет
# словарь родителя. Поэтому добавление или переименование capability размазано по
# ComputeDriver, LibvirtDriver, HyperVDriver и т.д + по клиентам.

# Было

class ComputeDriver(object):
    capabilities = {
        "has_imagecache": False,
        "supports_recreate": False,
        "supports_attach_interface": False,
        "supports_device_tagging": False,
        "supports_extend_volume": False,
        "supports_bfv_rescue": False,
    }


class LibvirtDriver(ComputeDriver):
    capabilities = {
        "has_imagecache": True,
        "supports_recreate": True,
        "supports_attach_interface": True,
        "supports_device_tagging": True,
        "supports_extend_volume": True,
        "supports_bfv_rescue": True,
    }


class HyperVDriver(ComputeDriver):
    capabilities = {
        "has_imagecache": True,
        "supports_recreate": False,
        "supports_attach_interface": True,
        "supports_device_tagging": True,
    }


# Стало

class ComputeDriver(object):
    DEFAULT_CAPABILITIES = {
        "has_imagecache": False,
        "supports_recreate": False,
        "supports_attach_interface": False,
        "supports_device_tagging": False,
        "supports_extend_volume": False,
        "supports_bfv_rescue": False,
    }
    capability_overrides = {}

    def supports(self, capability):
        return self.capability_overrides.get(
            capability,
            self.DEFAULT_CAPABILITIES[capability],
        )


class LibvirtDriver(ComputeDriver):
    capability_overrides = {
        "has_imagecache": True,
        "supports_recreate": True,
        "supports_attach_interface": True,
        "supports_device_tagging": True,
        "supports_extend_volume": True,
        "supports_bfv_rescue": True,
    }


class HyperVDriver(ComputeDriver):
    capability_overrides = {
        "has_imagecache": True,
        "supports_attach_interface": True,
        "supports_device_tagging": True,
    }


if not driver.supports("supports_bfv_rescue"):
    raise UnsupportedOperation()


# Новый default теперь добавляется в одном месте, а дочерние классы описывают только отклонения.
# Ещё надёжнее заменить строковые ключи enum/value object, чтобы опечатка не превращалась в скрытый
# новый capability.


# 3.2. Сложный паттерн там, где достаточно простого дизайна
#
# Изначально отдельный NovaProxyRequestHandlerBase помогал поддерживать несовместимые
# API websockify 0.5 и 0.6. После удаления этого кода причина разделения
# исчезла: вся логика осталась в базовом классе, а наследник только добавляет
# зависимости. В итоге имеем две половины одного обработчика в разных местах.

# Было

class NovaProxyRequestHandlerBase(object):
    def verify_origin_proto(self, connect_info, origin_proto):
        ...

    def _get_connect_info(self, ctxt, token):
        ...

    def new_websocket_client(self):
        ...


class NovaProxyRequestHandler(NovaProxyRequestHandlerBase,
                              websockify.ProxyRequestHandler):
    def __init__(self, *args, **kwargs):
        self._compute_rpcapi = None
        websockify.ProxyRequestHandler.__init__(self, *args, **kwargs)

    @property
    def compute_rpcapi(self):
        if not self._compute_rpcapi:
            self._compute_rpcapi = compute_rpcapi.ComputeAPI()
        return self._compute_rpcapi

    def socket(self, *args, **kwargs):
        return websockifyserver.WebSockifyServer.socket(*args, **kwargs)


# Стало

class NovaProxyRequestHandler(websockify.ProxyRequestHandler):
    def __init__(self, *args, **kwargs):
        self._compute_rpcapi = None
        websockify.ProxyRequestHandler.__init__(self, *args, **kwargs)

    @property
    def compute_rpcapi(self):
        if not self._compute_rpcapi:
            self._compute_rpcapi = compute_rpcapi.ComputeAPI()
        return self._compute_rpcapi

    def verify_origin_proto(self, connect_info, origin_proto):
        ...

    def _get_connect_info(self, ctxt, token):
        ...

    def new_websocket_client(self):
        ...

    def socket(self, *args, **kwargs):
        return websockifyserver.WebSockifyServer.socket(*args, **kwargs)


# Исчез промежуточный класс без оставшейся обязанности.
# Тесты теперь проверяют тот же самый обработчик, а
# навигация между двумя частями одного класса больше не нужна.
# Это не то чтобы "паттерн", скорее недоработка, но ничего ближе к сути пункта я не нашел.
# Только сложные антипаттерны :)


# Рефлексия
#
# Данное занятие вызвало у меня большое количество размышлений. Несмотря на то, что часть пунктов
# - однозначное улучшение, в части демонстрируемые мной исправления имеют все же скорее синтетический характер.
# Как вещь в себе они, определенно, являются благом - улучшают читаемость, структуру и упрощают восприятие.
# Но в контексте всего проекта получается, что эти изменения обязаны тянуть за собой другие, те - еще одни, и
# подобные цепочки получаются достаточно длинными. И изменение подобных длинных цепочек с каждым следующим звеном
# увеличивают риски непредсказуемого поведения, что опасно для инфраструктуры такой степени критичности, как публичное
# облако.В целом, классическое легаси :)
# Разумеется, это можно решить, перепроектировать, распутать, и так далее, однако, эта задача другого масштаба
# (в сравнении с локальным улучшением чистоты кода). Вопрос в том, что делать, если нет большого количества времени.
# Можно и нужно попробовать локализовать изменения и проследить упоминаемые выше длинные цепочки,
# инкапсулировать компоненты и раздельно покрыть их тестами (на мой взгляд). Но, опять таки, это сильно выходит за
# проблему текущего задания, хоть и полезно (и интересно) само по себе.