# 7 неочевидных проектных ошибок.

# 1. Сортировка флейворов: произвольные строки доходят до сборщика SQL


# Было

def _apply_sorting(query, sort_keys, sort_dir):
    for sort_key in sort_keys:
        sort_col = ALLOWED_SORT_KEYS.get(sort_key)
        if not sort_col:
            raise ValueError(f'Invalid sort field: {sort_key}')

        if sort_dir == 'desc':
            query = query.order_by(sa.desc(sort_col))
        elif sort_dir == 'asc':
            query = query.order_by(sa.asc(sort_col))
        else:
            raise ValueError(f'Invalid sort direction: {sort_dir}')

    return query


# Стало

from dataclasses import dataclass
import enum


class FlavorSortKey(enum.Enum):
    # id тоже оставлен: исходный ALLOWED_SORT_KEYS его допускает,
    # хотя отдельного значения id в перечислении HTTP-модели нет.
    ID = 'id'
    FLAVOR_ID = 'flavorid'
    NAME = 'name'
    MEMORY = 'memory_mb'
    VCPUS = 'vcpus'
    DISK = 'root_gb'


class SortDirection(enum.Enum):
    ASC = 'asc'
    DESC = 'desc'


@dataclass(frozen=True, init=False)
class FlavorOrder:
    key: FlavorSortKey
    direction: SortDirection

    def __init__(
        self,
        key: FlavorSortKey | str,
        direction: SortDirection | str,
    ):
        # Конструктор действительно проверяет значения в runtime.
        # После создания поля содержат Enum и не изменяются обычным присваиванием.
        try:
            parsed_key = FlavorSortKey(key)
        except ValueError:
            raise ValueError(f'Invalid sort field: {key}') from None
        try:
            parsed_direction = SortDirection(direction)
        except ValueError:
            raise ValueError(
                f'Invalid sort direction: {direction}'
            ) from None
        object.__setattr__(self, 'key', parsed_key)
        object.__setattr__(self, 'direction', parsed_direction)


# Этот адаптер вызывается обоими HTTP-контроллерами до вызова use case.
# Сохраняются прежние значения по умолчанию и доменное исключение для HTTP 400.
def order_from_query(query):
    try:
        return FlavorOrder(
            query.sort_key or 'flavorid',
            query.sort_dir or 'asc',
        )
    except ValueError as exc:
        raise exceptions.IncorrectInputError(message=str(exc)) from exc


# Репозиторий использует доменные перечисления, а не строки от клиента.
# Соответствие колонкам остаётся внутренней деталью слоя хранения.
SORT_COLUMNS = {
    FlavorSortKey.ID: api_db_models.Flavor.id,
    FlavorSortKey.FLAVOR_ID: api_db_models.Flavor.flavorid,
    FlavorSortKey.NAME: api_db_models.Flavor.name,
    FlavorSortKey.MEMORY: api_db_models.Flavor.memory_mb,
    FlavorSortKey.VCPUS: api_db_models.Flavor.vcpus,
    FlavorSortKey.DISK: api_db_models.Flavor.root_gb,
}
SORT_FUNCTIONS = {
    SortDirection.ASC: sa.asc,
    SortDirection.DESC: sa.desc,
}


def _apply_sorting(query, order: FlavorOrder):
    sort = SORT_FUNCTIONS[order.direction]
    # Вторичная сортировка по id была и в исходном коде.
    for key in (order.key, FlavorSortKey.ID):
        query = query.order_by(sort(SORT_COLUMNS[key]))
    return query



# 2. Лимит выдачи: нормализация повторяется в двух сценариях
#
# Use case получает int | None. В обоих вариантах листинга приходится помнить,
# что None и отрицательное число означают MAX_RESULTS, а большое надо обрезать.
# Репозиторий дополнительно проверяет None. При новом способе вызова легко
# забыть одну из этих договорённостей и получить запрос без нужного ограничения.


# Было — одинаковый фрагмент в ListFlavorsUseCase и ListFlavorsDetailUseCase

if limit is None or limit < 0:
    limit = const.MAX_RESULTS
limit = min(limit, const.MAX_RESULTS)

# А затем в _get_flavors_query_listing:
if limit is not None:
    query = query.limit(limit)


# Стало

