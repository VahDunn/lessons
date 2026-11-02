# 1. Настройки устройств - вместо стабильного куска конфигурации передаются мутабельные image и сама ВМ.
#
# Было

class GuestProperties:
    def __init__(self, instance, image_meta):
        self.instance = instance
        self.image_meta = image_meta

    def get_disk_bus(self):
        return (
            self.instance.system_metadata.get("image_hw_disk_bus")
            or self.image_meta.properties.get("hw_disk_bus")
            or "virtio"
        )

    def get_vif_model(self, mac):
        return (
            self.instance.system_metadata.get(f"image_hw_vif_model_{mac}")
            or self.instance.system_metadata.get("image_hw_vif_model")
            or self.image_meta.properties.get("hw_vif_model")
            or "virtio"
        )


def disk_target_before(properties):
    return Element("target", bus=properties.get_disk_bus())


def network_model_before(properties, mac):
    return Element("model", type=properties.get_vif_model(mac))


# properties выглядит как готовая конфигурация, но сохраняет ссылки на два
# изменяемых объекта. Каждый потребитель заново выясняет приоритет настроек.
# Если между подготовкой диска и сети поменять метаданные, этапы одной операции
# могут получить настройки из разных состояний исходных объектов.

# Стало

@dataclass(frozen=True)
class NetworkDevice:
    mac: str
    model: str


@dataclass(frozen=True)
class GuestHardware:
    disk_bus: str
    networks: tuple[NetworkDevice, ...]


def resolve_guest_hardware(instance, image_meta, macs) -> GuestHardware:
    properties = GuestProperties(instance, image_meta)
    return GuestHardware(
        disk_bus=properties.get_disk_bus(),
        networks=tuple(
            NetworkDevice(mac, properties.get_vif_model(mac)) for mac in macs
        ),
    )


def disk_target(hardware: GuestHardware) -> Element:
    return Element("target", bus=hardware.disk_bus)


def network_model(device: NetworkDevice) -> Element:
    return Element("model", type=device.model)


# Вызывающий код один раз получает resolve_guest_hardware()
# и передаёт его дальше по этапам подготовки устройств.
# Билдер XML не знает про instance, image_meta и порядок приоритетов.
# Вместо двух сущностей с произвольными метаданными теперь он
# получает фиксированные значения.

# 2. Хост, на котором уже была неудачная попытка (а это маркирует его как невалидный), может выбираться повторно.

# Было

def host_passes(self, host_state, spec_obj):
    retry = spec_obj.retry
    if not retry:
        return True

    host = [host_state.host, host_state.nodename]
    hosts = [[cn.host, cn.hypervisor_hostname] for cn in retry.hosts]
    return host not in hosts


# Для каждого кандидата фильтр заново обходит объекты прошлых попыток.
# Его ответ зависит от текущего содержимого retry.hosts и полей этих объектов.

# Стало

def excluded_hosts(retry) -> frozenset[tuple[str, str]]:
    if not retry:
        return frozenset()
    return frozenset((cn.host, cn.hypervisor_hostname) for cn in retry.hosts)


def host_passes(self, host: str, node: str, excluded: frozenset[tuple[str, str]]):
    return (host, node) not in excluded


# Перед обходом кандидатов один раз вычисляем excluded_hosts(spec_obj.retry).
# Фильтру больше не нужны спеки, стейт и объекты прошлых попыток:
# он получает только имя кандидата и фиксированное множество исключений.
# Изменение исходных объектов не меняет правила посреди обхода.


# 3. Отправка RPC - сообщение может меняться, пока ждёт соединения.

# Было

async def _call_once(self, context, config, method, kwargs, deadline):
    message_id = uuid.uuid4().hex
    reply_name = f"reply_{message_id}"
    async with self._connection_pool.acquire() as connection:
        channel = aio_pika.Channel(connection, on_return_raises=True)
    ...

    message = common_rpc.make_rpc_call(
        context, method, config.version, kwargs, message_id, reply_name
    )
    await queue.consume(receive, no_ack=True)
    await exchange.publish(
        aio_pika.Message(
            body=common_rpc.encode_rpc_message(message, self.oslo_version),
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        ),
        routing_key=self._routing_key(config),
    )
    ...  # Ожидание ответа с message_id и освобождение ресурсов.


# Пока функция ждёт соединения, другой код может изменить config.server
# или вложенные значения kwargs. Тогда вызов уйдёт другому получателю
# или с другими аргументами. Отправитель полагается на то, что владельцы
# объектов не меняют их до завершения отправки.

# Стало

@dataclass(frozen=True)
class PreparedCall:
    message_id: str
    reply_name: str
    routing_key: str
    body: bytes
    timeout: float


def _prepare_call(self, context, config, method, kwargs) -> PreparedCall:
    message_id = uuid.uuid4().hex
    reply_name = f"reply_{message_id}"
    message = common_rpc.make_rpc_call(
        context, method, config.version, kwargs, message_id, reply_name
    )
    return PreparedCall(
        message_id=message_id,
        reply_name=reply_name,
        routing_key=self._routing_key(config),
        body=common_rpc.encode_rpc_message(message, self.oslo_version),
        timeout=config.timeout,
    )


async def _call_with_timeout(self, prepared: PreparedCall):
    async with (
        asyncio.timeout(prepared.timeout) as deadline,
        self._call_slots,
    ):
        return await self._call_once(prepared, deadline)


async def _call_once(self, prepared: PreparedCall, deadline):
    message_id = prepared.message_id
    reply_name = prepared.reply_name
    async with self._connection_pool.acquire() as connection:
        channel = aio_pika.Channel(connection, on_return_raises=True)
    ...  # Та же настройка channel, reply_name и exchange.

    await queue.consume(receive, no_ack=True)
    await exchange.publish(
        aio_pika.Message(
            body=prepared.body,
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        ),
        routing_key=prepared.routing_key,
    )
    ...  # Ожидание ответа с message_id и освобождение ресурсов.


# Дальше передаётся готовое сообщение - байты, адрес и параметры ожидания.
# Изменение вложенного списка в kwargs уже не повлияет на отправку.
# Транспорт не разбирает доменные объекты и контекст, а только отправляет
# сообщение и получает ответ.

# Рефлексия.
# Почему-то подумал, что предыдущее задание по теме - единственное :)
# Рад, что это оказалось не так.
# Сама по себе тема мутабельности/иммутабельности мне представляется достаточно сложной, хоть и с
# относительно простой "базовой настройкой" - избегать мутабельности там, где возможно.
# Вероятно, немного занесло в абстрактные рассуждения и экстраполяцию мутабельности на пола в БД, но
# это мне еще предстоит обдумать. Стоит также сказать о том, что в текущем виде наш "основной" проект на работе,
# из которого я и дергаю куски кода в большинстве случаев, генерирует приличную часть багов как раз из-за
# любви к изменению доменных объектов на ходу. В итоге получаем кучу гонок, которые наблюдаются даже в тестах, флоп
# тех же самых тестов и пайплайнов и прочее, прочее.
# По мере сил в своих МР стараюсь от этой самой мутабельности уходить, но получается не всегда, в первую очередь
# из-за ограничений по времени и объему изменений. Но потихоньку двигаемся.