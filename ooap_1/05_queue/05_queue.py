from typing import Generic, Optional, TypeVar


T = TypeVar("T")


class _Node(Generic[T]):
    """Внутренняя деталь реализации, не входящая в интерфейс АТД."""

    def __init__(self, value: T) -> None:
        self.value = value
        self.next: Optional["_Node[T]"] = None

        return None


class Queue(Generic[T]):
    """
    АТД очереди.

    Публичный интерфейс АТД:
    - enqueue(value), добавить значение в хвост очереди
    - dequeue(), удалить значение из головы очереди
    - clear(), очистить очередь
    - get(), получить значение из головы очереди
    - size(), получить количество значений
    - get_dequeue_status(), получить статус последнего dequeue()
    - get_get_status(), получить статус последнего get()

    Инварианты класса:
    - size() >= 0
    - у пустой очереди нет головы и хвоста
    - у непустой очереди есть голова и хвост
    - первым удаляется значение, добавленное раньше остальных

    Гарантии эффективности:
    - enqueue(), dequeue(), get() и size() работают за O(1)
    """

    DEQUEUE_NIL = 0
    DEQUEUE_OK = 1
    DEQUEUE_ERR = 2

    GET_NIL = 0
    GET_OK = 1
    GET_ERR = 2

    def __init__(self) -> None:
        # предусловие:
        # отсутствует
        #
        # постусловие:
        # создана новая пустая очередь
        # size() == 0
        # статусы dequeue() и get() установлены в *_NIL

        self._head: Optional[_Node[T]] = None
        self._tail: Optional[_Node[T]] = None
        self._size = 0

        self._dequeue_status = self.DEQUEUE_NIL
        self._get_status = self.GET_NIL

        return None

    # команды

    def enqueue(self, value: T) -> None:
        # предусловие:
        # отсутствует
        #
        # постусловие:
        # value добавлено в хвост очереди
        # прежние значения и их порядок не изменены
        # размер очереди увеличен на 1

        new_node = _Node(value)

        if self._tail is None:
            self._head = new_node
            self._tail = new_node
        else:
            self._tail.next = new_node
            self._tail = new_node

        self._size += 1

        return None

    def dequeue(self) -> None:
        # предусловие:
        # очередь не пуста
        #
        # постусловие при выполнении предусловия:
        # значение из головы очереди удалено
        # порядок оставшихся значений не изменён
        # размер очереди уменьшен на 1
        # статус dequeue установлен в DEQUEUE_OK
        #
        # если предусловие нарушено:
        # очередь не изменяется
        # статус dequeue установлен в DEQUEUE_ERR

        if self._head is None:
            self._dequeue_status = self.DEQUEUE_ERR
        else:
            self._head = self._head.next
            self._size -= 1

            if self._head is None:
                self._tail = None

            self._dequeue_status = self.DEQUEUE_OK

        return None

    def clear(self) -> None:
        # предусловие:
        # отсутствует
        #
        # постусловие:
        # из очереди удалены все значения
        # size() == 0
        # статусы dequeue() и get() установлены в *_NIL

        self._head = None
        self._tail = None
        self._size = 0

        self._dequeue_status = self.DEQUEUE_NIL
        self._get_status = self.GET_NIL

        return None

    # запросы

    def get(self) -> Optional[T]:
        # предусловие:
        # очередь не пуста
        #
        # результат при выполнении предусловия:
        # возвращено значение из головы очереди
        # содержимое очереди не изменяется
        # статус get установлен в GET_OK
        #
        # если предусловие нарушено:
        # возвращается None
        # очередь не изменяется
        # статус get установлен в GET_ERR

        result: Optional[T] = None

        if self._head is None:
            self._get_status = self.GET_ERR
        else:
            result = self._head.value
            self._get_status = self.GET_OK

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

    def get_dequeue_status(self) -> int:
        # предусловие:
        # отсутствует
        #
        # результат:
        # возвращён статус последнего вызова dequeue()
        # DEQUEUE_NIL, DEQUEUE_OK или DEQUEUE_ERR
        # состояние очереди не изменяется

        result = self._dequeue_status

        return result

    def get_get_status(self) -> int:
        # предусловие:
        # отсутствует
        #
        # результат:
        # возвращён статус последнего вызова get()
        # GET_NIL, GET_OK или GET_ERR
        # состояние очереди не изменяется

        result = self._get_status

        return result
