@dataclass
class BaseComputeModel:
    """Базовый класс всех доменных моделей."""

    def __post_init__(self) -> None:
        """После создания считать, что объект не менялся."""
        self._changes: set[str] = set()

    def __setattr__(self, attr: str, value: Any) -> None:
        """Запомнить изменение атрибута."""
        if attr != '_changes':
            _changes = self.__dict__.setdefault('_changes', set())
            _changes.add(attr)
        super().__setattr__(attr, value)

    @classmethod
    def extract_attrs(
        cls,
        something: Any,
        ignore_missing: Collection[str] = (),
        **kwargs: Any,
    ) -> dict[str, Any]:
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

    @classmethod
    def from_object(cls, something: Any, **kwargs: Any) -> Self:
        """Создать экземпляр из произвольного объекта."""
        return cls(**cls.extract_attrs(something, **kwargs))

    def obj_what_changed(self) -> frozenset[str]:
        """Вернуть набор изменённых полей."""
        return frozenset(self._changes)

    def obj_reset_changes(self, fields: Collection[str] | None = None) -> None:
        """Сбросить накопленные изменения."""
        if fields is None:
            self._changes.clear()
        else:
            self._changes = self._changes - set(fields)

    def obj_get_changes(
        self,
        ignore: Collection[str] = (),
    ) -> dict[str, Any]:
        """Вернуть все изменившиеся атрибуты."""
        return {
            key: getattr(self, key)
            for key in self._changes
            if key not in ignore
        }



class BaseUseCase:
    """Базовый класс всех сценариев использования."""

    def __init__(
        self,
        context: infra.Context,
        policy: AbsPolicy,
        database: AbsDatabase,
    ) -> None:
        """Инициализировать экземпляр."""
        self.context = context
        self.policy = policy
        self.database = database




class BaseAvailabilityZonesUseCase(BaseUseCase):
    """Базовый класс сценария использования для зон доступности."""

    def __init__(
        self,
        context: infra.Context,
        policy: AbsPolicy,
        database: db_interfaces.AbsDatabase,
        services: db_interfaces.AbsServicesRepo,
        aggregates: db_interfaces.AbsAggregatesRepo,
        az_cache: cache_interfaces.AbsCache,
    ) -> None:
        """Инициализировать экземпляр."""
        super().__init__(context, policy, database)
        self.services = services
        self.aggregates = aggregates
        self.cache = az_cache

    @staticmethod
    def _build_zones(
        hosts: dict[str, bool],
        zones_by_host: dict[str, set[str]],
    ) -> dict[str, set[str]]:
        """Собрать маппинг хостов в зоны доступности.

        Compute-хосты получают AZ из агрегатов
        (или default_availability_zone).
        Non-compute хосты получают internal_service_availability_zone.
        """
        zones: dict[str, set[str]] = {}
        for host, has_compute in hosts.items():
            if has_compute:
                azs = zones_by_host.get(host)
                if not azs:
                    azs = {config.az.default_availability_zone}
                zones[host] = azs
            else:
                zones[host] = {config.az.internal_service_availability_zone}
        return zones

    async def _get_zones(
        self,
    ) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
        """Получить enabled_zones, disabled_zones."""
        async with self.database.cell_transaction() as conn:
            host_infos = await self.services.get_hosts_info(conn)

        enabled_hosts: dict[str, bool] = {}
        disabled_hosts: dict[str, bool] = {}
        compute_hosts: list[str] = []

        for host, disabled, has_compute in host_infos:
            if has_compute:
                compute_hosts.append(host)
            if disabled:
                disabled_hosts[host] = has_compute
            else:
                enabled_hosts[host] = has_compute

        zones_by_host: dict[str, set[str]] = {}
        async with self.database.transaction() as conn:
            zones_by_host = await self.aggregates.get_metadata_by_key_per_host(
                conn,
                'availability_zone',
                hosts=compute_hosts,
            )

        enabled_zones = self._build_zones(enabled_hosts, zones_by_host)
        disabled_zones = self._build_zones(disabled_hosts, zones_by_host)

        return enabled_zones, disabled_zones


