class Node:

    def __init__(self, v):
        self.value = v
        self.prev = None
        self.next = None


class DummyNode(Node):

    def __init__(self):
        super().__init__(None)


class LinkedList2:

    def __init__(self):
        self.head = None
        self.tail = None

    def add_in_tail(self, item):
        if self.head is None:
            self.head = item
            item.prev = None
            item.next = None
        else:
            self.tail.next = item
            item.prev = self.tail
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

            if current.value != val:
                current = next_node
                continue

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
            self.add_in_tail(new_node)
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
        if self.head is None:
            return

        before_first = Node(None)
        after_last = Node(None)
        before_first.next = after_last
        after_last.prev = before_first
        current = self.head

        while current is not None:
            next_node = current.next
            position = before_first.next

            while position is not after_last and position.value <= current.value:
                position = position.next

            current.prev = position.prev
            current.next = position
            position.prev.next = current
            position.prev = current
            current = next_node

        self.head = before_first.next
        self.tail = after_last.prev
        self.head.prev = None
        self.tail.next = None

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
            if right.value < left.value:
                result.add_in_tail(Node(right.value))
                right = right.next
                continue

            result.add_in_tail(Node(left.value))
            left = left.next

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
        self.head = DummyNode()
        self.tail = DummyNode()
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

        while not isinstance(current, DummyNode):
            if current.value == val:
                return current
            current = current.next

        return None

    def find_all(self, val):
        result = []
        current = self.head.next

        while not isinstance(current, DummyNode):
            if current.value == val:
                result.append(current)
            current = current.next

        return result

    def delete(self, val, all=False):
        current = self.head.next

        while not isinstance(current, DummyNode):
            next_node = current.next

            if current.value != val:
                current = next_node
                continue

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

        while not isinstance(current, DummyNode):
            count += 1
            current = current.next

        return count

    def insert(self, after_node, new_node):
        if after_node is None:
            self.add_in_tail(new_node)
            return

        new_node.prev = after_node
        new_node.next = after_node.next
        after_node.next.prev = new_node
        after_node.next = new_node

    def reverse(self):
        first = self.head.next

        if isinstance(first, DummyNode):
            return

        last = self.tail.prev
        current = first

        while not isinstance(current, DummyNode):
            next_node = current.next
            current.next = current.prev
            current.prev = next_node
            current = next_node

        self.head.next = last
        last.prev = self.head
        self.tail.prev = first
        first.next = self.tail

    def has_cycle(self):
        slow = self.head.next
        fast = self.head.next

        while (
            not isinstance(fast, DummyNode)
            and not isinstance(fast.next, DummyNode)
        ):
            slow = slow.next
            fast = fast.next.next

            if slow is fast:
                return True

        return False

    def sort(self):
        current = self.head.next

        if isinstance(current, DummyNode):
            return

        current = current.next

        while not isinstance(current, DummyNode):
            next_node = current.next
            position = current.prev

            if position.value <= current.value:
                current = next_node
                continue

            current.prev.next = current.next
            current.next.prev = current.prev

            while (
                not isinstance(position, DummyNode)
                and position.value > current.value
            ):
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

        while (
            not isinstance(left, DummyNode)
            and not isinstance(right, DummyNode)
        ):
            if right.value < left.value:
                result.add_in_tail(Node(right.value))
                right = right.next
                continue

            result.add_in_tail(Node(left.value))
            left = left.next

        while not isinstance(left, DummyNode):
            result.add_in_tail(Node(left.value))
            left = left.next

        while not isinstance(right, DummyNode):
            result.add_in_tail(Node(right.value))
            right = right.next

        return result


# Рефлексия
# Самой сложной снова оказалась сортировка. О(n^2), немного печально. Зато почитал про merge sort.
# С Dummy узлом действительно проще/удобнее. На доп задания отнаследовался, удобнее.
# Merge, reverse просто несложные, а has cycles я где-то видел что через 2 указателя решается :)
