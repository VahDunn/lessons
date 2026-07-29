from linked_list_2 import LinkedList2 as BaseLinkedList2, Node


class LinkedList2(BaseLinkedList2):

    def _first_node(self):
        return self.head

    def _last_node(self):
        return self.tail

    def _before_first_node(self):
        return None

    def _after_last_node(self):
        return None

    def _insert_between(self, left, new_node, right):
        new_node.prev = left
        new_node.next = right

        if left is None:
            self.head = new_node
        else:
            left.next = new_node

        if right is None:
            self.tail = new_node
        else:
            right.prev = new_node

    def _unlink(self, node):
        left = node.prev
        right = node.next

        if left is None:
            self.head = right
        else:
            left.next = right

        if right is None:
            self.tail = left
        else:
            right.prev = left

        node.prev = None
        node.next = None

    def _reset(self):
        self.head = None
        self.tail = None

    def add_in_tail(self, item):
        self._insert_between(
            self._last_node(),
            item,
            self._after_last_node(),
        )

    def add_in_head(self, new_node):
        self._insert_between(
            self._before_first_node(),
            new_node,
            self._first_node(),
        )

    def find(self, val):
        current = self._first_node()
        end = self._after_last_node()

        while current is not end:
            if current.value == val:
                return current
            current = current.next

        return None

    def find_all(self, val):
        result = []
        current = self._first_node()
        end = self._after_last_node()

        while current is not end:
            if current.value == val:
                result.append(current)
            current = current.next

        return result

    def delete(self, val, all=False):
        current = self._first_node()
        end = self._after_last_node()

        while current is not end:
            next_node = current.next

            if current.value == val:
                self._unlink(current)

                if not all:
                    return

            current = next_node

    def clean(self):
        self._reset()

    def len(self):
        count = 0
        current = self._first_node()
        end = self._after_last_node()

        while current is not end:
            count += 1
            current = current.next

        return count

    def insert(self, afterNode, newNode):
        if afterNode is None:
            self.add_in_head(newNode)
            return

        self._insert_between(afterNode, newNode, afterNode.next)

    # Задание на курсе: 2
    # Задача: 2.10
    # Название: разворот списка
    # Временная сложность: O(n)
    # Пространственная сложность: O(1)
    def reverse(self):
        current = self._first_node()
        end = self._after_last_node()

        while current is not end:
            next_node = current.next
            self._unlink(current)
            self.add_in_head(current)
            current = next_node

    def _next_data_node(self, node):
        if node is None:
            return None

        next_node = node.next

        if next_node is self._after_last_node():
            return None

        return next_node

    # Задание на курсе: 2
    # Задача: 2.11
    # Название: проверка списка на наличие циклов
    # Временная сложность: O(n)
    # Пространственная сложность: O(1)
    def has_cycle(self):
        first = self._first_node()

        if first is self._after_last_node():
            return False

        slow = first
        fast = first

        while fast is not None:
            fast = self._next_data_node(fast)

            if fast is None:
                return False

            slow = self._next_data_node(slow)
            fast = self._next_data_node(fast)

            if slow is fast:
                return True

        return False

    # Задание на курсе: 2
    # Задача: 2.12
    # Название: сортировка списка
    # Временная сложность: O(n^2)
    # Пространственная сложность: O(1)
    def sort(self):
        current = self._first_node()
        end = self._after_last_node()

        if current is end:
            return

        current = current.next

        while current is not end:
            next_node = current.next
            position = current.prev

            if position.value <= current.value:
                current = next_node
                continue

            self._unlink(current)
            before_first = self._before_first_node()

            while (
                position is not before_first
                and position.value > current.value
            ):
                position = position.prev

            if position is before_first:
                self.add_in_head(current)
            else:
                self._insert_between(position, current, position.next)

            current = next_node

    # Задание на курсе: 2
    # Задача: 2.13
    # Название: слияние двух отсортированных списков
    # Временная сложность: O(n + m)
    # Пространственная сложность: O(n + m)
    def merge(self, other):
        result = type(self)()
        left = self._first_node()
        right = other._first_node()
        left_end = self._after_last_node()
        right_end = other._after_last_node()

        while left is not left_end and right is not right_end:
            if left.value <= right.value:
                result.add_in_tail(Node(left.value))
                left = left.next
            else:
                result.add_in_tail(Node(right.value))
                right = right.next

        while left is not left_end:
            result.add_in_tail(Node(left.value))
            left = left.next

        while right is not right_end:
            result.add_in_tail(Node(right.value))
            right = right.next

        return result


# Задание на курсе: 2
# Задача: 2.14
# Название: двунаправленный список с фиктивными узлами
# Временная сложность: O(1) для граничных вставок, O(n) для поиска и удаления
# Пространственная сложность: O(1) дополнительной памяти
class DummyNode(Node):
    def __init__(self):
        super().__init__(None)


class LinkedList2WithDummy(LinkedList2):
    def __init__(self):
        super().__init__()
        self.head = DummyNode()
        self.tail = DummyNode()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _first_node(self):
        return self.head.next

    def _last_node(self):
        return self.tail.prev

    def _before_first_node(self):
        return self.head

    def _after_last_node(self):
        return self.tail

    @staticmethod
    def _insert_between(left, new_node, right):
        left.next = new_node
        new_node.prev = left
        new_node.next = right
        right.prev = new_node

    @staticmethod
    def _unlink(node):
        node.prev.next = node.next
        node.next.prev = node.prev
        node.prev = None
        node.next = None

    def _reset(self):
        self.head.next = self.tail
        self.tail.prev = self.head


# Рефлексия
# Самой сложной снова оказалась сортировка. О(n^2), немного печально. Зато почитал про merge sort.
# С Dummy узлом действительно проще/удобнее. На доп задания отнаследовался, удобнее.
# Merge, reverse просто несложные, а has cycles я где-то видел что через 2 указателя решается :)
