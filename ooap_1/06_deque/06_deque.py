from typing import Generic, Optional, TypeVar


T = TypeVar("T")


class _Node(Generic[T]):
    """Внутренняя деталь реализации, не входящая в интерфейс АТД."""

    def __init__(self, value: T) -> None:
        self.value = value
        self.prev: Optional["_Node[T]"] = None
        self.next: Optional["_Node[T]"] = None

        return None


class ParentQueue(Generic[T]):
    """
    Общая реализация АТД Queue и Deque.

    Публичный интерфейс общего АТД:
    - add_tail(value), добавить значение в хвост
    - remove_front(), удалить значение из головы
    - clear(), очистить очередь
    - get_front(), получить значение из головы
    - size(), получить количество значений
    - get_remove_front_status(), получить статус последнего remove_front()
    - get_get_front_status(), получить статус последнего get_front()

    Инварианты класса:
    - size() >= 0
    - у пустой очереди нет головы и хвоста
    - у непустой очереди есть голова и хвост
    - голова не имеет предыдущего узла
    - хвост не имеет следующего узла

    Гарантии эффективности:
    - все публичные операции работают за O(1)

    Внутри используется двусвязная структура, хотя обычной Queue обратные
    связи не нужны. Благодаря этому Deque наследует общую реализацию без
    переопределений и добавляет только операции второго конца.
    """

    REMOVE_FRONT_NIL = 0
    REMOVE_FRONT_OK = 1
    REMOVE_FRONT_ERR = 2

    GET_FRONT_NIL = 0
    GET_FRONT_OK = 1
    GET_FRONT_ERR = 2

    def __init__(self) -> None:
        # предусловие:
        # отсутствует
        #
        # постусловие:
        # создана новая пустая очередь
        # size() == 0
        # статусы remove_front() и get_front() установлены в *_NIL

        self._head: Optional[_Node[T]] = None
        self._tail: Optional[_Node[T]] = None
        self._size = 0

        self._remove_front_status = self.REMOVE_FRONT_NIL
        self._get_front_status = self.GET_FRONT_NIL

        return None

    # команды

    def add_tail(self, value: T) -> None:
        # предусловие:
        # отсутствует
        #
        # постусловие:
        # значение добавлено в хвост очереди
        # прежние значения и их порядок не изменены
        # размер очереди увеличен на 1
        # постусловие при пустой очереди
        # +

        new_node = _Node(value)
        new_node.prev = self._tail

        if self._tail is None:
            self._head = new_node
        else:
            self._tail.next = new_node

        self._tail = new_node
        self._size += 1

        return None

    def remove_front(self) -> None:
        # предусловие:
        # очередь не пуста
        #
        # постусловие при выполнении предусловия:
        # значение из головы очереди удалено
        # порядок оставшихся значений не изменён
        # размер очереди уменьшен на 1
        # статус remove_front установлен в REMOVE_FRONT_OK
        #
        # если предусловие нарушено:
        # очередь не изменяется
        # статус remove_front установлен в REMOVE_FRONT_ERR

        if self._head is None:
            self._remove_front_status = self.REMOVE_FRONT_ERR
        else:
            self._head = self._head.next
            self._size -= 1

            if self._head is None:
                self._tail = None
            else:
                self._head.prev = None

            self._remove_front_status = self.REMOVE_FRONT_OK

        return None

    def clear(self) -> None:
        # предусловие:
        # отсутствует
        #
        # постусловие:
        # из очереди удалены все значения
        # size() == 0
        # статусы remove_front() и get_front() установлены в *_NIL

        self._head = None
        self._tail = None
        self._size = 0

        self._remove_front_status = self.REMOVE_FRONT_NIL
        self._get_front_status = self.GET_FRONT_NIL

        return None

    # запросы

    def get_front(self) -> Optional[T]:
        # предусловие:
        # очередь не пуста
        #
        # результат при выполнении предусловия:
        # возвращено значение из головы очереди
        # содержимое очереди не изменяется
        # статус get_front установлен в GET_FRONT_OK
        #
        # если предусловие нарушено:
        # возвращается None
        # очередь не изменяется
        # статус get_front установлен в GET_FRONT_ERR

        result: Optional[T] = None

        if self._head is None:
            self._get_front_status = self.GET_FRONT_ERR
        else:
            result = self._head.value
            self._get_front_status = self.GET_FRONT_OK

        return result

    def size(self) -> int:
        # предусловие:
        # отсутствует
        #
        # результат:
        # возвращено текущее количество значений в очереди
        # состояние очереди не изменяется

        result = self._size

        return result

    # запросы статусов

    def get_remove_front_status(self) -> int:
        # предусловие:
        # отсутствует
        #
        # результат:
        # возвращён статус последнего вызова remove_front()
        # REMOVE_FRONT_NIL, REMOVE_FRONT_OK или REMOVE_FRONT_ERR
        # состояние очереди не изменяется

        result = self._remove_front_status

        return result

    def get_get_front_status(self) -> int:
        # предусловие:
        # отсутствует
        #
        # результат:
        # возвращён статус последнего вызова get_front()
        # GET_FRONT_NIL, GET_FRONT_OK или GET_FRONT_ERR
        # состояние очереди не изменяется

        result = self._get_front_status

        return result


