from typing import Generic, Optional, TypeVar


T = TypeVar("T")


class DynArray(Generic[T]):
    """
    АТД динамического массива.

    Пользователь работает только через индексы.
    Текущая ёмкость, свободные ячейки и перераспределение памяти являются
    скрытыми деталями реализации.

    Инварианты класса:
    - 0 <= size() <= текущая ёмкость
    - текущая ёмкость не меньше начальной ёмкости
    - значения занимают индексы от 0 до size() - 1 без промежутков
    - изменение ёмкости не меняет порядок и значения элементов

    Гарантии эффективности:
    - get(), replace() и size() работают за O(1)
    - append() работает за амортизированное O(1)
    - insert() и remove() работают за O(N)
    """

    GET_NIL = 0
    GET_OK = 1
    GET_ERR = 2

    INSERT_NIL = 0
    INSERT_OK = 1
    INSERT_ERR = 2

    REMOVE_NIL = 0
    REMOVE_OK = 1
    REMOVE_ERR = 2

    REPLACE_NIL = 0
    REPLACE_OK = 1
    REPLACE_ERR = 2

    _MIN_CAPACITY = 16
    _GROWTH_FACTOR = 2
    _SHRINK_FACTOR = 1.5

    def __init__(self) -> None:
        # предусловие:
        # отсутствует
        #
        # постусловие:
        # создан новый пустой динамический массив
        # size() == 0
        # внутренняя ёмкость равна начальной ёмкости
        # статусы всех операций установлены в *_NIL

        self._size = 0
        self._capacity = self._MIN_CAPACITY
        self._storage: list[Optional[T]] = [None] * self._capacity

        self._get_status = self.GET_NIL
        self._insert_status = self.INSERT_NIL
        self._remove_status = self.REMOVE_NIL
        self._replace_status = self.REPLACE_NIL

        return None

    # команды

    def append(self, value: T) -> None:
        # предусловие:
        # отсутствует
        #
        # постусловие:
        # value добавлено в конец массива
        # прежние элементы и их порядок не изменены
        # размер массива увеличен на 1

        if self._size == self._capacity:
            self._resize(self._capacity * self._GROWTH_FACTOR)

        self._storage[self._size] = value
        self._size += 1

        return None

    def insert(self, index: int, value: T) -> None:
        # предусловие:
        # индекс, по которому ставим, 0+ и <= размеру (если по размеру, то вставляем в конец)
        #
        # постусловие при выполнении предусловия:
        # value добавлено по индексу index
        # элементы, ранее находившиеся на позициях от index до size() - 1,
        # сдвинуты на одну позицию вправо без изменения порядка
        # размер массива увеличен на 1
        # статус insert установлен в INSERT_OK
        #
        # если предусловие нарушено:
        # массив не изменяется
        # статус insert установлен в INSERT_ERR

        if 0 <= index <= self._size:
            if self._size == self._capacity:
                self._resize(self._capacity * self._GROWTH_FACTOR)

            current_index = self._size

            while current_index > index:
                self._storage[current_index] = self._storage[current_index - 1]
                current_index -= 1

            self._storage[index] = value
            self._size += 1
            self._insert_status = self.INSERT_OK
        else:
            self._insert_status = self.INSERT_ERR

        return None

    def remove(self, index: int) -> None:
        # предусловие:
        # 0 <= index < size()
        #
        # постусловие при выполнении предусловия:
        # элемент по индексу index удалён
        # элементы справа от него сдвинуты на одну позицию влево
        # порядок оставшихся элементов не изменён
        # размер массива уменьшен на 1
        # статус remove установлен в REMOVE_OK
        #
        # если предусловие нарушено:
        # массив не изменяется
        # статус remove установлен в REMOVE_ERR

        if 0 <= index < self._size:
            current_index = index

            while current_index < self._size - 1:
                self._storage[current_index] = self._storage[current_index + 1]
                current_index += 1

            self._size -= 1
            self._storage[self._size] = None

            if self._size * 2 < self._capacity:
                new_capacity = max(
                    self._MIN_CAPACITY,
                    int(self._capacity / self._SHRINK_FACTOR),
                )

                if new_capacity < self._capacity:
                    self._resize(new_capacity)

            self._remove_status = self.REMOVE_OK
        else:
            self._remove_status = self.REMOVE_ERR

        return None

    def replace(self, index: int, value: T) -> None:
        # предусловие:
        # 0 <= index < size()
        #
        # постусловие при выполнении предусловия:
        # значение по индексу index заменено на value
        # размер, порядок остальных элементов и их значения не изменены
        # статус replace установлен в REPLACE_OK
        #
        # если предусловие нарушено:
        # массив не изменяется
        # статус replace установлен в REPLACE_ERR

        if 0 <= index < self._size:
            self._storage[index] = value
            self._replace_status = self.REPLACE_OK
        else:
            self._replace_status = self.REPLACE_ERR

        return None

    def clear(self) -> None:
        # предусловие:
        # отсутствует
        #
        # постусловие:
        # из массива удалены все значения
        # size() == 0
        # внутренняя ёмкость равна начальной ёмкости
        # статусы всех операций установлены в *_NIL

        self._size = 0
        self._capacity = self._MIN_CAPACITY
        self._storage = [None] * self._capacity

        self._get_status = self.GET_NIL
        self._insert_status = self.INSERT_NIL
        self._remove_status = self.REMOVE_NIL
        self._replace_status = self.REPLACE_NIL

        return None

    # запросы

    def get(self, index: int) -> Optional[T]:
        # предусловие:
        # 0 <= index < size()
        #
        # результат при выполнении предусловия:
        # возвращено значение по индексу index
        # массив не изменяется
        # статус get установлен в GET_OK
        #
        # если предусловие нарушено:
        # возвращается None
        # массив не изменяется
        # статус get установлен в GET_ERR

        result: Optional[T] = None

        if 0 <= index < self._size:
            result = self._storage[index]
            self._get_status = self.GET_OK
        else:
            self._get_status = self.GET_ERR

        return result

    def size(self) -> int:
        # предусловие:
        # отсутствует
        #
        # результат:
        # возвращено текущее количество значений в массиве
        # массив не изменяется

        result = self._size

        return result

    # запросы статусов

    def get_get_status(self) -> int:
        # предусловие:
        # отсутствует
        #
        # результат:
        # возвращён статус последнего вызова get()
        # GET_NIL, GET_OK или GET_ERR
        # состояние массива не изменяется

        result = self._get_status

        return result

    def get_insert_status(self) -> int:
        # предусловие:
        # отсутствует
        #
        # результат:
        # возвращён статус последнего вызова insert()
        # INSERT_NIL, INSERT_OK или INSERT_ERR
        # состояние массива не изменяется

        result = self._insert_status

        return result

    def get_remove_status(self) -> int:
        # предусловие:
        # отсутствует
        #
        # результат:
        # возвращён статус последнего вызова remove()
        # REMOVE_NIL, REMOVE_OK или REMOVE_ERR
        # состояние массива не изменяется

        result = self._remove_status

        return result

    def get_replace_status(self) -> int:
        # предусловие:
        # отсутствует
        #
        # результат:
        # возвращён статус последнего вызова replace()
        # REPLACE_NIL, REPLACE_OK или REPLACE_ERR
        # состояние массива не изменяется

        result = self._replace_status

        return result

    # закрытая операция реализации

    def _resize(self, new_capacity: int) -> None:
        # предусловие:
        # new_capacity >= size()
        #
        # постусловие:
        # внутренняя ёмкость равна new_capacity
        # значения, их порядок и логический размер массива не изменены
        #
        # _resize не входит в публичный интерфейс АТД

        new_storage: list[Optional[T]] = [None] * new_capacity
        index = 0

        while index < self._size:
            new_storage[index] = self._storage[index]
            index += 1

        self._storage = new_storage
        self._capacity = new_capacity

        return None
