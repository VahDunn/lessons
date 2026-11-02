
# 1. Наследование вариаций

# Функциональная вариация

class Notification:
    def send(self, message: str) -> None:
        print(f"Notification: {message}")


class EmailNotification(Notification):
    def send(self, message: str) -> None:
        print(f"Email: {message}")


notification: Notification = EmailNotification()
notification.send("Hello")  # Email: Hello


# Вариация типа

class Animal:
    pass


class Cat(Animal):
    pass


class AnimalFactory:
    def create(self) -> Animal:
        return Animal()


class CatFactory(AnimalFactory):
    def create(self) -> Cat:
        return Cat()

factory: AnimalFactory = CatFactory()
animal = factory.create()


# 2. Наследование с конкретизацией


class Storage(ABC):

    @abstractmethod
    def save(self, data: str) -> None:
        ...

class FileStorage(Storage):

    def save(self, data: str) -> None:
        print(f"Save to file: {data}")


storage: Storage = FileStorage()
storage.save("hello")


# 3. Структурное наследование

# Iterable — дополнительное автономное свойство класса


class Vector[T](Iterable[T]):

    def __init__(self, items: list[T]):
        self.items = items

    def __iter__(self) -> Iterator[T]:
        return iter(self.items)


vector = Vector([1, 2, 3])

for item in vector:
    print(item)