class GetAllAvailabilityZoneUseCase(BaseAvailabilityZonesUseCase):
    """Получить данные о всех зонах доступности."""

    def _filter_availability_zones(
        self, zones: list[str], is_available: bool
    ) -> list[dict[str, Any]]:
        """Отфильтровать зоны."""
        result = []
        for zone in zones:
            if zone == config.az.internal_service_availability_zone:
                continue
            result.append(
                {
                    'zoneName': zone,
                    'zoneState': {'available': is_available},
                    'hosts': None,
                }
            )
        return result

    async def execute(self) -> list[dict]:
        """Исполнение."""
        await self.policy.can('os-availability-zone:list', self.context)

        enabled_zones, disabled_zones = await super()._get_zones()

        available_zone_names = sorted(
            {az for azs in enabled_zones.values() for az in azs}
        )
        disabled_zone_names = sorted(
            {az for azs in disabled_zones.values() for az in azs}
            - set(available_zone_names)
        )

        filtered_available = self._filter_availability_zones(
            available_zone_names, is_available=True
        )
        filtered_disabled = self._filter_availability_zones(
            disabled_zone_names, is_available=False
        )

        return filtered_available + filtered_disabled


class GetAllAvailabilityZoneVerboseUseCase(BaseAvailabilityZonesUseCase):
    """Получить данные о всех зонах доступности с информацией о хостах."""

    @staticmethod
    def _build_host_state(
        service: service_models.Service,
    ) -> dict[str, Any]:
        """Собрать состояние сервиса на хосте.

        `available` — сервис работоспособен (аналог service_is_up);
        `active` — сервис не находится в состоянии disabled.
        """
        return {
            'available': service.is_alive(),
            'active': not service.disabled,
            'updated_at': (
                service.updated_at.isoformat() if service.updated_at else None
            ),
        }

    async def execute(self) -> list[dict]:
        """Исполнение."""
        await self.policy.can('os-availability-zone:detail', self.context)

        enabled_zones, disabled_zones = await super()._get_zones()

        async with self.database.cell_transaction() as conn:
            services = await self.services.get_all(conn, None, None)

        services_by_host: dict[str, list[service_models.Service]] = {}
        for service in services:
            if service.host is None:
                continue
            services_by_host.setdefault(service.host, []).append(service)

        zone_hosts: dict[str, set[str]] = {}
        for host, azs in enabled_zones.items():
            for az in azs:
                zone_hosts.setdefault(az, set()).add(host)

        result: list[dict] = []
        available_zone_names = sorted(zone_hosts.keys())

        for zone in available_zone_names:
            hosts = {
                host: {
                    svc.binary: self._build_host_state(svc)
                    for svc in services_by_host.get(host, [])
                    if svc.binary and svc.binary not in const.API_SERVICES
                }
                for host in sorted(zone_hosts.get(zone, set()))
            }
            result.append(
                {
                    'zoneName': zone,
                    'zoneState': {'available': True},
                    'hosts': hosts,
                }
            )

        disabled_zone_names = sorted(
            {az for azs in disabled_zones.values() for az in azs}
            - set(available_zone_names)
        )
        for zone in disabled_zone_names:
            result.append(
                {
                    'zoneName': zone,
                    'zoneState': {'available': False},
                    'hosts': None,
                }
            )
        return result


class Context(context.PolicyContext):
    """Класс для передачи данных между этажами стека вызова."""

    def __init__(
        self,
        request: Request,
        credentials: CredentialsData,
        *,
        is_admin: bool,
        request_id: str | None,
        timestamp: datetime | None = None,
    ) -> None:
        """Инициализировать экземпляр."""
        super().__init__(
            request, credentials, is_admin=is_admin, request_id=request_id
        )

        if timestamp is None:
            timestamp = utils.now()
        self.timestamp = timestamp


# Рефлексия
# В целом, выглядит несложно (если, конечно, я правильно понял и выполнил задание) -
# по сути, мы описываем "детальки лего", облегчая понимание того, как и зачем ими пользоваться,
# без вникания в суть их внутренней структуры.
# Действительно, чтобы прочитать инструкцию к конструктору и собрать из него что-то,
# мне не требуется знать, как именно сделана деталь длиной 6 и шириной 2,
# мне требуется знать, как именно она выглядит, где лежит и как правильно ее прикрепить к остальным.
# В данном случае, "автономный кусок кода" - это гораздо более сложная по форме и
# специфичная по назначению деталь, чем описываемая мной выше, и, как следствие, о ней
# нужно чуть больше высокоуровневой информации. И если для понимания того, как ей пользоваться,
# можно почитать сигнатуры методов (и это, конечно, говорит о том, что их тоже надо писать
# качественно), то для понимания того, зачем она нужна и/или какую роль играет во всем проекте,
# крайне желательно иметь комментарий (или докстрингу). На мой взгляд, распространенный сейчас
# подход к докстрингам с явным указанием ввода и вывода и пр. зачастую является избыточным -
# достаточно выразительно написанная и типизированная функция (в первую очередь, шапка)
# в 90% случаев уже отвечает на вопрос, что въодит и выходит :) (хотя исключений не может не быть).
# А вот то, зачем это все происходит и как на это смотреть на высоком уровне - здесь
# комментарии отлично помогают.
