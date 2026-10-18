# 1.
class A:
    def foo(self) -> None:
        print("A.foo")


class B(A):
    pass


b = B()
b.foo()  # A.foo

# 2
class A:
    def foo(self) -> None:
        print("A.foo")


class B(A):
    pass


b = B()
b.foo()  # метод всё равно доступен

# 3
class A:
    def _foo(self) -> None:
        print("A._foo")


class B(A):
    foo = A._foo


b = B()

b.foo()   # публичный интерфейс B
b._foo()  # технически тоже доступен

# 4
class A:
    def _foo(self) -> None:
        print("A._foo")


class B(A):
    pass