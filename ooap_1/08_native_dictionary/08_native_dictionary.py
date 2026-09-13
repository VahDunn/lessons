from typing import Generic, Optional, TypeVar, cast


T = TypeVar("T")


class NativeDictionary(Generic[T]):
    """
    АТД словаря со строковыми ключами.

    Публичный интерфейс АТД:
    - put(key, value), добавить новую пару или заменить значение существующей
    - remove(key), удалить пару по ключу
    - clear(), удалить все пары
    - get(key), получить значение по ключу
    - is_key(key), проверить наличие ключа
    - size(), получить количество пар
    - get_remove_status(), получить статус последнего remove()
    - get_get_status(), получить статус последнего get()

    Инварианты класса:
    - все ключи имеют тип str
    - каждый ключ присутствует не более одного раза
    - каждому присутствующему ключу соответствует ровно одно значение
    - size() равно количеству хранящихся ключей
    - is_key(key) истинно только пара ключ-значение существует

    Гарантии эффективности:
    - put(), remove(), get() и is_key() работают за O(1) в среднем без
      учёта вычисления хеша строки
    - put() и remove() имеют амортизированную сложность O(1), потому что
      иногда перестраивают внутреннюю таблицу
    - в худшем случае одна операция работает за O(N) из-за коллизий или
      перестройки, где N — количество внутренних слотов
    - size() работает за O(1)

    Внутри используется автоматически расширяемая хеш-таблица.
    Её ёмкость, слоты и маркеры удаления не входят в публичный
    интерфейс АТД.

    None является допустимым значением. Успешное получение такого значения
    отличается от отсутствующего ключа с помощью статуса get().
    """

    REMOVE_NIL = 0
    REMOVE_OK = 1
    REMOVE_ERR = 2

    GET_NIL = 0
    GET_OK = 1
    GET_ERR = 2

    _EMPTY = object()
    _DELETED = object()

    _INITIAL_CAPACITY = 16
    _MAX_LOAD_NUMERATOR = 7
    _MAX_LOAD_DENOMINATOR = 10
    _MIN_LOAD_NUMERATOR = 2
    _MIN_LOAD_DENOMINATOR = 10
    _REBUILD_DELETED_RATIO = 4

    def __init__(self) -> None:
        # предусловие:
        # отсутствует
        #
        # постусловие:
        # создан новый пустой словарь
        # size() == 0
        # статусы remove() и get() установлены в *_NIL

        self._capacity = self._INITIAL_CAPACITY
        self._keys: list[object] = [self._EMPTY] * self._capacity
        self._values: list[Optional[T]] = [None] * self._capacity
        self._size = 0
        self._deleted_count = 0

        self._remove_status = self.REMOVE_NIL
        self._get_status = self.GET_NIL

        return None

    # команды

    def put(self, key: str, value: T) -> None:
        # предусловие:
        # ключ имеет тип str
        #
        # постусловие, если ключ отсутствовал:
        # пара ключ и значение добавлена в словарь
        # прежние пары не изменены
        # размер словаря увеличен на 1
        #
        # постусловие, если ключ уже присутствовал:
        # связанное с ключом значение заменено
        # остальные пары не изменены
        # размер словаря не изменился

        self._require_string_key(key)
        slot = self._find_key_slot(key)

        if slot is not None:
            self._values[slot] = value
            return None

        self._prepare_for_insert()
        slot = self._find_free_slot(key)

        if slot is None:
            raise RuntimeError("dictionary has no free slot")

        if self._keys[slot] is self._DELETED:
            self._deleted_count -= 1

        self._keys[slot] = key
        self._values[slot] = value
        self._size += 1

        return None

    def remove(self, key: str) -> None:
        # предусловие:
        # ключ имеет тип str и присутствует в словаре
        #
        # постусловие при выполнении предусловия:
        # пара с ключом удалена из словаря
        # остальные пары не изменены
        # размер словаря уменьшен на 1
        # статус remove установлен в REMOVE_OK
        #
        # если ключ отсутствует:
        # словарь не изменяется
        # статус remove установлен в REMOVE_ERR

        self._require_string_key(key)
        slot = self._find_key_slot(key)

        if slot is None:
            self._remove_status = self.REMOVE_ERR
        else:
            self._keys[slot] = self._DELETED
            self._values[slot] = None
            self._size -= 1
            self._deleted_count += 1

            self._compact_after_remove()
            self._remove_status = self.REMOVE_OK

        return None

    def clear(self) -> None:
        # предусловие:
        # отсутствует
        #
        # постусловие:
        # из словаря удалены все пары
        # size() == 0
        # статусы remove() и get() установлены в *_NIL

        self._capacity = self._INITIAL_CAPACITY
        self._keys = [self._EMPTY] * self._capacity
        self._values = [None] * self._capacity
        self._size = 0
        self._deleted_count = 0

        self._remove_status = self.REMOVE_NIL
        self._get_status = self.GET_NIL

        return None

    # запросы

    def get(self, key: str) -> Optional[T]:
        # предусловие:
        # ключ имеет тип str и присутствует в словаре
        #
        # результат при выполнении предусловия:
        # возвращено связанное с ключом значение
        # пары словаря не изменяются
        # статус get установлен в GET_OK
        #
        # если ключ отсутствует:
        # возвращается None
        # словарь не изменяется
        # статус get установлен в GET_ERR

        self._require_string_key(key)
        result: Optional[T] = None
        slot = self._find_key_slot(key)

        if slot is None:
            self._get_status = self.GET_ERR
        else:
            result = self._values[slot]
            self._get_status = self.GET_OK

        return result

    def is_key(self, key: str) -> bool:
        # предусловие:
        # ключ имеет тип str
        #
        # результат:
        # возвращается True, если пара с ключом существует, иначе False
        # состояние словаря и статусы операций не изменяются

        self._require_string_key(key)
        result = self._find_key_slot(key) is not None

        return result

    def size(self) -> int:
        # предусловие:
        # отсутствует
        #
        # результат:
        # возвращено текущее количество пар в словаре
        # состояние словаря не изменяется

        result = self._size

        return result

    # запросы статусов

    def get_remove_status(self) -> int:
        # предусловие:
        # отсутствует
        #
        # результат:
        # возвращён статус последнего вызова remove()
        # REMOVE_NIL, REMOVE_OK или REMOVE_ERR
        # состояние словаря не изменяется

        result = self._remove_status

        return result

    def get_get_status(self) -> int:
        # предусловие:
        # отсутствует
        #
        # результат:
        # возвращён статус последнего вызова get()
        # GET_NIL, GET_OK или GET_ERR
        # состояние словаря не изменяется

        result = self._get_status

        return result

    # закрытые операции реализации

    def _hash_key(self, key: str) -> int:
        # Полиномиальный хеш вычисляется одновременно с приведением к диапазону
        # слотов, поэтому промежуточное число не растёт вместе с длиной строки.

        result = 0

        for symbol in key:
            result = (result * 31 + ord(symbol)) % self._capacity

        return result

    def _find_key_slot(self, key: str) -> Optional[int]:
        # Обычный пустой слот завершает поиск. Маркер удалённого слота поиск не
        # завершает, потому что нужный ключ мог попасть дальше из-за коллизии.

        start = self._hash_key(key)
        offset = 0

        while offset < self._capacity:
            slot = (start + offset) % self._capacity
            current_key = self._keys[slot]

            if current_key is self._EMPTY:
                return None

            if current_key is not self._DELETED and current_key == key:
                return slot

            offset += 1

        return None

    def _find_free_slot(self, key: str) -> Optional[int]:
        # При поиске запоминается первый удалённый слот. Обычный пустой слот
        # можно занять сразу, но предпочтение отдаётся найденному ранее маркеру.

        start = self._hash_key(key)
        first_deleted: Optional[int] = None
        offset = 0

        while offset < self._capacity:
            slot = (start + offset) % self._capacity
            current_key = self._keys[slot]

            if current_key is self._EMPTY:
                if first_deleted is not None:
                    return first_deleted

                return slot

            if current_key is self._DELETED and first_deleted is None:
                first_deleted = slot

            offset += 1

        return first_deleted

    def _prepare_for_insert(self) -> None:
        # Рост зависит от числа живых пар. Если мешают только накопившиеся
        # маркеры удаления, таблица перестраивается без увеличения ёмкости.

        next_size = self._size + 1
        occupied_slots = self._size + self._deleted_count + 1

        if (
            next_size * self._MAX_LOAD_DENOMINATOR
            > self._capacity * self._MAX_LOAD_NUMERATOR
        ):
            self._resize(self._capacity * 2)
        elif (
            occupied_slots * self._MAX_LOAD_DENOMINATOR
            > self._capacity * self._MAX_LOAD_NUMERATOR
        ):
            self._resize(self._capacity)

        return None

    def _compact_after_remove(self) -> None:
        # При малой загрузке таблица уменьшается. Если уменьшать её ещё рано,
        # большое количество маркеров удаления убирается перестройкой.

        if (
            self._capacity > self._INITIAL_CAPACITY
            and self._size * self._MIN_LOAD_DENOMINATOR
            < self._capacity * self._MIN_LOAD_NUMERATOR
        ):
            new_capacity = max(
                self._INITIAL_CAPACITY,
                self._capacity // 2,
            )
            self._resize(new_capacity)
        elif (
            self._deleted_count * self._REBUILD_DELETED_RATIO
            >= self._capacity
        ):
            self._resize(self._capacity)

        return None

    def _resize(self, new_capacity: int) -> None:
        # Перестраивает внутреннюю таблицу, сохраняя все пары, их количество и
        # публичные статусы. Ёмкость не является частью состояния АТД.

        old_keys = self._keys
        old_values = self._values
        old_size = self._size

        self._capacity = new_capacity
        self._keys = [self._EMPTY] * self._capacity
        self._values = [None] * self._capacity
        self._size = 0
        self._deleted_count = 0

        index = 0

        while index < len(old_keys):
            current_key = old_keys[index]

            if (
                current_key is not self._EMPTY
                and current_key is not self._DELETED
            ):
                key = cast(str, current_key)
                slot = self._find_free_slot(key)

                if slot is None:
                    raise RuntimeError("failed to rebuild dictionary")

                self._keys[slot] = key
                self._values[slot] = old_values[index]
                self._size += 1

            index += 1

        if self._size != old_size:
            raise RuntimeError("dictionary size changed during rebuild")

        return None

    @staticmethod
    def _require_string_key(key: str) -> None:
        if not isinstance(key, str):
            raise TypeError("key must be a string")

        return None
