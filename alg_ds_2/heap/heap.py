class Heap:
    def __init__(self):
        self.HeapArray = []
        self.size = 0

    def _left(self, i):  return 2 * i + 1
    def _right(self, i): return 2 * i + 2
    def _parent(self, i): return (i - 1) // 2

    def _sift_up(self, i):
        if i == 0:
            return
        p = self._parent(i)
        if self.HeapArray[p] < self.HeapArray[i]:
            self.HeapArray[p], self.HeapArray[i] = self.HeapArray[i], self.HeapArray[p]
            self._sift_up(p)

    def _sift_down(self, i):
        l, r = self._left(i), self._right(i)
        largest = i
        if l < self.size and self.HeapArray[l] > self.HeapArray[largest]:
            largest = l
        if r < self.size and self.HeapArray[r] > self.HeapArray[largest]:
            largest = r
        if largest != i:
            self.HeapArray[i], self.HeapArray[largest] = self.HeapArray[largest], self.HeapArray[i]
            self._sift_down(largest)

    def MakeHeap(self, a, depth):
        cap = 2 ** (depth + 1) - 1
        self.HeapArray = [None] * cap
        self.size = min(len(a), cap)
        self.HeapArray[:self.size] = a[:self.size]
        for i in range(self.size // 2 - 1, -1, -1):
            self._sift_down(i)
        return self.HeapArray

    def Add(self, key):
        if self.size == len(self.HeapArray):
            return False
        self.HeapArray[self.size] = key
        self.size += 1
        self._sift_up(self.size - 1)
        return True

    def GetMax(self):
        if self.size == 0:
            return -1
        top = self.HeapArray[0]
        self.size -= 1
        self.HeapArray[0] = self.HeapArray[self.size]
        self.HeapArray[self.size] = None
        if self.size > 0:
            self._sift_down(0)
        return top
