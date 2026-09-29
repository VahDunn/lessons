class Base:
    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name


class Inherit(Base):
    def __init__(self, name: str, age: int):
        super().__init__(name)
        self._age = age

    @property
    def age(self) -> int:
        return self._age

    def name_list(self) -> list[str]:
        return list(self._name)


obj = Inherit("Walter", 50)

print(obj.name)
print(obj.age)
print(obj.name_list())

# Наследник расширяет поведение родителя, сохраняя уже имеющееся.
# Собственно, здесь же иллюстрирован и полиморфизм - вызывающий код вызывает методы
# наследника как методы родителя.

class Engine:
    def __init__(self, power: int):
        self.power = power

    def start(self) -> str:
        return "Engine started"


class Car:
    def __init__(self, power: int):
        self._engine = Engine(power)

    def start(self) -> str:
        return self._engine.start()

# В случае с композицией получается part-of, то есть Engine инициализируется
# непосредственно при инициализации класса Car. И в то же время, что я зачастую понимал
# как "тоже композицию" является агрегацией. Отличие, вроде бы, в том, что
# в случае композиции жизненный цикл зависимого объекта подчинен основному (whole-part), а в случае
# с агрегацией - это два изначально независимых объекта, один из которых has-a другой.
# Местный полиморфизм нужно задавать более явно - "прокидывать" методы внутреннего класса во внешний.
