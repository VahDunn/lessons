from typing import Final, TypeVar, final


T = TypeVar("T", bound="General")


class General(object):

    @staticmethod
    @final
    def assignment_attempt(
        target_type: type[T],
        source: object,
    ) -> T | "NoneValue":
        if isinstance(source, target_type):
            return source

        return Void


class Any(General):
    pass


class Animal(Any):
    pass


class Cat(Animal):
    pass


class Dog(Animal):
    pass


@final
class NoneValue(Cat, Dog):
    pass


Void: Final[NoneValue] = NoneValue()

# Пример

source: Any = Cat()

target: Animal = Any.assignment_attempt(Animal, source)

# Cat совместим с Animal:
print(target is Void)
# False


source = Any()

target = Any.assignment_attempt(Animal, source)

# Any не является Animal, поэтому получаем Void:
print(target is Void)
# True