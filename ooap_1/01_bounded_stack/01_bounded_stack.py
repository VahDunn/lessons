from typing import Generic, Optional, TypeVar


T = TypeVar("T")


class BoundedStack(Generic[T]):
    """
    Инварианты класса:
    - максимальный размер стека положителен;
    - 0 <= size() <= max_size();
    - максимальный размер стека не изменяется после создания объекта.
    """

    PUSH_NIL = 0
    PUSH_OK = 1
    PUSH_ERR = 2

    POP_NIL = 0
    POP_OK = 1
    POP_ERR = 2

    PEEK_NIL = 0
    PEEK_OK = 1
    PEEK_ERR = 2

    DEFAULT_MAX_SIZE = 32

    def __init__(self, max_size: int = DEFAULT_MAX_SIZE) -> None:
        # предусловие:
        # max_size > 0
        #
        # постусловие:
        # создан новый пустой стек;
        # максимальное количество элементов равно max_size;
        # статусы push(), pop() и peek() установлены в *_NIL

        if max_size <= 0:
            raise ValueError("max_size must be positive")

        self._stack: list[T] = []
        self._max_size = max_size

        self._push_status = self.PUSH_NIL
        self._pop_status = self.POP_NIL
        self._peek_status = self.PEEK_NIL

        return None

    # команды

    def push(self, value: T) -> None:
        # предусловие:
        # количество элементов в стеке меньше максимально допустимого
        #
        # постусловие при выполнении предусловия:
        # value добавлен на вершину стека;
        # размер стека увеличен на 1;
        # статус push установлен в PUSH_OK
        #
        # если предусловие нарушено:
        # стек не изменяется;
        # статус push установлен в PUSH_ERR

        if self.size() >= self._max_size:
            self._push_status = self.PUSH_ERR

        if self.size() < self._max_size:
            self._stack.append(value)
            self._push_status = self.PUSH_OK

        return None

    def pop(self) -> None:
        # предусловие:
        # стек не пустой
        #
        # постусловие при выполнении предусловия:
        # верхний элемент удалён из стека;
        # размер стека уменьшен на 1;
        # статус pop установлен в POP_OK
        #
        # если предусловие нарушено:
        # стек не изменяется;
        # статус pop установлен в POP_ERR

        if self.size() == 0:
            self._pop_status = self.POP_ERR

        if self.size() > 0:
            self._stack.pop()
            self._pop_status = self.POP_OK

        return None

    def clear(self) -> None:
        # предусловие:
        # отсутствует
        #
        # постусловие:
        # из стека удалены все элементы;
        # size() == 0;
        # максимальный размер стека не изменился;
        # статусы push(), pop() и peek() установлены в *_NIL

        self._stack.clear()

        self._push_status = self.PUSH_NIL
        self._pop_status = self.POP_NIL
        self._peek_status = self.PEEK_NIL

        return None

    # запросы

    def peek(self) -> Optional[T]:
        # предусловие:
        # стек не пустой
        #
        # результат при выполнении предусловия:
        # возвращён верхний элемент стека;
        # сам стек не изменяется;
        # статус peek установлен в PEEK_OK
        #
        # если предусловие нарушено:
        # возвращается None;
        # стек не изменяется;
        # статус peek установлен в PEEK_ERR

        result: Optional[T] = None

        if self.size() == 0:
            self._peek_status = self.PEEK_ERR

        if self.size() > 0:
            result = self._stack[-1]
            self._peek_status = self.PEEK_OK

        return result

    def size(self) -> int:
        # предусловие:
        # отсутствует
        #
        # результат:
        # возвращено текущее количество элементов в стеке;
        # состояние стека не изменяется

        result = len(self._stack)

        return result

    def max_size(self) -> int:
        # предусловие:
        # отсутствует
        #
        # результат:
        # возвращено максимально допустимое количество элементов;
        # состояние стека не изменяется

        result = self._max_size

        return result

    # запросы статусов

    def get_push_status(self) -> int:
        # предусловие:
        # отсутствует
        #
        # результат:
        # возвращён статус последнего вызова push():
        # PUSH_NIL, PUSH_OK или PUSH_ERR;
        # состояние стека не изменяется

        result = self._push_status

        return result

    def get_pop_status(self) -> int:
        # предусловие:
        # отсутствует
        #
        # результат:
        # возвращён статус последнего вызова pop():
        # POP_NIL, POP_OK или POP_ERR;
        # состояние стека не изменяется

        result = self._pop_status

        return result

    def get_peek_status(self) -> int:
        # предусловие:
        # отсутствует
        #
        # результат:
        # возвращён статус последнего вызова peek():
        # PEEK_NIL, PEEK_OK или PEEK_ERR;
        # состояние стека не изменяется

        result = self._peek_status

        return result




class Node:

    def __init__(self, v):
        self.value = v
        self.next = None

class LinkedList:

    def __init__(self):
        self.pointer = None

    # commands
    # предусловие - список не пуст
    # постусловие если предусловие соблюдается - поинтер указывает на первый элемент
    # если предусловие не соблюдается - никаких изменений, head_status = HEAD_ERR
    # д

    def head(self) -> None:
        cur = self.pointer
