class Queue:
    def __init__(self):
        self._items = []

    def put(self, item) -> None:
        self._items.append(item)

    def get(self):
        return self._items.pop(0)

    def size(self) -> int:
        return len(self._items)


class TaskQueue(Queue):
    def get_next_task(self):
        return self.get()


tasks = TaskQueue()
tasks.put("build")
tasks.put("test")

print(tasks.size())
print(tasks.get_next_task())

# TaskQueue наследует готовую реализацию хранения элементов
# и методы put, get и size.

class Calculator:
    def add(self, a: int, b: int) -> int:
        return a + b


class CalculatorTest(unittest.TestCase):
    def setUp(self):
        self.calculator = Calculator()

    def test_add(self):
        result = self.calculator.add(2, 3)

        self.assertEqual(result, 5)


# Здесь конкретный тесткейс наследует инфраструктуру общего,
# используя ее для тестирования конкретного сценария
