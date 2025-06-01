package main

import (
	"errors"
	"os"
	//	"fmt"
)

type Node[T any] struct {
	prev  *Node[T]
	next  *Node[T]
	value T
}

type Deque[T any] struct {
	head *Node[T]
	tail *Node[T]
	size int
}

func (d *Deque[T]) Size() int {
	return d.size
}

func (d *Deque[T]) AddFront(itm T) {
	n := Node[T]{value: itm}
	if d.head == nil {
		d.head = &n
		d.tail = &n
	} else {
		n.next = d.head
		d.head.prev = &n
		d.head = &n
	}
	d.size++
}

func (d *Deque[T]) AddTail(itm T) {
	n := Node[T]{value: itm}

	if d.head == nil {
		d.head = &n
		d.tail = &n
	} else {
		n.prev = d.tail
		d.tail.next = &n
		d.tail = &n
	}
	d.size++
}

func (d *Deque[T]) RemoveFront() (T, error) {
	var result T
	if d.Size() == 0 {
		return result, errors.New("deque is empty")
	}
	result = d.head.value
	d.head = d.head.next

	if d.head != nil {
		d.head.prev = nil
	} else {
		d.tail = nil
	}
	d.size--
	return result, nil
}

func (d *Deque[T]) RemoveTail() (T, error) {
	var result T
	if d.Size() == 0 {
		return result, errors.New("deque is empty")
	}
	result = d.tail.value
	d.tail = d.tail.prev
	if d.tail != nil {
		d.tail.next = nil
	} else {
		d.head = nil
	}
	d.size--
	return result, nil
}