@dataclass(frozen=True, init=False)
class FlavorPageSize:
    value: int

    def __init__(self, requested: int | None = None):
        if requested is not None and type(requested) is not int:
            raise TypeError('Page size must be an integer or None')
        if requested is None or requested < 0:
            value = const.MAX_RESULTS
        else:
            value = min(requested, const.MAX_RESULTS)
        object.__setattr__(self, 'value', value)


# После существующей HTTP-валидации ge=0 оба контроллера создают:
page_size = FlavorPageSize(query.limit)

# Внутренние методы листинга получают page_size: FlavorPageSize
# и передают тот же объект в AbsFlavorsRepo. В них больше нет нормализации.
# Финальная строка построения SQL теперь без проверки None:
query = query.limit(page_size.value)



# 3. Создание флейвора: assert обязательного ID выполняется после INSERT
#

# Было — подготовка в use case

if raw_flavor.id is None:
    raw_flavor.id = str(uuid.uuid4())

# И фрагмент репозитория после conn.execute(stmt):
assert raw_flavor.id is not None


# Стало

from dataclasses import asdict
import uuid


@dataclass(frozen=True)
class FlavorToCreate:
    id: str
    name: str
    memory_mb: int
    vcpus: int
    root_gb: int
    swap: int
    is_public: bool
    rxtx_factor: float | None = 1.0
    ephemeral_gb: int | None = 0

    def __post_init__(self):
        if not isinstance(self.id, str):
            raise TypeError('FlavorToCreate requires a string id')


def prepare_flavor(raw_flavor) -> FlavorToCreate:
    # Копируем значения вместо сохранения ссылки на изменяемый RawFlavor.
    # Пользовательский строковый id сохраняется тк он не обязан быть UUID.
    return FlavorToCreate(
        id=(raw_flavor.id if raw_flavor.id is not None else str(uuid.uuid4())),
        name=raw_flavor.name,
        memory_mb=raw_flavor.memory_mb,
        vcpus=raw_flavor.vcpus,
        root_gb=raw_flavor.root_gb,
        swap=raw_flavor.swap,
        is_public=raw_flavor.is_public,
        rxtx_factor=raw_flavor.rxtx_factor,
        ephemeral_gb=raw_flavor.ephemeral_gb,
    )


# В CreateFlavorUseCase.execute после проверки:
# flavor = prepare_flavor(raw_flavor)
# Далее final_exc, final_message и вызов create используют flavor.
# Подготовка выполняется один раз перед try_transaction, чтобы при повторах
# операции не менялся сгенерированный идентификатор.


# Такой же тип аргумента задаётся в AbsFlavorsRepo.create.
async def create(self, conn, flavor: FlavorToCreate):
    values = asdict(flavor)
    values['flavorid'] = values.pop('id')
    values.update(disabled=False, vcpu_weight=1)
    stmt = sa.insert(api_db_models.Flavor).values(**values)
    response = await conn.execute(stmt)

    if response is None:
        raise RuntimeError('Failed to save flavor')

    return models.Flavor(id=int(response.lastrowid), **values)



# 4. Режимы cache и I/O: сериализатор исправляет противоречивые настройки
#
# driver_cache и driver_io записываются независимо. Можно собрать диск
# с cache='writeback' и io='native'. Перед передачей libvirt сериализатор
# страхуется и незаметно заменяет io на threads. Значения объекта и XML расходятся.


# Было — часть _format_driver

if self.driver_io is not None:
    drv.set('io', self.driver_io)
if self.driver_cache not in NATIVE_MODES and self.driver_cache is not None:
    drv.set('io', 'threads')


# Стало — объект описывает правило выбора I/O, а не два независимых результата.
# Этот и следующий пример используют синтаксис, совместимый с Python 2.7 (на котором все и написано).

from collections import namedtuple


class DiskIOPolicy(namedtuple('_DiskIOPolicy', 'cache requested_io')):
    __slots__ = ()

    @property
    def io(self):
        # Сохраняем правило исходного кода: при cache=None
        # оставляем выбор backend, а не приравниваем None к строке 'none'.
        if self.cache is not None and self.cache not in ('none', 'directsync'):
            return 'threads'
        return self.requested_io


