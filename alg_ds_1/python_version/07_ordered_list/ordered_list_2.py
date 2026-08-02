from ordered_list import Node, OrderedList as BaseOrderedList


class OrderedList(BaseOrderedList):

    def __init__(self, asc):
        super().__init__(asc)
        self._index = []

    def add(self, value):
        super().add(value)
        self._rebuild_index()

    def delete(self, val):
        super().delete(val)
        self._rebuild_index()

    def clean(self, asc):
        super().clean(asc)
        self._index = []

    # Задание на курсе: 7
    # Задача: 8
    # Название: удаление всех дубликатов
    # Временная сложность: O(n)
    # Пространственная сложность: O(n) для вспомогательного индекса
    def delete_duplicates(self):
        current = self.head

        while current is not None and current.next is not None:
            if self.compare(current.value, current.next.value) != 0:
                current = current.next
                continue

            self._unlink_node(current.next)

        self._rebuild_index()

    # Задание на курсе: 7
    # Задача: 9
    # Название: слияние двух упорядоченных списков
    # Временная сложность: O(n + m)
    # Пространственная сложность: O(n + m)
    def merge(self, other):
        if self._is_ascending() != other._is_ascending():
            raise ValueError('Lists must have the same sort order')

        result = OrderedList(self._is_ascending())
        left = self.head
        right = other.head

        while left is not None and right is not None:
            if self._should_take_left(left.value, right.value):
                result._append_indexed_value(left.value)
                left = left.next
                continue
            result._append_indexed_value(right.value)
            right = right.next

        while left is not None:
            result._append_indexed_value(left.value)
            left = left.next

        while right is not None:
            result._append_indexed_value(right.value)
            right = right.next

        return result

    # Задание на курсе: 7
    # Задача: 10
    # Название: проверка наличия упорядоченного подсписка
    # Временная сложность: O(n * m)
    # Пространственная сложность: O(1)
    def contains_sublist(self, sublist):
        if sublist.head is None:
            return True

        if self._is_ascending() != sublist._is_ascending():
            return False

        current = self.head

        while current is not None:
            comparison = self.compare(current.value, sublist.head.value)

            if comparison == 0 and self._matches_sublist(current, sublist.head):
                return True

            passed_value = (
                self._is_ascending() and comparison > 0
                or not self._is_ascending() and comparison < 0
            )

            if passed_value:
                return False

            current = current.next

        return False

    # Задание на курсе: 7
    # Задача: 11
    # Название: поиск наиболее часто встречающегося значения
    # Временная сложность: O(n)
    # Пространственная сложность: O(1)
    def find_most_frequent(self):
        if self.head is None:
            return None

        most_frequent = self.head.value
        maximum_count = 1
        current_value = self.head.value
        current_count = 1
        current = self.head.next

        while current is not None:
            if self.compare(current.value, current_value) == 0:
                current_count += 1
                current = current.next
                continue

            if current_count > maximum_count:
                most_frequent = current_value
                maximum_count = current_count

            current_value = current.value
            current_count = 1
            current = current.next

        if current_count > maximum_count:
            most_frequent = current_value

        return most_frequent

    # Задание на курсе: 7
    # Задача: 12
    # Название: поиск индекса элемента
    # Временная сложность: O(log n)
    # Пространственная сложность: O(1) для вызова, O(n) для индекса
    def find_index(self, value):
        left = 0
        right = len(self._index)

        while left < right:
            middle = (left + right) // 2
            comparison = self.compare(self._index[middle].value, value)
            middle_before_value = (
                self._is_ascending() and comparison < 0
                or not self._is_ascending() and comparison > 0
            )

            if middle_before_value:
                left = middle + 1
                continue

            right = middle

        if left == len(self._index):
            return -1

        if self.compare(self._index[left].value, value) != 0:
            return -1

        return left

    def _matches_sublist(self, current, expected):
        while expected is not None:
            if current is None:
                return False

            if self.compare(current.value, expected.value) != 0:
                return False

            current = current.next
            expected = expected.next

        return True

    def _append_indexed_value(self, value):
        node = Node(value)
        self._append_node(node)
        self._index.append(node)

    def _should_take_left(self, left_value, right_value):
        comparison = self.compare(left_value, right_value)

        if self._is_ascending():
            return comparison <= 0

        return comparison >= 0

    def _rebuild_index(self):
        self._index = self.get_all()

# Рефлексия по заданию 5
# Вращение сделал ровно так же, с вталкиванием/выталкиванием.
# С перемещением во второй стек только если он пустой неочевидна (лично для меня),
# но я поэтому и запомнил :)
# И в целом прием разворачивания не-массивов через стек кажется удобным.
# С круговой очередью описание (и задача) кажутся намного сложнее, чем по факту есть.
# А код написал - и норм.
