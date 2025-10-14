class Heap:
    def __init__(self):
        self.a = []
        self.size = 0

    def _left(self, i):  return 2 * i + 1
    def _right(self, i): return 2 * i + 2
    def _parent(self, i): return (i - 1) // 2

    def _sift_up(self, i):
        if i == 0:
            return
        p = self._parent(i)
        if self.a[p] < self.a[i]:
            self.a[p], self.a[i] = self.a[i], self.a[p]
            self._sift_up(p)

    def _sift_down(self, i):
        l, r = self._left(i), self._right(i)
        largest = i
        if l < self.size and self.a[l] > self.a[largest]:
            largest = l
        if r < self.size and self.a[r] > self.a[largest]:
            largest = r
        if largest != i:
            self.a[i], self.a[largest] = self.a[largest], self.a[i]
            self._sift_down(largest)

    def MakeHeap(self, arr, depth):
        cap = 2 ** (depth + 1) - 1
        self.a = [None] * cap
        self.size = min(len(arr), cap)
        self.a[:self.size] = arr[:self.size]
        for i in range(self.size // 2 - 1, -1, -1):
            self._sift_down(i)
        return self.a

    def Add(self, key):
        if self.size == len(self.a):
            return False
        self.a[self.size] = key
        self.size += 1
        self._sift_up(self.size - 1)
        return True

    def GetMax(self):
        if self.size == 0:
            return -1
        top = self.a[0]
        self.size -= 1
        self.a[0] = self.a[self.size]
        self.a[self.size] = None
        if self.size > 0:
            self._sift_down(0)
        return top
