package main

import (
	"errors"
)

type Node struct {
	next  *Node
	value int
}

type LinkedList struct {
	head *Node
	tail *Node
}

func (l *LinkedList) AddInTail(item Node) {
	if l.head == nil {
		l.head = &item
	} else {
		l.tail.next = &item
		l.tail = &item
	}
}

func (l *LinkedList) Count() int {
	count := 0
	cur := l.head
	for cur != nil {
		cur = cur.next
		count = count + 1
	}
	return count
}

// error не nil, если узел не найден
func (l *LinkedList) Find(n int) (*Node, error) {
	if l.head == nil {
		return nil, errors.New("list is empty")
	}
	curr := l.head
	for curr != nil {
		if curr.value == n {
			return curr, nil
		}
		curr = curr.next
	}
	return nil, errors.New("node not found")
}

func (l *LinkedList) FindAll(n int) []*Node {
	var nodes []*Node
	curr := l.head
	for curr != nil {
		if curr.value == n {
			nodes = append(nodes, curr)
		}
		curr = curr.next
	}
	return nodes
}

func (l *LinkedList) Delete(n int, all bool) {
	if l.head == nil {
		return
	}
	for l.head != nil && l.head.value == n {
		l.head = l.head.next
		if !all {
			if l.head == nil {
				l.tail = nil
			}
			return
		}
	}
	prev := l.head
	if prev == nil {
		l.tail = nil
		return
	}
	curr := prev.next
	for curr != nil {
		if curr.value == n {
			prev.next = curr.next
			if curr == l.tail {
				l.tail = prev
			}
			if !all {
				return
			}
			curr = prev.next
		} else {
			prev = curr
			curr = prev.next
		}
	}
}

func (l *LinkedList) Insert(after *Node, add Node) {
	if l.head == nil {
		l.head = &add
	}
	next := after.next
	after.next = &add
	add.next = next
}

func (l *LinkedList) InsertFirst(first Node) {
	first.next = l.head
	l.head = &first
}

func (l *LinkedList) Clean() {
	l.head = nil
	l.tail = nil
}