# Фрагмент LibvirtConfigGuestDisk. Остальные поля и XML-атрибуты не показаны.
class LibvirtConfigGuestDisk(LibvirtConfigGuestDevice):
    def __init__(self, **kwargs):
        super(LibvirtConfigGuestDisk, self).__init__(root_name='disk', **kwargs)
        self._io_policy = DiskIOPolicy(cache=None, requested_io=None)

    @property
    def driver_cache(self):
        return self._io_policy.cache

    @driver_cache.setter
    def driver_cache(self, value):
        self._io_policy = self._io_policy._replace(cache=value)

    @property
    def driver_io(self):
        return self._io_policy.io

    @driver_io.setter
    def driver_io(self, value):
        self._io_policy = self._io_policy._replace(requested_io=value)

    def _format_driver(self, dev):
        drv = self._new_node('driver')
        # Здесь остаётся вывод остальных атрибутов driver.
        if self.driver_cache is not None:
            drv.set('cache', self.driver_cache)
        if self.driver_io is not None:
            drv.set('io', self.driver_io)
        dev.append(drv)



# 5. detect_zeroes: одна и та же строка проверяется при чтении и записи XML
#
# В объект можно записать произвольную строку. Поэтому три разных места
# вспоминают допустимые значения on/off/unmap. Ошибка не меняет состояние
# объекта сразу, а проявляется как молча пропущенный атрибут при сериализации.


# Было — фрагменты _format_driver и parse_dom

if self.driver_detect_zeroes is not None and (
    self.driver_detect_zeroes in ['off', 'on', 'unmap']
):
    drv.set('detect_zeroes', self.driver_detect_zeroes)

self.driver_detect_zeroes = c.get('detect_zeroes')
if self.driver_detect_zeroes not in ['on', 'off', 'unmap']:
    self.driver_detect_zeroes = None


# Стало

class DetectZeroesMode(enum.Enum):
    UNSPECIFIED = None
    OFF = 'off'
    ON = 'on'
    UNMAP = 'unmap'

    @classmethod
    def from_legacy(cls, value):
        try:
            return cls(value)
        except ValueError:
            # Сохраняем прежнее поведение: неизвестная строка означает
            # отсутствие настройки, а не новый отказ при чтении старого XML.
            return cls.UNSPECIFIED


# Отдельный фрагмент того же класса; в реальной интеграции совмещается с п. 4.
class LibvirtConfigGuestDisk(LibvirtConfigGuestDevice):
    def __init__(self, **kwargs):
        super(LibvirtConfigGuestDisk, self).__init__(root_name='disk', **kwargs)
        self._driver_detect_zeroes = DetectZeroesMode.UNSPECIFIED

    @property
    def driver_detect_zeroes(self):
        # Для существующих читателей сохраняется интерфейс str | None.
        return self._driver_detect_zeroes.value

    @driver_detect_zeroes.setter
    def driver_detect_zeroes(self, value):
        # Любая запись через публичный интерфейс проходит одну границу.
        self._driver_detect_zeroes = DetectZeroesMode.from_legacy(value)

    def _format_driver(self, dev):
        drv = self._new_node('driver')
        # Вывод остальных атрибутов driver сохранён.
        if self.driver_detect_zeroes is not None:
            drv.set('detect_zeroes', self.driver_detect_zeroes)
        dev.append(drv)


# В parse_dom остаётся только присваивание через свойство:
self.driver_detect_zeroes = c.get('detect_zeroes')

# В условии создания driver в format_dom вместо проверки в списке:
# self.driver_detect_zeroes in ['on', 'off', 'unmap']
# используется:
# self.driver_detect_zeroes is not None
# Остальные условия создания driver остаются прежними.



# Рефлексия
# Во всех пяти случаях гарантия действует при работе через описанный интерфейс.
# Это не формальное доказательство
# корректности всей программы, но обычные способы работы больше не создают
# рассматриваемые ошибочные состояния. И проверяются именно эти свойства:
# допустимая сортировка, границы страницы, ID до SQL и итоговые XML-настройки,
# а не количество вызовов вспомогательных методов.
# На самом деле, это, конечно, не оптимум - то есть, все же система под капотом
# делает проверки правил и прочие подобные вещи. Однако, эти првоерки сфокусированы
# в одном конкретном месте, тогда как раньше они были размазаны по коду. И, таким
# образом, мы получаем в более глубоких слоях логики объекты взаимодействия,
# по поводу которых можем не тыкать везде проверки и уповать на то, что не забыли
# их написать где-то там в конкретном месте. Немного печалит, что я примерно такое
# уже предлагал, но мне сказали, что надо писать проще (хотя это вообще-то сложнее).
# Впрочем, многие предложения архитектурных изменений (которые проводятся относительно быстро
# в апи-слое, например) встречают вот такое вот нежелание "усложнять".
