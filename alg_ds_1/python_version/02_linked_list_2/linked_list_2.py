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
        if self.head is None:
            self.head = item
            item.prev = None
            item.next = None
        else:
            self.tail.next = item
            item.prev = self.tail
        self.tail = item

    # Задание на курсе: 2
    # Задача: 2.1
    # Название: поиск первого узла по значению
    # Временная сложность: O(n)
    # Пространственная сложность: O(1)
    def find(self, val):
        current = self.head

        while current is not None:
            if current.value == val:
                return current
            current = current.next

        return None

    # Задание на курсе: 2
    # Задача: 2.2
    # Название: поиск всех узлов по значению
    # Временная сложность: O(n)
    # Пространственная сложность: O(n)
    def find_all(self, val):
        result = []
        current = self.head

        while current is not None:
            if current.value == val:
                result.append(current)
            current = current.next

        return result

    # Задание на курсе: 2
    # Задачи: 2.3, 2.4
    # Название: удаление первого или всех узлов по значению
    # Временная сложность: O(n)
    # Пространственная сложность: O(1)
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
                if not all:
                    return
            current = next_node
    # Задание на курсе: 2
    # Задача: 2.7
    # Название: очистка списка
    # Временная сложность: O(1)
    # Пространственная сложность: O(1)
    def clean(self):
        self.head = None
        self.tail = None

    # Задание на курсе: 2
    # Задача: 2.8
    # Название: вычисление длины списка
    # Временная сложность: O(n)
    # Пространственная сложность: O(1)
    def len(self):
        count = 0
        current = self.head

        while current is not None:
            count += 1
            current = current.next

        return count

    # Задание на курсе: 2
    # Задача: 2.5
    # Название: вставка узла после заданного узла
    # Временная сложность: O(1)
    # Пространственная сложность: O(1)
    def insert(self, afterNode, newNode):
        if afterNode is None:
            self.add_in_head(newNode)
            return
        newNode.prev = afterNode
        newNode.next = afterNode.next
        if afterNode.next is None:
            self.tail = newNode
        else:
            afterNode.next.prev = newNode
        afterNode.next = newNode

    # Задание на курсе: 2
    # Задача: 2.6
    # Название: добавление узла в голову списка
    # Временная сложность: O(1)
    # Пространственная сложность: O(1)
    def add_in_head(self, newNode):
        newNode.prev = None
        newNode.next = self.head
        if self.head is None:
            self.tail = newNode
        else:
            self.head.prev = newNode
        self.head = newNode
