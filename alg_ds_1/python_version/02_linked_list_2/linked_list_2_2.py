class Node:

    def __init__(self, v):
        self.value = v
        self.prev = None
        self.next = None


class LinkedList2:

    def __init__(self):
        self.head = None
        self.tail = None

    def add_in_tail(self, item):
        item.prev = self.tail
        item.next = None

        if self.tail is None:
            self.head = item
        else:
            self.tail.next = item

        self.tail = item

    def add_in_head(self, new_node):
        new_node.prev = None
        new_node.next = self.head

        if self.head is None:
            self.tail = new_node
        else:
            self.head.prev = new_node

        self.head = new_node

    def find(self, val):
        current = self.head

        while current is not None:
            if current.value == val:
                return current
            current = current.next

        return None

    def find_all(self, val):
        result = []
        current = self.head

        while current is not None:
            if current.value == val:
                result.append(current)
            current = current.next

        return result

    def delete(self, val, all=False):
        current = self.head

        while current is not None:
            next_node = current.next

            if current.value == val:
                if current.prev is None:
                    self.head = current.next
                else:
                    current.prev.next = current.next

                if current.next is None:
                    self.tail = current.prev
                else:
                    current.next.prev = current.prev

                current.prev = None
                current.next = None

                if not all:
                    return

            current = next_node

    def clean(self):
        self.head = None
        self.tail = None

    def len(self):
        count = 0
        current = self.head

        while current is not None:
            count += 1
            current = current.next

        return count

    def insert(self, after_node, new_node):
        if after_node is None:
            self.add_in_head(new_node)
            return

        new_node.prev = after_node
        new_node.next = after_node.next

        if after_node.next is None:
            self.tail = new_node
        else:
            after_node.next.prev = new_node

        after_node.next = new_node

    # Задание на курсе: 2
    # Задача: 2.10
    # Название: разворот списка
    # Временная сложность: O(n)
    # Пространственная сложность: O(1)
    def reverse(self):
        current = self.head

        while current is not None:
            next_node = current.next
            current.next = current.prev
            current.prev = next_node
            current = next_node

        self.head, self.tail = self.tail, self.head

    # Задание на курсе: 2
    # Задача: 2.11
    # Название: проверка списка на наличие циклов
    # Временная сложность: O(n)
    # Пространственная сложность: O(1)
    def has_cycle(self):
        slow = self.head
        fast = self.head

        while fast is not None and fast.next is not None:
            slow = slow.next
            fast = fast.next.next

            if slow is fast:
                return True

        return False

    # Задание на курсе: 2
    # Задача: 2.12
    # Название: сортировка списка
    # Временная сложность: O(n^2)
    # Пространственная сложность: O(1)
    def sort(self):
        if self.head is None or self.head.next is None:
            return

        sorted_head = None
        current = self.head

        while current is not None:
            next_node = current.next

            if sorted_head is None or current.value < sorted_head.value:
                current.prev = None
                current.next = sorted_head

                if sorted_head is not None:
                    sorted_head.prev = current

                sorted_head = current
            else:
                position = sorted_head

                while (
                    position.next is not None
                    and position.next.value <= current.value
                ):
                    position = position.next

                current.next = position.next
                current.prev = position

                if position.next is not None:
                    position.next.prev = current

                position.next = current

            current = next_node

        self.head = sorted_head
        self.tail = self.head

        while self.tail.next is not None:
            self.tail = self.tail.next

    # Задание на курсе: 2
    # Задача: 2.13
    # Название: слияние двух отсортированных списков
    # Временная сложность: O(n + m)
    # Пространственная сложность: O(n + m)
    def merge(self, other):
        result = LinkedList2()
        left = self.head
        right = other.head

        while left is not None and right is not None:
            if left.value <= right.value:
                result.add_in_tail(Node(left.value))
                left = left.next
            else:
                result.add_in_tail(Node(right.value))
                right = right.next

        while left is not None:
            result.add_in_tail(Node(left.value))
            left = left.next

        while right is not None:
            result.add_in_tail(Node(right.value))
            right = right.next

        return result


# Задание на курсе: 2
# Задача: 2.14
# Название: двунаправленный список с фиктивными узлами
class LinkedList2WithDummy:

    def __init__(self):
        self.head = Node(None)
        self.tail = Node(None)
        self.head.next = self.tail
        self.tail.prev = self.head

    def add_in_tail(self, item):
        item.prev = self.tail.prev
        item.next = self.tail
        self.tail.prev.next = item
        self.tail.prev = item

    def add_in_head(self, new_node):
        new_node.prev = self.head
        new_node.next = self.head.next
        self.head.next.prev = new_node
        self.head.next = new_node

    def find(self, val):
        current = self.head.next

        while current is not self.tail:
            if current.value == val:
                return current
            current = current.next

        return None

    def find_all(self, val):
        result = []
        current = self.head.next

        while current is not self.tail:
            if current.value == val:
                result.append(current)
            current = current.next

        return result

    def delete(self, val, all=False):
        current = self.head.next

        while current is not self.tail:
            next_node = current.next

            if current.value == val:
                current.prev.next = current.next
                current.next.prev = current.prev
                current.prev = None
                current.next = None

                if not all:
                    return

            current = next_node

    def clean(self):
        self.head.next = self.tail
        self.tail.prev = self.head

    def len(self):
        count = 0
        current = self.head.next

        while current is not self.tail:
            count += 1
            current = current.next

        return count

    def insert(self, after_node, new_node):
        if after_node is None:
            self.add_in_head(new_node)
            return

        new_node.prev = after_node
        new_node.next = after_node.next
        after_node.next.prev = new_node
        after_node.next = new_node

    def reverse(self):
        first = self.head.next
        last = self.tail.prev
        current = first

        while current is not self.tail:
            next_node = current.next
            current.next = current.prev
            current.prev = next_node
            current = next_node

        if first is self.tail:
            return

        self.head.next = last
        last.prev = self.head
        self.tail.prev = first
        first.next = self.tail

    def has_cycle(self):
        slow = self.head.next
        fast = self.head.next

        while fast is not self.tail and fast.next is not self.tail:
            slow = slow.next
            fast = fast.next.next

            if slow is fast:
                return True

        return False

    def sort(self):
        current = self.head.next

        if current is self.tail:
            return

        current = current.next

        while current is not self.tail:
            next_node = current.next
            position = current.prev

            if position.value <= current.value:
                current = next_node
                continue

            current.prev.next = current.next
            current.next.prev = current.prev

            while position is not self.head and position.value > current.value:
                position = position.prev

            current.prev = position
            current.next = position.next
            position.next.prev = current
            position.next = current
            current = next_node

    def merge(self, other):
        result = LinkedList2WithDummy()
        left = self.head.next
        right = other.head.next

        while left is not self.tail and right is not other.tail:
            if left.value <= right.value:
                result.add_in_tail(Node(left.value))
                left = left.next
            else:
                result.add_in_tail(Node(right.value))
                right = right.next

        while left is not self.tail:
            result.add_in_tail(Node(left.value))
            left = left.next

        while right is not other.tail:
            result.add_in_tail(Node(right.value))
            right = right.next

        return result


# Рефлексия
# Самой сложной снова оказалась сортировка. O(n^2), немного печально.
# Зато почитал про merge sort.
# С dummy-узлами действительно проще работать с границами списка.
