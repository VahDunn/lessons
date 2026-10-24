class Animal:
    def sound(self) -> str:
        return "animal"


class Cat(Animal):
    def sound(self) -> str:
        return "meow"


# Полиморфный вызов

animal: Animal = Cat()

# Статический тип переменной — Animal,
# реальный тип объекта — Cat.
#
# будет вызван Cat.sound(), а не Animal.sound().
print(animal.sound())

# 2. Ковариантный вызов

class Zoo:
    def print_animals(self, animals: Sequence[Animal]) -> None:
        for animal in animals:
            print(animal.sound())


cats: Sequence[Cat] = [
    Cat(),
    Cat(),
]

zoo = Zoo()

# Sequence ковариантен по своему типу-параметру ->
# Sequence[Cat] можно передать туда,
# где ожидается Sequence[Animal].
zoo.print_animals(cats)