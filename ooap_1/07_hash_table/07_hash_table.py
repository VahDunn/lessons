from typing import Generic, Optional, TypeVar


T = TypeVar("T")


class HashTable(Generic[T]):
    """
    АТД хэш-таблицы, хранящей неупорядоченное множество значений.

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
    - contains(value) истинно тогда и только тогда, когда value хранится в
      таблице

    Ограничения на значения:
    - значение должно быть хэшируемым
    - результат hash(value) и сравнение value с другими значениями не должны
      изменяться, пока значение находится в таблице

    Гарантии эффективности:
    - put() и contains() работают за O(1) в среднем при равномерном
      распределении хэшей и наличии свободных слотов
    - remove() работает за амортизированное O(1) в среднем: иногда оно
      запускает перестройку таблицы того же размера
    - одно пробирование в худшем случае работает за O(N), где N —
      максимальный размер таблицы
    - перестройка работает за O(N) в среднем и за O(N^2) в худшем случае,
      если все хэши коллидируют
    - size() работает за O(1), clear() — за O(N)

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
        # создана новая пустая хэш-таблица
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
        # value отсутствует в таблице
        # механизм разрешения коллизий может найти свободный слот
        #
        # постусловие при выполнении предусловия:
        # value добавлено в таблицу
        # прежние значения не изменены
        # размер таблицы увеличен на 1
        # статус put установлен в PUT_OK
        #
        # если предусловие нарушено:
        # таблица не изменяется
        # статус put установлен в PUT_ERR

        slot = self._find_slot_for_put(value)

        if slot is None:
            self._put_status = self.PUT_ERR
        else:
            if self._slots[slot] is self._DELETED:
                self._deleted_count -= 1

            self._slots[slot] = value
            self._size += 1
            self._put_status = self.PUT_OK

        return None

    def remove(self, value: T) -> None:
        # предусловие:
        # value содержится в таблице
        #
        # постусловие при выполнении предусловия:
        # value удалено из таблицы
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
            # Обычный пустой слот остановил бы поиск значений, которые попали
            # дальше из-за коллизии. Поэтому удалённый слот помечается отдельно.
            self._slots[slot] = self._DELETED
            self._size -= 1
            self._deleted_count += 1

            # Удалённые маркеры удлиняют пробирование. После накопления
            # четверти буфера таблица перестраивается в том же размере. Такая
            # перестройка не является динамическим расширением, а её стоимость
            # распределяется по предшествующей серии удалений.
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
        # возвращается True, если value содержится в таблице, иначе False
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

    def _find_value_slot(self, value: T) -> Optional[int]:
        # Возвращает слот с value либо None. Маркер удалённого слота не
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
        # Возвращает слот для нового value либо None, если value уже существует
        # или вставка невозможна. Первый удалённый слот запоминается, но поиск
        # продолжается: дальше в цепочке может находиться равное значение.

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

    def _rebuild(self) -> None:
        # Удаляет накопившиеся маркеры удалённых слотов, не меняя максимальный
        # размер, набор значений, логический размер и публичные статусы.

        old_slots = self._slots
        self._slots = [self._EMPTY] * self._max_size
        self._deleted_count = 0

        for value in old_slots:
            if value is self._EMPTY or value is self._DELETED:
                continue

            slot = self._find_slot_for_put(value)

            if slot is None:
                raise RuntimeError("failed to rebuild hash table")

            self._slots[slot] = value

        return None
