package main

import (
	"errors"
	"os"
	"reflect"
)

type Node struct {
	next  *Node
	prev  *Node
	value int
}

type LinkedList2 struct {
	head *Node
	tail *Node
}

func (l *LinkedList2) AddInTail(item Node) {
	if l.head == nil {
		l.head = &item
		l.head.next = nil
		l.head.prev = nil
	} else {
		l.tail.next = &item
		item.prev = l.tail
	}

	l.tail = &item
	l.tail.next = nil
}

func (l *LinkedList2) Count() int {
	count := 0
	cur := l.head
	for cur != nil {
		count++
		cur = cur.next
	}
	return count
}

// error не nil, если узел не найден
func (l *LinkedList2) Find(n int) (Node, error) {
	curr := l.head
	for curr != nil {
		if curr.value == n {
			return *curr, nil
		}
		curr = curr.next
	}
	return Node{}, errors.New("node not found")
}

func (l *LinkedList2) FindAll(n int) []Node {
	var nodes []Node
	curr := l.head
	for curr != nil {
		if curr.value == n {
			nodes = append(nodes, *curr)
		}
		curr = curr.next
	}
	return nodes
}

func (l *LinkedList2) Delete(n int, all bool) {
	if l.head == nil {
		return
	}
	current := l.head
	for current != nil {
		if current.value == n {
			if current.prev != nil {
				current.prev.next = current.next
			} else {
				l.head = current.next
			}
			if current.next != nil {
				current.next.prev = current.prev
			} else {
				l.tail = current.prev
			}
			if !all {
				return
			}
		}
		current = current.next
	}
}

func (l *LinkedList2) Insert(after *Node, add Node) {
	newNode := &add

	if after == nil {
		newNode.next = l.head
		newNode.prev = nil
		if l.head != nil {
			l.head.prev = newNode
		}
		l.head = newNode
		if l.tail == nil {
			l.tail = newNode
		}
		return
	}
	newNode.prev = after
	newNode.next = after.next

	after.next = newNode

	if newNode.next != nil {
		newNode.next.prev = newNode
	} else {
		l.tail = newNode
	}
}

func (l *LinkedList2) InsertFirst(first Node) {
	if l.head == nil {
		l.head = &first
		l.tail = &first
		return
	}
	first.next = l.head
	l.head.prev = &first
	l.head = &first
}

func (l *LinkedList2) Clean() {
	l.head = nil
	l.tail = nil
}
