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

func (l1 *LinkedList) AddInTail(item *Node) {
	item.next = nil
	if l1.head == nil {
		l1.head = item
		l1.tail = item
	} else {
		l1.tail.next = item
		l1.tail = item
	}
}

func (l1 *LinkedList) Count() int {
	count := 0
	cur := l1.head
	for cur != nil {
		count++
		cur = cur.next
	}
	return count
}

func (l1 *LinkedList) Find(n int) (*Node, error) {
	curr := l1.head
	for curr != nil {
		if curr.value == n {
			return curr, nil
		}
		curr = curr.next
	}
	return nil, errors.New("node not found")
}

func (l1 *LinkedList) FindAll(n int) []*Node {
	var nodes []*Node
	curr := l1.head
	for curr != nil {
		if curr.value == n {
			nodes = append(nodes, curr)
		}
		curr = curr.next
	}
	return nodes
}

func (l1 *LinkedList) Delete(n int, all bool) {
	if l1.head == nil {
		return
	}
	// Удаление из начала списка
	for l1.head != nil && l1.head.value == n {
		l1.head = l1.head.next
		if l1.head == nil {
			l1.tail = nil
			return
		}
		if !all {
			if l1.head == nil {
				l1.tail = nil
			}
			return
		}
	}
	// Удаление из "середины"
	prev := l1.head
	if prev == nil {
		l1.tail = nil
		return
	}
	curr := prev.next
	for curr != nil {
		if curr.value == n {
			prev.next = curr.next
			if curr == l1.tail {
				l1.tail = prev
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

func (l1 *LinkedList) Insert(after *Node, add *Node) {
	if l1.head == nil {
		l1.head = add
		l1.tail = add
		add.next = nil
		return
	}
	add.next = after.next
	after.next = add
	if l1.tail == after {
		l1.tail = add
	}
}

func (l1 *LinkedList) InsertFirst(first *Node) {
	first.next = l1.head
	l1.head = first
	if l1.tail == nil {
		l1.tail = first
	}
}

func (l1 *LinkedList) Clean() {
	l1.head = nil
	l1.tail = nil
}
