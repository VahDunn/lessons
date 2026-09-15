from typing import Generic, Iterator, Optional, TypeVar, cast


T = TypeVar("T")


class HashTable(Generic[T]):
    """
    АТД хеш-таблицы, хранящей неупорядоченное множество значений.

    Публичный интерфейс АТД:
    - put(value), добавить новое значение
    - remove(value), удалить значение
    - clear(), удалить все значения
    - contains(value), проверить наличие значения
    - size(), получить количество значений
    - get_put_status(), получить статус последнего put()
    - get_remove_status(), получить статус последнего remove()

    Инварианты класса:
    - максимальный размер положителен и не меняется после создания таблицы
    - 0 <= size() <= максимальный размер
    - каждое значение хранится в таблице не более одного раза
    - contains(value) истинно тогда и только тогда, когда значение хранится
      в таблице

    Ограничения на значения:
    - значение должно быть хешируемым
    - результат hash(value) и сравнение значения с другими значениями не
      должны изменяться, пока значение находится в таблице

    Внутри используется открытая адресация с линейным пробированием. Индексы,
    слоты и признаки удалённых слотов не входят в публичный интерфейс АТД.
    """

    PUT_NIL = 0
    PUT_OK = 1
    PUT_ERR = 2

    REMOVE_NIL = 0
    REMOVE_OK = 1
    REMOVE_ERR = 2

    _EMPTY = object()
    _DELETED = object()
    _REBUILD_DELETED_RATIO = 4

    def __init__(self, max_size: int) -> None:
        # предусловие:
        # max_size — положительное целое число
        #
        # постусловие:
        # создана новая пустая хеш-таблица
        # максимальное количество значений равно max_size
        # size() == 0
        # статусы put() и remove() установлены в *_NIL

        if (
            not isinstance(max_size, int)
            or isinstance(max_size, bool)
            or max_size <= 0
        ):
            raise ValueError("max_size must be a positive integer")

        self._max_size = max_size
        self._slots: list[object] = [self._EMPTY] * max_size
        self._size = 0
        self._deleted_count = 0

        self._put_status = self.PUT_NIL
        self._remove_status = self.REMOVE_NIL

        return None

    # команды

    def put(self, value: T) -> None:
        # предусловие:
        # значение отсутствует в таблице
        # механизм разрешения коллизий может найти свободный слот
        #
        # постусловие при выполнении предусловия:
        # значение добавлено в таблицу
        # прежние значения не изменены
        # размер таблицы увеличен на 1
        # статус put установлен в PUT_OK
        #
        # если предусловие нарушено:
        # таблица не изменяется
        # статус put установлен в PUT_ERR

        if self._insert(value):
            self._put_status = self.PUT_OK
        else:
            self._put_status = self.PUT_ERR

        return None

    def remove(self, value: T) -> None:
        # предусловие:
        # значение содержится в таблице
        #
        # постусловие при выполнении предусловия:
        # значение удалено из таблицы
        # остальные значения не изменены
        # размер таблицы уменьшен на 1
        # статус remove установлен в REMOVE_OK
        #
        # если предусловие нарушено:
        # таблица не изменяется
        # статус remove установлен в REMOVE_ERR

        slot = self._find_value_slot(value)

        if slot is None:
            self._remove_status = self.REMOVE_ERR
        else:
            self._slots[slot] = self._DELETED
            self._size -= 1
            self._deleted_count += 1

            if (
                self._deleted_count * self._REBUILD_DELETED_RATIO
                >= self._max_size
            ):
                self._rebuild()

            self._remove_status = self.REMOVE_OK

        return None

    def clear(self) -> None:
        # предусловие:
        # отсутствует
        #
        # постусловие:
        # из таблицы удалены все значения
        # максимальный размер таблицы не изменился
        # size() == 0
        # статусы put() и remove() установлены в *_NIL

        self._slots = [self._EMPTY] * self._max_size
        self._size = 0
        self._deleted_count = 0

        self._put_status = self.PUT_NIL
        self._remove_status = self.REMOVE_NIL

        return None

    # запросы

    def contains(self, value: T) -> bool:
        # предусловие:
        # отсутствует
        #
        # результат:
        # возвращается True, если значение содержится в таблице, иначе False
        # состояние таблицы и статусы операций не изменяются

        result = self._find_value_slot(value) is not None

        return result

    def size(self) -> int:
        # предусловие:
        # отсутствует
        #
        # результат:
        # возвращено текущее количество значений в таблице
        # состояние таблицы не изменяется

        result = self._size

        return result

    # запросы статусов

    def get_put_status(self) -> int:
        # предусловие:
        # отсутствует
        #
        # результат:
        # возвращён статус последнего вызова put()
        # PUT_NIL, PUT_OK или PUT_ERR
        # состояние таблицы не изменяется

        result = self._put_status

        return result

    def get_remove_status(self) -> int:
        # предусловие:
        # отсутствует
        #
        # результат:
        # возвращён статус последнего вызова remove()
        # REMOVE_NIL, REMOVE_OK или REMOVE_ERR
        # состояние таблицы не изменяется

        result = self._remove_status

        return result

    # закрытые операции реализации

    def _insert(self, value: T) -> bool:
        # Добавляет отсутствующее значение, не меняя публичный статус put().
        # Возвращает False при повторном значении или отсутствии свободного
        # слота. Метод нужен наследникам для построения результатов запросов.

        slot = self._find_slot_for_put(value)

        if slot is None:
            return False

        if self._slots[slot] is self._DELETED:
            self._deleted_count -= 1

        self._slots[slot] = value
        self._size += 1

        return True

    def _find_value_slot(self, value: T) -> Optional[int]:
        # Возвращает слот со значением либо None. Маркер удалённого слота не
        # завершает поиск, потому что искомое значение могло попасть дальше по
        # той же цепочке коллизий.

        start = hash(value) % self._max_size
        offset = 0

        while offset < self._max_size:
            slot = (start + offset) % self._max_size
            current = self._slots[slot]

            if current is self._EMPTY:
                return None

            if (
                current is not self._DELETED
                and (current is value or current == value)
            ):
                return slot

            offset += 1

        return None

    def _find_slot_for_put(self, value: T) -> Optional[int]:
        # Возвращает слот для нового значения либо None, если значение уже
        # существует или вставка невозможна. Первый удалённый слот запоминается,
        # но поиск продолжается, потому что дальше может быть равное значение.

        start = hash(value) % self._max_size
        first_deleted: Optional[int] = None
        offset = 0

        while offset < self._max_size:
            slot = (start + offset) % self._max_size
            current = self._slots[slot]

            if current is self._EMPTY:
                if first_deleted is not None:
                    return first_deleted

                return slot

            if current is self._DELETED:
                if first_deleted is None:
                    first_deleted = slot
            elif current is value or current == value:
                return None

            offset += 1

        return first_deleted

    def _iter_values(self) -> Iterator[T]:
        # Даёт наследнику значения без раскрытия слотов в публичном интерфейсе.

        for value in self._slots:
            if value is self._EMPTY or value is self._DELETED:
                continue

            yield cast(T, value)

    def _rebuild(self) -> None:
        # Удаляет накопившиеся маркеры удалённых слотов, не меняя максимальный
        # размер, набор значений, логический размер и публичные статусы.

        values = list(self._iter_values())
        old_size = self._size

        self._slots = [self._EMPTY] * self._max_size
        self._size = 0
        self._deleted_count = 0

        for value in values:
            if not self._insert(value):
                raise RuntimeError("failed to rebuild hash table")

        if self._size != old_size:
            raise RuntimeError("hash table size changed during rebuild")

        return None


