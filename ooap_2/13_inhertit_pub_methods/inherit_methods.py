# 1.
# Поддерживается.

class A:
    def foo(self) -> None:
        print("A.foo")


class B(A):
    pass


b = B()
b.foo()  # A.foo


# 2. Штатно не поддерживается.
# В Python нельзя уменьшить видимость унаследованного метода.

class A:
    def foo(self) -> None:
        print("A.foo")


class B(A):
    pass


b = B()
b.foo()  # foo по-прежнему публично доступен


# 3.
# Можно реализовать, предоставив в B новый публичный метод,
# который вызывает унаследованный внутренний метод.

class A:
    def _foo(self) -> None:
        print("A._foo")


class B(A):
    def foo(self) -> None:
        self._foo()


b = B()
b.foo()  # публичный интерфейс B


# 4.
# Поддерживается по соглашению об именовании.

class A:
    def _foo(self) -> None:
        print("A._foo")


class B(A):
    pass


b = B()
b._foo()  # технически доступен, но считается внутренним методом