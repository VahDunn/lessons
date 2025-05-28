package main

import (
	"errors"
	"io"
	"os"
)

// Задание 5 - функция с обращением очереди - с созданием временного слайса, в который выгружается вся очередь,
// а потом загружается обратно с другого конца - написана для очереди из основного варианта
func (q *Queue[T]) Reverse() {
	if q.size <= 1 {
		return
	}

	stack := make([]T, 0, q.size)
	for q.size > 0 {
		val, _ := q.Dequeue()
		stack = append(stack, val)
	}

	for i := len(stack) - 1; i >= 0; i-- {
		q.Enqueue(stack[i])
	}
}

// Задание 3 - вращение очереди по кругу на N элементов (в любую сторону)
func RotateQueue[T any](q *Queue[T], n int) {
	if q.Size() == 0 {
		return
	}

	n = n % q.Size()
	if n < 0 {
		n += q.Size()
	}

	for i := 0; i < n; i++ {
		if val, err := q.Dequeue(); err == nil {
			q.Enqueue(val)
		}
	}
}

// Stack реализация - из-за особенностей реализации мы получаем сложность O(n)
// для операции извлечения когда выходной стек пуст, потому что придется все элементы перекладывать.
// Такая операция не будет проходить слишком часто, поэтому амортизировання сложность будет ниже, но
// "чистая реализация" выглядит лучше.
// Затрудняюсь представить, зачем может быть нужна такая реализация, кроме демонстрации
type Stack[T any] struct {
	items []T
}

func (s *Stack[T]) Push(item T) {
	s.items = append(s.items, item)
}

func (s *Stack[T]) Pop() (T, error) {
	if len(s.items) == 0 {
		var zero T
		return zero, errors.New("stack is empty")
	}
	item := s.items[len(s.items)-1]
	s.items = s.items[:len(s.items)-1]
	return item, nil
}

func (s *Stack[T]) Size() int {
	return len(s.items)
}

// Задание 4 - реализация очереди на двух стеках
type Queue[T any] struct {
	inStack  Stack[T]
	outStack Stack[T]
}

func (q *Queue[T]) Enqueue(item T) {
	q.inStack.Push(item)
}

func (q *Queue[T]) Dequeue() (T, error) {
	// Если выходной стек пуст, перекладываем элементы из входного
	if q.outStack.Size() == 0 {
		for q.inStack.Size() > 0 {
			item, _ := q.inStack.Pop()
			q.outStack.Push(item)
		}
	}

	return q.outStack.Pop()
}

func (q *Queue[T]) Size() int {
	return q.inStack.Size() + q.outStack.Size()
}

// Задание 6 - циклическая очередь через статический массив (то есть нужна проерка полная/неполная)
// через 2 указателя - один указывает на начало очереди, второй - на конец
// если размер очереди становится равным 0, указатели сбрасываются
// Также здесь, как и в обычной круговой очереди, используется остаток деления емкости очереди на индекс для
// зацикливания

type CircularQueue[T any] struct {
	data     []T
	front    int
	rear     int
	size     int
	capacity int
}

func NewCircularQueue[T any](capacity int) *CircularQueue[T] {
	return &CircularQueue[T]{
		data:     make([]T, capacity),
		front:    -1,
		rear:     -1,
		size:     0,
		capacity: capacity,
	}
}

func (q *CircularQueue[T]) IsEmpty() bool {
	return q.size == 0
}

func (q *CircularQueue[T]) IsFull() bool {
	return q.size == q.capacity
}

func (q *CircularQueue[T]) Enqueue(item T) error {
	if q.IsFull() {
		return errors.New("queue is full")
	}

	if q.IsEmpty() {
		q.front = 0
	}

	q.rear = (q.rear + 1) % q.capacity
	q.data[q.rear] = item
	q.size++
	return nil
}

func (q *CircularQueue[T]) Dequeue() (T, error) {
	var zero T
	if q.IsEmpty() {
		return zero, errors.New("queue is empty")
	}

	item := q.data[q.front]
	if q.front == q.rear {
		q.front = -1
		q.rear = -1
	} else {
		q.front = (q.front + 1) % q.capacity
	}
	q.size--
	return item, nil
}

func (q *CircularQueue[T]) Peek() (T, error) {
	var zero T
	if q.IsEmpty() {
		return zero, errors.New("queue is empty")
	}
	return q.data[q.front], nil
}