class PowerSet(HashTable[T]):
    """
    АТД ограниченного множества как расширение АТД HashTable.

    PowerSet(max_size) создаёт пустое множество, способное хранить не более
    max_size элементов. Все операции HashTable и их статусы наследуются без
    изменения контрактов.

    Дополнительные запросы АТД:
    - intersection(other), пересечение текущего множества и other
    - union(other), объединение текущего множества и other
    - difference(other), разность текущего множества и other
    - is_subset(other), входит ли other целиком в текущее множество
    - equals(other), равны ли множества

    Операции не изменяют исходные множества и возвращают новые множества.
    Максимальный размер результата intersection() равен меньшему из ограничений
    операндов, difference() — ограничению текущего множества, union() — сумме
    ограничений операндов. Статусы нового множества установлены в *_NIL.
    """

    def intersection(self, other: "PowerSet[T]") -> "PowerSet[T]":
        # предусловие:
        # other имеет совместимый тип PowerSet<T>
        #
        # результат:
        # возвращено новое множество из значений, которые входят одновременно
        # в текущее множество и в other
        # исходные множества и их статусы не изменяются

        result = PowerSet[T](min(self._max_size, other._max_size))

        if self.size() <= other.size():
            source = self
            target = other
        else:
            source = other
            target = self

        for value in source._iter_values():
            if target.contains(value) and not result._insert(value):
                raise RuntimeError("failed to build intersection")

        return result

    def union(self, other: "PowerSet[T]") -> "PowerSet[T]":
        # предусловие:
        # other имеет совместимый тип PowerSet<T>
        #
        # результат:
        # возвращено новое множество из всех значений текущего множества и other
        # каждое значение входит в результат ровно один раз
        # исходные множества и их статусы не изменяются

        result = PowerSet[T](self._max_size + other._max_size)

        for value in self._iter_values():
            if not result._insert(value):
                raise RuntimeError("failed to build union")

        for value in other._iter_values():
            if result.contains(value):
                continue

            if not result._insert(value):
                raise RuntimeError("failed to build union")

        return result

    def difference(self, other: "PowerSet[T]") -> "PowerSet[T]":
        # предусловие:
        # other имеет совместимый тип PowerSet<T>
        #
        # результат:
        # возвращено новое множество из значений текущего множества, которых
        # нет в other
        # исходные множества и их статусы не изменяются

        result = PowerSet[T](self._max_size)

        for value in self._iter_values():
            if not other.contains(value) and not result._insert(value):
                raise RuntimeError("failed to build difference")

        return result

    def is_subset(self, other: "PowerSet[T]") -> bool:
        # предусловие:
        # other имеет совместимый тип PowerSet<T>
        #
        # результат:
        # возвращается True, если каждый элемент other входит в текущее
        # множество, иначе False
        # исходные множества и их статусы не изменяются

        if other.size() > self.size():
            return False

        result = True

        for value in other._iter_values():
            if not self.contains(value):
                result = False
                break

        return result

    def equals(self, other: "PowerSet[T]") -> bool:
        # предусловие:
        # other имеет совместимый тип PowerSet<T>
        #
        # результат:
        # возвращается True, если множества содержат одинаковые элементы,
        # иначе False
        # исходные множества и их статусы не изменяются

        result = self.size() == other.size() and self.is_subset(other)

        return result
