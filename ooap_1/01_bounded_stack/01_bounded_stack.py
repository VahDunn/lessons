from typing import Generic, Optional, TypeVar


T = TypeVar("T")


class BoundedStack(Generic[T]):
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
        if self.size() >= self._max_size:
            self._push_status = self.PUSH_ERR

        if self.size() < self._max_size:
            self._stack.append(value)
            self._push_status = self.PUSH_OK

        return None

    def pop(self) -> None:
        if self.size() == 0:
            self._pop_status = self.POP_ERR

        if self.size() > 0:
            self._stack.pop()
            self._pop_status = self.POP_OK

        return None

    def clear(self) -> None:
        self._stack.clear()

        self._push_status = self.PUSH_NIL
        self._pop_status = self.POP_NIL
        self._peek_status = self.PEEK_NIL

        return None

    # запросы

    def peek(self) -> Optional[T]:
        result: Optional[T] = None

        if self.size() == 0:
            self._peek_status = self.PEEK_ERR

        if self.size() > 0:
            result = self._stack[-1]
            self._peek_status = self.PEEK_OK

        return result

    def size(self) -> int:
        result = len(self._stack)
        return result

    def max_size(self) -> int:
        result = self._max_size
        return result

    # запросы статусов

    def get_push_status(self) -> int:
        result = self._push_status
        return result

    def get_pop_status(self) -> int:
        result = self._pop_status
        return result

    def get_peek_status(self) -> int:
        result = self._peek_status
        return result
