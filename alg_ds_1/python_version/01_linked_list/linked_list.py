class Node:

    def __init__(self, v):
        self.value = v
        self.next = None

class LinkedList:

    def __init__(self):
        self.head = None
        self.tail = None

    def add_in_tail(self, item):
        if self.head is None:
            self.head = item
        else:
            self.tail.next = item
        self.tail = item

    def print_all_nodes(self):
        node = self.head
        while node != None:
            print(node.value)
            node = node.next

    def find(self, val):
        node = self.head
        while node is not None:
            if node.value == val:
                return node
            node = node.next
        return None

    # Задание на курсе: 1
    # Задача: 1.4
    # Название: поиск всех узлов по значению
    # Временная сложность: O(n)
    # Пространственная сложность: O(n)
    def find_all(self, val):
        res = []
        if self.head is None:
            return res
        cur = self.head
        while cur:
            if cur.value == val:
                res.append(cur)
            cur = cur.next
        return res

    # Задание на курсе: 1
    # Задачи: 1.1, 1.2
    # Название: удаление первого или всех узлов по значению
    # Временная сложность: O(n)
    # Пространственная сложность: O(1)
    def delete(self, val, all=False):
        while self.head is not None and self.head.value == val:
            self.head = self.head.next
            if not all:
                if self.head is None:
                    self.tail = None
                return

        if self.head is None:
            self.tail = None
            return

        cur = self.head

        while cur.next is not None:
            if cur.next.value == val:
                if cur.next is self.tail:
                    self.tail = cur
                cur.next = cur.next.next

                if not all:
                    return
            else:
                cur = cur.next

    # Задание на курсе: 1
    # Задача: 1.3
    # Название: очистка списка
    # Временная сложность: O(1)
    # Пространственная сложность: O(1)
    def clean(self):
        self.head = None
        self.tail = None

    # Задание на курсе: 1
    # Задача: 1.5
    # Название: вычисление длины списка
    # Временная сложность: O(n)
    # Пространственная сложность: O(1)
    def len(self):
        count = 0
        cur = self.head
        while cur is not None:
            count += 1
            cur = cur.next
        return count

    # Задание на курсе: 1
    # Задача: 1.6
    # Название: вставка узла
    # Временная сложность: O(1)
    # Пространственная сложность: O(1)
    def insert(self, afterNode, newNode):
        if afterNode is None:
            newNode.next = self.head
            self.head = newNode
        else:
            newNode.next = afterNode.next
            afterNode.next = newNode

        if newNode.next is None:
            self.tail = newNode