class Queue(ParentQueue[T]):
    """
    Односторонняя очередь FIFO.

    add_tail() соответствует enqueue()
    remove_front() соответствует dequeue()
    get_front() соответствует get()
    """


class Deque(ParentQueue[T]):
    """
    Двусторонняя очередь.

    В дополнение к операциям ParentQueue поддерживает добавление в голову,
    удаление из хвоста и получение значения из хвоста.
    """

    REMOVE_TAIL_NIL = 0
    REMOVE_TAIL_OK = 1
    REMOVE_TAIL_ERR = 2

    GET_TAIL_NIL = 0
    GET_TAIL_OK = 1
    GET_TAIL_ERR = 2

    def __init__(self) -> None:
        # предусловие:
        # отсутствует
        #
        # постусловие:
        # создана новая пустая двусторонняя очередь
        # статусы remove_tail() и get_tail() установлены в *_NIL
        # остальные постусловия определены конструктором ParentQueue

        super().__init__()
        self._remove_tail_status = self.REMOVE_TAIL_NIL
        self._get_tail_status = self.GET_TAIL_NIL

        return None

    # команды

    def add_front(self, value: T) -> None:
        # предусловие:
        # отсутствует
        #
        # постусловие:
        # value добавлено в голову очереди
        # прежние значения и их порядок не изменены
        # размер очереди увеличен на 1

        new_node = _Node(value)
        new_node.next = self._head

        if self._head is None:
            self._tail = new_node
        else:
            self._head.prev = new_node

        self._head = new_node
        self._size += 1

        return None

    def remove_tail(self) -> None:
        # предусловие:
        # очередь не пуста
        #
        # постусловие при выполнении предусловия:
        # значение из хвоста очереди удалено
        # порядок оставшихся значений не изменён
        # размер очереди уменьшен на 1
        # статус remove_tail установлен в REMOVE_TAIL_OK
        #
        # если предусловие нарушено:
        # очередь не изменяется
        # статус remove_tail установлен в REMOVE_TAIL_ERR

        if self._tail is None:
            self._remove_tail_status = self.REMOVE_TAIL_ERR
        else:
            self._tail = self._tail.prev
            self._size -= 1

            if self._tail is None:
                self._head = None
            else:
                self._tail.next = None

            self._remove_tail_status = self.REMOVE_TAIL_OK

        return None

    def clear(self) -> None:
        # предусловие:
        # отсутствует
        #
        # постусловие:
        # выполнены постусловия ParentQueue.clear()
        # статусы remove_tail() и get_tail() установлены в *_NIL

        super().clear()
        self._remove_tail_status = self.REMOVE_TAIL_NIL
        self._get_tail_status = self.GET_TAIL_NIL

        return None

    # запросы

    def get_tail(self) -> Optional[T]:
        # предусловие:
        # очередь не пуста
        #
        # результат при выполнении предусловия:
        # возвращено значение из хвоста очереди
        # содержимое очереди не изменяется
        # статус get_tail установлен в GET_TAIL_OK
        #
        # если предусловие нарушено:
        # возвращается None
        # очередь не изменяется
        # статус get_tail установлен в GET_TAIL_ERR

        result: Optional[T] = None

        if self._tail is None:
            self._get_tail_status = self.GET_TAIL_ERR
        else:
            result = self._tail.value
            self._get_tail_status = self.GET_TAIL_OK

        return result

    # запросы статусов

    def get_remove_tail_status(self) -> int:
        # предусловие:
        # отсутствует
        #
        # результат:
        # возвращён статус последнего вызова remove_tail()
        # REMOVE_TAIL_NIL, REMOVE_TAIL_OK или REMOVE_TAIL_ERR
        # состояние очереди не изменяется

        result = self._remove_tail_status

        return result

    def get_get_tail_status(self) -> int:
        # предусловие:
        # отсутствует
        #
        # результат:
        # возвращён статус последнего вызова get_tail()
        # GET_TAIL_NIL, GET_TAIL_OK или GET_TAIL_ERR
        # состояние очереди не изменяется

        result = self._get_tail_status

        return result
