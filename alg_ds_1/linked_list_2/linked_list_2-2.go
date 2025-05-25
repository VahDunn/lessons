package main

func (l *LinkedList2) Reverse() {
	if l.head == nil || l.head.next == nil {
		return
	}

	current := l.head
	var prev *Node = nil

	l.head, l.tail = l.tail, l.head

	for current != nil {
		next := current.next
		current.next = prev
		current.prev = next
		prev = current
		current = next
	}
}

func (l *LinkedList2) HasCycle() bool {
	return l.hasCycleForward() || l.hasCycleBackward()
}

func (l *LinkedList2) hasCycleForward() bool {
	slow, fast := l.head, l.head
	for fast != nil && fast.next != nil {
		slow = slow.next
		fast = fast.next.next
		if slow == fast {
			return true
		}
	}
	return false
}

func (l *LinkedList2) hasCycleBackward() bool {
	slow, fast := l.tail, l.tail
	for fast != nil && fast.prev != nil {
		slow = slow.prev
		fast = fast.prev.prev
		if slow == fast {
			return true
		}
	}
	return false
}

func (l *LinkedList2) Sort() {
	if l.head == nil || l.head.next == nil {
		return
	}

	var sorted *Node = nil
	current := l.head

	for current != nil {
		next := current.next

		if sorted == nil || sorted.value >= current.value {
			current.next = sorted
			current.prev = nil
			if sorted != nil {
				sorted.prev = current
			}
			sorted = current
		} else {
			temp := sorted
			for temp.next != nil && temp.next.value < current.value {
				temp = temp.next
			}
			current.next = temp.next
			current.prev = temp
			if temp.next != nil {
				temp.next.prev = current
			}
			temp.next = current
		}

		current = next
	}

	l.head = sorted

	if l.head != nil {
		l.tail = l.head
		for l.tail.next != nil {
			l.tail = l.tail.next
		}
	} else {
		l.tail = nil
	}
}

func (l *LinkedList2) MergeSortedLists(other *LinkedList2) *LinkedList2 {
	result := &LinkedList2{}
	a := l.head
	b := other.head

	for a != nil && b != nil {
		if a.value <= b.value {
			result.AddInTail(Node{value: a.value})
			a = a.next
		} else {
			result.AddInTail(Node{value: b.value})
			b = b.next
		}
	}

	for a != nil {
		result.AddInTail(Node{value: a.value})
		a = a.next
	}

	for b != nil {
		result.AddInTail(Node{value: b.value})
		b = b.next
	}

	return result
}

// Основные алгоритмы проблем не вызвали, над дополнительными сидел подольше. С проверкой на циклы решил поделить метод,
// по сути это две одинаково работающие фнукции, просто направленность разная. Можно было бы в один, но так показалось
// проще. Про слияние особо сказать нечего, кроме того, что оно реализовано через создание нового списка, что, возможно,
// не оптимально. Сортировка вставкой.
