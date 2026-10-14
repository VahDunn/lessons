from typing import Final, final


class General(object):
    pass


class Any(General):
    pass


class Animal(Any):
    def sound(self) -> str:
        raise NotImplementedError


class Cat(Animal):
    def sound(self) -> str:
        return "meow"


class Dog(Animal):
    def sound(self) -> str:
        return "woof"


@final
class NoneValue(Cat, Dog):
    """Нижний тип иерархии — аналог отсутствия значения."""

    def sound(self) -> str:
        raise RuntimeError("Operation on Void")


Void: Final[NoneValue] = NoneValue()


def find_cat(found: bool) -> Cat:
    if found:
        return Cat()

    return Void


def find_dog(found: bool) -> Dog:
    if found:
        return Dog()

    return Void


cat: Cat = find_cat(False)
dog: Dog = find_dog(False)

if cat is Void:
    print("Кот не найден")
else:
    print(cat.sound())

if dog is Void:
    print("Собака не найдена")
else:
    print(dog.sound())
