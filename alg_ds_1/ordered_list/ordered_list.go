package main

import (
	"constraints"
	"errors"
	"os"
	"strings"
)

type Node[T constraints.Ordered] struct {
	prev  *Node[T]
	next  *Node[T]
	value T
}

type OrderedList[T constraints.Ordered] struct {
	head       *Node[T]
	tail       *Node[T]
	_ascending bool
	count      int
}

func (l *OrderedList[T]) Count() int {
	return l.count
}

func (l *OrderedList[T]) Add(item T) {
	l.count++
	newNode := Node[T]{value: item}
	if l.head == nil {
		l.head = &newNode
		l.tail = &newNode
		return
	}
	n := l.head
	for n != nil {
		if (l._ascending && l.Compare(n.value, item) >= 0) || (!l._ascending && l.Compare(n.value, item) <= 0) {
			l.addToMiddle(n, &newNode)
			return
		}
		n = n.next
	}
	newNode.prev = l.tail
	l.tail.next = &newNode
	l.tail = &newNode
}

func (l *OrderedList[T]) addToMiddle(n, newNode *Node[T]) {
	if n == l.head {
		newNode.next = l.head
		l.head.prev = newNode
		l.head = newNode
	} else {
		newNode.prev = n.prev
		n.prev.next = newNode
		n.prev = newNode

		newNode.next = n
	}
}

func (l *OrderedList[T]) Find(n T) (Node[T], error) {
	node := l.head
	for node != nil {
		if (l._ascending && l.Compare(node.value, n) > 0) || (!l._ascending && l.Compare(node.value, n) < 0) {
			return Node[T]{value: n, next: nil, prev: nil}, errors.New("node not found")
		}
		if l.Compare(node.value, n) == 0 {
			return *node, nil
		}
		node = node.next
	}
	return Node[T]{value: n, next: nil, prev: nil}, errors.New("node not found")
}

func (l *OrderedList[T]) Delete(n T) {
	node := l.head

	for node != nil {
		if l.Compare(node.value, n) != 0 {
			node = node.next
			continue
		}

		if node == l.head {
			l.head = l.head.next
		}

		if node.prev != nil {
			node.prev.next = node.next
		}

		if node.next != nil {
			node.next.prev = node.prev
		} else {
			l.tail = node.prev
		}

		if l.head == nil {
			l.tail = nil
		}

		l.count--
		return
	}
}

func (l *OrderedList[T]) Clear(asc bool) {
	l._ascending = asc
	l.head, l.tail = nil, nil
	l.count = 0
}

func (l *OrderedList[T]) Compare(v1 T, v2 T) int {
	val1 := interface{}(v1)
	val2 := interface{}(v2)

	s1, ok1 := val1.(string)
	s2, ok2 := val2.(string)

	if ok1 && ok2 {
		return l.CompareStrings(s1, s2)
	}

	if v1 < v2 {
		return -1
	}
	if v1 > v2 {
		return +1
	}
	return 0
}

func (l *OrderedList[T]) CompareStrings(s1, s2 string) int {
	s1 = strings.TrimSpace(s1)
	s2 = strings.TrimSpace(s2)
	if s1 < s2 {
		return -1
	}
	if s1 > s2 {
		return 1
	}
	return 0
}
