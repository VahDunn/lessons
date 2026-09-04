from typing import Generic, Optional, TypeVar


T = TypeVar("T")


class _Node(Generic[T]):
    """Внутренняя деталь реализации, не входящая в интерфейс АТД."""

    def __init__(self, value: T) -> None:
        self.value = value
        self.prev: Optional["_Node[T]"] = None
        self.next: Optional["_Node[T]"] = None

        return None


class ParentList(Generic[T]):
    """
    Общая реализация АТД LinkedList и TwoWayList с курсором.

    Инварианты класса:
    - size() >= 0
    - пустой список не имеет первого, последнего и текущего элементов
    - в непустом списке курсор всегда установлен на один из его элементов
    - первый и последний элементы доступны за O(1)
    - size() возвращает размер за O(1).
    """

    HEAD_NIL = 0
    HEAD_OK = 1
    HEAD_ERR = 2

    TAIL_NIL = 0
    TAIL_OK = 1
    TAIL_ERR = 2

    RIGHT_NIL = 0
    RIGHT_OK = 1
    RIGHT_ERR = 2

    GET_NIL = 0
    GET_OK = 1
    GET_ERR = 2

    PUT_RIGHT_NIL = 0
    PUT_RIGHT_OK = 1
    PUT_RIGHT_ERR = 2

    PUT_LEFT_NIL = 0
    PUT_LEFT_OK = 1
    PUT_LEFT_ERR = 2

    REMOVE_NIL = 0
    REMOVE_OK = 1
    REMOVE_ERR = 2

    ADD_TO_EMPTY_NIL = 0
    ADD_TO_EMPTY_OK = 1
    ADD_TO_EMPTY_ERR = 2

    REPLACE_NIL = 0
    REPLACE_OK = 1
    REPLACE_ERR = 2

    FIND_NIL = 0
    FIND_OK = 1
    FIND_ERR = 2

    def __init__(self) -> None:
        # предусловие:
        # отсутствует
        #
        # постусловие:
        # создан новый пустой список
        # size() == 0
        # is_value(), is_head() и is_tail() возвращают False
        # статусы всех операций установлены в *_NIL

        self._head: Optional[_Node[T]] = None
        self._tail: Optional[_Node[T]] = None
        self._cursor: Optional[_Node[T]] = None
        self._size = 0

        self._head_status = self.HEAD_NIL
        self._tail_status = self.TAIL_NIL
        self._right_status = self.RIGHT_NIL
        self._get_status = self.GET_NIL
        self._put_right_status = self.PUT_RIGHT_NIL
        self._put_left_status = self.PUT_LEFT_NIL
        self._remove_status = self.REMOVE_NIL
        self._add_to_empty_status = self.ADD_TO_EMPTY_NIL
        self._replace_status = self.REPLACE_NIL
        self._find_status = self.FIND_NIL

        return None

    # команды

    def head(self) -> None:
        # предусловие:
        # список не пустой
        #
        # постусловие при выполнении предусловия:
        # курсор установлен на первый элемент списка
        # список не изменён
        # статус head установлен в HEAD_OK
        #
        # если предусловие нарушено:
        # список и курсор не изменяются
        # статус head установлен в HEAD_ERR

        if self._head is not None:
            self._cursor = self._head
            self._head_status = self.HEAD_OK
        else:
            self._head_status = self.HEAD_ERR

        return None

    def tail(self) -> None:
        # предусловие:
        # список не пустой
        #
        # постусловие при выполнении предусловия:
        # курсор установлен на последний элемент списка
        # список не изменён
        # статус tail установлен в TAIL_OK
        #
        # если предусловие нарушено:
        # список и курсор не изменяются
        # статус tail установлен в TAIL_ERR

        if self._tail is not None:
            self._cursor = self._tail
            self._tail_status = self.TAIL_OK
        else:
            self._tail_status = self.TAIL_ERR

        return None

    def right(self) -> None:
        # предусловие:
        # список не пустой и курсор находится не на последнем элементе
        #
        # постусловие при выполнении предусловия:
        # курсор сдвинут на один элемент вправо
        # список не изменён
        # статус right установлен в RIGHT_OK
        #
        # если предусловие нарушено:
        # список и курсор не изменяются
        # статус right установлен в RIGHT_ERR

        if self._cursor is not None and self._cursor.next is not None:
            self._cursor = self._cursor.next
            self._right_status = self.RIGHT_OK
        else:
            self._right_status = self.RIGHT_ERR

        return None

    def put_right(self, value: T) -> None:
        # предусловие:
        # список не пустой
        #
        # постусловие при выполнении предусловия:
        # после текущего элемента вставлен новый элемент value
        # курсор остаётся на прежнем элементе
        # размер списка увеличен на 1
        # статус put_right установлен в PUT_RIGHT_OK
        #
        # если предусловие нарушено:
        # список и курсор не изменяются
        # статус put_right установлен в PUT_RIGHT_ERR

        if self._cursor is not None:
            new_node = _Node(value)
            old_right = self._cursor.next

            new_node.prev = self._cursor
            new_node.next = old_right
            self._cursor.next = new_node

            if old_right is None:
                self._tail = new_node
            else:
                old_right.prev = new_node

            self._size += 1
            self._put_right_status = self.PUT_RIGHT_OK
        else:
            self._put_right_status = self.PUT_RIGHT_ERR

        return None

    def put_left(self, value: T) -> None:
        # предусловие:
        # список не пустой
        #
        # постусловие при выполнении предусловия:
        # перед текущим элементом вставлен новый элемент value
        # курсор остаётся на прежнем элементе
        # размер списка увеличен на 1
        # статус put_left установлен в PUT_LEFT_OK
        #
        # если предусловие нарушено:
        # список и курсор не изменяются
        # статус put_left установлен в PUT_LEFT_ERR

        if self._cursor is not None:
            new_node = _Node(value)
            old_left = self._cursor.prev

            new_node.prev = old_left
            new_node.next = self._cursor
            self._cursor.prev = new_node

            if old_left is None:
                self._head = new_node
            else:
                old_left.next = new_node

            self._size += 1
            self._put_left_status = self.PUT_LEFT_OK
        else:
            self._put_left_status = self.PUT_LEFT_ERR

        return None

    def remove(self) -> None:
        # предусловие:
        # список не пустой
        #
        # постусловие при выполнении предусловия:
        # текущий элемент удалён
        # размер списка уменьшен на 1
        # курсор установлен на правого соседа удалённого элемента, если он был
        # иначе курсор установлен на его левого соседа, если он был
        # после удаления единственного элемента курсор не установлен
        # статус remove установлен в REMOVE_OK
        #
        # если предусловие нарушено:
        # список и курсор не изменяются
        # статус remove установлен в REMOVE_ERR

        if self._cursor is not None:
            removed = self._cursor
            left = removed.prev
            right = removed.next

            if left is None:
                self._head = right
            else:
                left.next = right

            if right is None:
                self._tail = left
            else:
                right.prev = left

            self._cursor = right if right is not None else left
            removed.prev = None
            removed.next = None
            self._size -= 1
            self._remove_status = self.REMOVE_OK
        else:
            self._remove_status = self.REMOVE_ERR

        return None

    def clear(self) -> None:
        # предусловие:
        # отсутствует
        #
        # постусловие:
        # из списка удалены все элементы
        # size() == 0
        # is_value(), is_head() и is_tail() возвращают False
        # статусы всех операций установлены в *_NIL

        self._head = None
        self._tail = None
        self._cursor = None
        self._size = 0

        self._head_status = self.HEAD_NIL
        self._tail_status = self.TAIL_NIL
        self._right_status = self.RIGHT_NIL
        self._get_status = self.GET_NIL
        self._put_right_status = self.PUT_RIGHT_NIL
        self._put_left_status = self.PUT_LEFT_NIL
        self._remove_status = self.REMOVE_NIL
        self._add_to_empty_status = self.ADD_TO_EMPTY_NIL
        self._replace_status = self.REPLACE_NIL
        self._find_status = self.FIND_NIL

        return None

    def add_to_empty(self, value: T) -> None:
        # предусловие:
        # список пустой
        #
        # постусловие при выполнении предусловия:
        # в список добавлен единственный элемент value
        # курсор установлен на этот элемент
        # head и tail указывают на этот элемент
        # size() == 1
        # is_head(), is_tail() и is_value() возвращают True
        # статус add_to_empty установлен в ADD_TO_EMPTY_OK
        #
        # если предусловие нарушено:
        # список и курсор не изменяются
        # статус add_to_empty установлен в ADD_TO_EMPTY_ERR

        if self._size == 0:
            new_node = _Node(value)
            self._head = new_node
            self._tail = new_node
            self._cursor = new_node
            self._size = 1
            self._add_to_empty_status = self.ADD_TO_EMPTY_OK
        else:
            self._add_to_empty_status = self.ADD_TO_EMPTY_ERR

        return None

    def add_tail(self, value: T) -> None:
        # предусловие:
        # отсутствует
        #
        # постусловие:
        # в конец списка добавлен элемент value
        # размер списка увеличен на 1
        # если список был пуст, курсор установлен на добавленный элемент
        # иначе положение курсора не изменилось

        new_node = _Node(value)

        if self._tail is None:
            self._head = new_node
            self._tail = new_node
            self._cursor = new_node
        else:
            new_node.prev = self._tail
            self._tail.next = new_node
            self._tail = new_node

        self._size += 1

        return None

    def replace(self, value: T) -> None:
        # предусловие:
        # список не пустой
        #
        # постусловие при выполнении предусловия:
        # значение текущего элемента заменено на value
        # структура списка и положение курсора не изменены
        # статус replace установлен в REPLACE_OK
        #
        # если предусловие нарушено:
        # список и курсор не изменяются
        # статус replace установлен в REPLACE_ERR

        if self._cursor is not None:
            self._cursor.value = value
            self._replace_status = self.REPLACE_OK
        else:
            self._replace_status = self.REPLACE_ERR

        return None

    def find(self, value: T) -> None:
        # предусловие:
        # список не пустой
        #
        # постусловие при выполнении предусловия и успешном поиске:
        # курсор установлен на первый элемент справа от текущего, значение
        # которого равно value
        # список не изменён
        # статус find установлен в FIND_OK
        #
        # если список пуст или подходящего элемента справа нет:
        # список и курсор не изменяются
        # статус find установлен в FIND_ERR

        found: Optional[_Node[T]] = None

        if self._cursor is not None:
            found = self._cursor.next

            while found is not None and found.value != value:
                found = found.next

        if found is not None:
            self._cursor = found
            self._find_status = self.FIND_OK
        else:
            self._find_status = self.FIND_ERR

        return None

    def remove_all(self, value: T) -> None:
        # предусловие:
        # отсутствует
        #
        # постусловие:
        # из списка удалены все элементы со значением value
        # размер списка уменьшен на количество удалённых элементов
        # если текущий элемент не удалён, положение курсора не изменилось
        # если текущий элемент удалён, курсор установлен на ближайший
        # оставшийся элемент справа, иначе на ближайший оставшийся слева
        # если список стал пустым, курсор не установлен

        current = self._head

        while current is not None:
            next_node = current.next

            if current.value == value:
                left = current.prev
                right = current.next

                if left is None:
                    self._head = right
                else:
                    left.next = right

                if right is None:
                    self._tail = left
                else:
                    right.prev = left

                if current is self._cursor:
                    self._cursor = right if right is not None else left

                current.prev = None
                current.next = None
                self._size -= 1

            current = next_node

        return None

    # запросы

    def get(self) -> Optional[T]:
        # предусловие:
        # список не пустой
        #
        # результат при выполнении предусловия:
        # возвращено значение текущего элемента
        # список и курсор не изменяются
        # статус get установлен в GET_OK
        #
        # если предусловие нарушено:
        # возвращается None
        # список и курсор не изменяются
        # статус get установлен в GET_ERR

        result: Optional[T] = None

        if self._cursor is not None:
            result = self._cursor.value
            self._get_status = self.GET_OK
        else:
            self._get_status = self.GET_ERR

        return result

    def size(self) -> int:
        # предусловие:
        # отсутствует
        #
        # результат:
        # возвращено текущее количество элементов в списке
        # список и курсор не изменяются

        result = self._size

        return result

    def is_head(self) -> bool:
        # предусловие:
        # отсутствует
        #
        # результат:
        # возвращается True, только если список не пустой и курсор установлен
        # на первый элемент, для пустого списка возвращается False
        # список и курсор не изменяются

        result = self._cursor is not None and self._cursor is self._head

        return result

    def is_tail(self) -> bool:
        # предусловие:
        # отсутствует
        #
        # результат:
        # возвращается True, только если список не пустой и курсор установлен
        # на последний элемент, для пустого списка возвращается False
        # список и курсор не изменяются

        result = self._cursor is not None and self._cursor is self._tail

        return result

    def is_value(self) -> bool:
        # предусловие:
        # отсутствует
        #
        # результат:
        # возвращается True, если курсор установлен на элемент списка
        # возвращается False для пустого списка
        # список и курсор не изменяются

        result = self._cursor is not None

        return result

    # запросы статусов

    def get_head_status(self) -> int:
        # предусловие:
        # отсутствует
        #
        # результат:
        # возвращён статус последнего вызова head():
        # HEAD_NIL, HEAD_OK или HEAD_ERR
        # состояние списка не изменяется

        result = self._head_status

        return result

    def get_tail_status(self) -> int:
        # предусловие:
        # отсутствует
        #
        # результат:
        # возвращён статус последнего вызова tail():
        # TAIL_NIL, TAIL_OK или TAIL_ERR
        # состояние списка не изменяется

        result = self._tail_status

        return result

    def get_right_status(self) -> int:
        # предусловие:
        # отсутствует
        #
        # результат:
        # возвращён статус последнего вызова right():
        # RIGHT_NIL, RIGHT_OK или RIGHT_ERR
        # состояние списка не изменяется

        result = self._right_status

        return result

    def get_get_status(self) -> int:
        # предусловие:
        # отсутствует
        #
        # результат:
        # возвращён статус последнего вызова get():
        # GET_NIL, GET_OK или GET_ERR
        # состояние списка не изменяется

        result = self._get_status

        return result

    def get_put_right_status(self) -> int:
        # предусловие:
        # отсутствует
        #
        # результат:
        # возвращён статус последнего вызова put_right():
        # PUT_RIGHT_NIL, PUT_RIGHT_OK или PUT_RIGHT_ERR
        # состояние списка не изменяется

        result = self._put_right_status

        return result

    def get_put_left_status(self) -> int:
        # предусловие:
        # отсутствует
        #
        # результат:
        # возвращён статус последнего вызова put_left():
        # PUT_LEFT_NIL, PUT_LEFT_OK или PUT_LEFT_ERR
        # состояние списка не изменяется

        result = self._put_left_status

        return result

    def get_remove_status(self) -> int:
        # предусловие:
        # отсутствует
        #
        # результат:
        # возвращён статус последнего вызова remove():
        # REMOVE_NIL, REMOVE_OK или REMOVE_ERR
        # состояние списка не изменяется

        result = self._remove_status

        return result

    def get_add_to_empty_status(self) -> int:
        # предусловие:
        # отсутствует
        #
        # результат:
        # возвращён статус последнего вызова add_to_empty():
        # ADD_TO_EMPTY_NIL, ADD_TO_EMPTY_OK или ADD_TO_EMPTY_ERR
        # состояние списка не изменяется

        result = self._add_to_empty_status

        return result

    def get_replace_status(self) -> int:
        # предусловие:
        # отсутствует
        #
        # результат:
        # возвращён статус последнего вызова replace():
        # REPLACE_NIL, REPLACE_OK или REPLACE_ERR
        # состояние списка не изменяется

        result = self._replace_status

        return result

    def get_find_status(self) -> int:
        # предусловие:
        # отсутствует
        #
        # результат:
        # возвращён статус последнего вызова find():
        # FIND_NIL, FIND_OK или FIND_ERR
        # состояние списка не изменяется

        result = self._find_status

        return result


