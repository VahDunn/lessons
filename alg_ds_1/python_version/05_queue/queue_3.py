from queue import Queue
from queue_2 import (
    CircularQueue,
    Queue as ReversibleQueue,
    TwoStackQueue,
    rotate_queue,
)


def test_size():
    queue = Queue()

    assert queue.size() == 0

    queue.enqueue(1)
    queue.enqueue('2')
    assert queue.size() == 2

    queue.dequeue()
    assert queue.size() == 1


def test_enqueue():
    queue = Queue()

    queue.enqueue(1)
    queue.enqueue('2')
    queue.enqueue(3.14)

    assert queue.size() == 3
    assert queue.queue == [3.14, '2', 1]


def test_dequeue():
    queue = Queue()

    assert queue.dequeue() is None

    queue.enqueue(1)
    queue.enqueue('2')
    queue.enqueue(3.14)

    assert queue.dequeue() == 1
    assert queue.dequeue() == '2'
    assert queue.dequeue() == 3.14
    assert queue.size() == 0
    assert queue.dequeue() is None



def test_rotate_queue():
    queue = Queue()
    rotate_queue(queue, 3)
    assert queue.size() == 0

    for item in (1, 2, 3, 4, 5):
        queue.enqueue(item)

    rotate_queue(queue, 2)

    assert queue.size() == 5
    assert [queue.dequeue() for _ in range(5)] == [3, 4, 5, 1, 2]


def test_two_stack_queue():
    queue = TwoStackQueue()

    assert queue.dequeue() is None

    queue.enqueue(1)
    queue.enqueue(2)
    assert queue.dequeue() == 1

    queue.enqueue(3)
    assert queue.size() == 2
    assert queue.dequeue() == 2
    assert queue.dequeue() == 3
    assert queue.dequeue() is None


def test_reverse_queue():
    queue = ReversibleQueue()
    queue.reverse()
    assert queue.size() == 0

    for item in (1, 2, 3, 4):
        queue.enqueue(item)

    queue.reverse()

    assert queue.size() == 4
    assert [queue.dequeue() for _ in range(4)] == [4, 3, 2, 1]


def test_circular_queue_wraps_around():
    queue = CircularQueue(3)
    queue.enqueue(1)
    queue.enqueue(2)
    queue.enqueue(3)

    assert queue.dequeue() == 1
    queue.enqueue(4)

    assert queue.size() == 3
    assert queue.dequeue() == 2
    assert queue.dequeue() == 3
    assert queue.dequeue() == 4
    assert queue.dequeue() is None


def test_circular_queue_is_full():
    queue = CircularQueue(2)

    assert queue.is_full() is False

    queue.enqueue(1)
    queue.enqueue(2)
    assert queue.is_full() is True

    queue.enqueue(3)
    assert queue.size() == 2
    assert queue.dequeue() == 1
    assert queue.dequeue() == 2
