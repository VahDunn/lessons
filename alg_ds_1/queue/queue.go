package main

import (
	"errors"
	"os"
	//	"fmt" включите если используете
)

// Задание 1 - очередь, реализована на основе связного списка.
type Node[T any] struct {
	next *Node[T]
	val  T
}
type Queue[T any] struct {
	head *Node[T]
	tail *Node[T]
	size int
}

// Сложность О(1)
func (q *Queue[T]) Size() int {
	return q.size
}

// Сложность О(1)
func (q *Queue[T]) Dequeue() (T, error) {
	var res T
	if q.size == 0 {
		return res, errors.New("empty queue")
	}
	res = q.head.val
	q.head = q.head.next
	if q.head == nil {
		q.tail = nil
	}
	q.size--
	return res, nil
}

// Сложность О(1)
func (q *Queue[T]) Enqueue(itm T) {
	n := &Node[T]{val: itm}
	if q.head == nil {
		q.head = n
	} else {
		q.tail.next = n
	}
	q.tail = n
	q.size++
}
