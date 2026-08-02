class Node:

    def __init__(self, value):
        self.value = value
        self.prev = None
        self.next = None


class OrderedList:

    # Задание на курсе: 7
    # Задача: 1
    # Название: создание упорядоченного списка
    def __init__(self, asc):
        self.head = None
        self.tail = None
        self.__ascending = asc

    # Задание на курсе: 7
    # Задача: 2
    # Название: сравнение числовых значений
    # Временная сложность: O(1)
    # Пространственная сложность: O(1)
    def compare(self, v1, v2):
        if v1 < v2:
            return -1

        if v1 > v2:
            return 1

        return 0

    # Задание на курсе: 7
    # Задача: 3
    # Название: добавление значения с сохранением порядка
    # Временная сложность: O(n)
    # Пространственная сложность: O(1)
    def add(self, value):
        new_node = Node(value)
        current = self.head

        while current is not None:
            comparison = self.compare(current.value, value)
            should_insert_before = (
                self.__ascending and comparison >= 0
                or not self.__ascending and comparison <= 0
            )

            if should_insert_before:
                self._insert_before(current, new_node)
                return

            current = current.next

        self._append_node(new_node)

    # Задание на курсе: 7
    # Задача: 4
    # Название: удаление первого элемента по значению
    # Временная сложность: O(n)
    # Пространственная сложность: O(1)
    def delete(self, val):
        node = self.find(val)

        if node is None:
            return

        self._unlink_node(node)

    # Задание на курсе: 7
    # Задача: 6
    # Название: поиск элемента с ранним прерыванием
    # Временная сложность: O(n)
    # Пространственная сложность: O(1)
    def find(self, val):
        current = self.head

        while current is not None:
            comparison = self.compare(current.value, val)

            if comparison == 0:
                return current

            passed_value = (
                self.__ascending and comparison > 0
                or not self.__ascending and comparison < 0
            )

            if passed_value:
                return None

            current = current.next

        return None

    # Название: очистка списка и изменение направления сортировки
    # Временная сложность: O(1)
    # Пространственная сложность: O(1)
    def clean(self, asc):
        self.head = None
        self.tail = None
        self.__ascending = asc

    # Название: количество элементов в списке
    # Временная сложность: O(n)
    # Пространственная сложность: O(1)
    def len(self):
        count = 0
        current = self.head

        while current is not None:
            count += 1
            current = current.next

        return count

    # Название: получение всех узлов списка
    # Временная сложность: O(n)
    # Пространственная сложность: O(n)
    def get_all(self):
        nodes = []
        current = self.head

        while current is not None:
            nodes.append(current)
            current = current.next

        return nodes

    def _is_ascending(self):
        return self.__ascending

    def _append_node(self, node):
        node.prev = self.tail
        node.next = None

        if self.tail is None:
            self.head = node
            self.tail = node
            return

        self.tail.next = node
        self.tail = node

    def _insert_before(self, current, new_node):
        previous = current.prev
        new_node.prev = previous
        new_node.next = current
        current.prev = new_node

        if previous is None:
            self.head = new_node
            return

        previous.next = new_node

    def _unlink_node(self, node):
        previous = node.prev
        following = node.next

        if previous is None:
            self.head = following

        if previous is not None:
            previous.next = following

        if following is None:
            self.tail = previous

        if following is not None:
            following.prev = previous

        node.prev = None
        node.next = None


# Задание на курсе: 7
# Задача: 5
# Название: упорядоченный список строк
class OrderedStringList(OrderedList):

    # Временная сложность: O(k)
    # Пространственная сложность: O(k)
    def compare(self, v1, v2):
        return super().compare(v1.strip(), v2.strip())