class LinkedList(ParentList[T]):
    """Однонаправленный интерфейс списка без операции движения влево."""


class TwoWayList(ParentList[T]):
    """Двунаправленный список с возможностью движения курсора влево."""

    LEFT_NIL = 0
    LEFT_OK = 1
    LEFT_ERR = 2

    def __init__(self) -> None:
        # предусловие:
        # отсутствует
        #
        # постусловие:
        # создан новый пустой двунаправленный список
        # статус left установлен в LEFT_NIL
        # остальные постусловия определены конструктором ParentList

        super().__init__()
        self._left_status = self.LEFT_NIL

        return None

    # команды

    def left(self) -> None:
        # предусловие:
        # список не пустой и курсор находится не на первом элементе
        #
        # постусловие при выполнении предусловия:
        # курсор сдвинут на один элемент влево
        # список не изменён
        # статус left установлен в LEFT_OK
        #
        # если предусловие нарушено:
        # список и курсор не изменяются
        # статус left установлен в LEFT_ERR

        if self._cursor is not None and self._cursor.prev is not None:
            self._cursor = self._cursor.prev
            self._left_status = self.LEFT_OK
        else:
            self._left_status = self.LEFT_ERR

        return None

    def clear(self) -> None:
        # предусловие:
        # отсутствует
        #
        # постусловие:
        # выполнены постусловия ParentList.clear()
        # статус left установлен в LEFT_NIL

        super().clear()
        self._left_status = self.LEFT_NIL

        return None

    # запросы статусов

    def get_left_status(self) -> int:
        # предусловие:
        # отсутствует
        #
        # результат:
        # возвращён статус последнего вызова left():
        # LEFT_NIL, LEFT_OK или LEFT_ERR
        # состояние списка не изменяется

        result = self._left_status

        return result
