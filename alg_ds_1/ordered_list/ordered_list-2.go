package main

import (
	"constraints"
	"errors"
	"fmt"
	"os"
)

func (l *OrderedList[T]) RemoveDuplicates() {
	if l.head == nil {
		return
	}

	current := l.head
	for current != nil && current.next != nil {
		if l.Compare(current.value, current.next.value) == 0 {
			nodeToRemove := current.next
			current.next = nodeToRemove.next
			if nodeToRemove.next != nil {
				nodeToRemove.next.prev = current
			} else {
				l.tail = current
			}
		} else {
			current = current.next
		}
	}
}

func (l *OrderedList[T]) Merge(other *OrderedList[T]) error {
	if l._ascending != other._ascending {
		return errors.New("списки должны иметь одинаковый порядок сортировки")
	}

	if other.head == nil {
		return nil
	}

	if l.head == nil {
		l.head = other.head
		l.tail = other.tail
		return nil
	}

	merged := &OrderedList[T]{}
	merged.Clear(l._ascending)

	current1 := l.head
	current2 := other.head
	for current1 != nil && current2 != nil {
		if (l._ascending && l.Compare(current1.value, current2.value) <= 0) ||
			(!l._ascending && l.Compare(current1.value, current2.value) >= 0) {
			merged.Add(current1.value)
			current1 = current1.next
		} else {
			merged.Add(current2.value)
			current2 = current2.next
		}
	}

	for current1 != nil {
		merged.Add(current1.value)
		current1 = current1.next
	}

	for current2 != nil {
		merged.Add(current2.value)
		current2 = current2.next
	}

	l.head = merged.head
	l.tail = merged.tail

	return nil
}

func (l *OrderedList[T]) Contains(sublist []T) bool {
	if len(sublist) == 0 {
		return true
	}

	if l.head == nil {
		return false
	}

	current := l.head
	for current != nil {
		if l.Compare(current.value, sublist[0]) == 0 {
			if l.checkSublistFromNode(current, sublist) {
				return true
			}
		}
		current = current.next
	}
	return false
}

func (l *OrderedList[T]) checkSublistFromNode(startNode *Node[T], sublist []T) bool {
	current := startNode
	for i := 0; i < len(sublist); i++ {
		if current == nil || l.Compare(current.value, sublist[i]) != 0 {
			return false
		}
		current = current.next
	}
	return true
}

func (l *OrderedList[T]) FindMostFrequent() (T, int, error) {
	var zeroValue T
	if l.head == nil {
		return zeroValue, 0, errors.New("список пуст")
	}

	maxCount := 0
	maxValue := zeroValue
	currentCount := 1
	currentValue := l.head.value

	current := l.head.next
	for current != nil {
		if l.Compare(current.value, currentValue) == 0 {
			currentCount++
		} else {
			if currentCount > maxCount {
				maxCount = currentCount
				maxValue = currentValue
			}
			currentValue = current.value
			currentCount = 1
		}
		current = current.next
	}

	if currentCount > maxCount {
		maxCount = currentCount
		maxValue = currentValue
	}

	return maxValue, maxCount, nil
}

type IndexedOrderedList[T constraints.Ordered] struct {
	OrderedList[T]
	nodes []*Node[T]
}

func (l *IndexedOrderedList[T]) Add(item T) {
	l.OrderedList.Add(item)
	l.rebuildIndex()
}

func (l *IndexedOrderedList[T]) Delete(item T) {
	l.OrderedList.Delete(item)
	l.rebuildIndex()
}

func (l *IndexedOrderedList[T]) Clear(asc bool) {
	l.OrderedList.Clear(asc)
	l.nodes = nil
}

func (l *IndexedOrderedList[T]) rebuildIndex() {
	count := l.Count()
	l.nodes = make([]*Node[T], 0, count)
	current := l.head
	for current != nil {
		l.nodes = append(l.nodes, current)
		current = current.next
	}
}

func (l *IndexedOrderedList[T]) FindIndex(item T) (int, error) {
	count := l.Count()
	if count == 0 {
		return -1, errors.New("список пуст")
	}

	left, right := 0, count-1

	for left <= right {
		mid := (left + right) / 2
		cmp := l.Compare(l.nodes[mid].value, item)

		if cmp == 0 {
			for mid > 0 && l.Compare(l.nodes[mid-1].value, item) == 0 {
				mid--
			}
			return mid, nil
		} else if (l._ascending && cmp < 0) || (!l._ascending && cmp > 0) {
			left = mid + 1
		} else {
			right = mid - 1
		}
	}

	return -1, errors.New("элемент не найден")
}

func (l *IndexedOrderedList[T]) GetByIndex(index int) (T, error) {
	var zeroValue T
	count := l.Count()
	if index < 0 || index >= count {
		return zeroValue, errors.New("индекс вне диапазона")
	}
	return l.nodes[index].value, nil
}

func (l *OrderedList[T]) ToSlice() []T {
	count := l.Count()
	result := make([]T, 0, count)
	current := l.head
	for current != nil {
		result = append(result, current.value)
		current = current.next
	}
	return result
}

func (l *OrderedList[T]) Print() {
	fmt.Print("Список: ")
	current := l.head
	for current != nil {
		fmt.Printf("%v ", current.value)
		current = current.next
	}
	fmt.Printf("(порядок: %t, количество: %d)\n", l._ascending, l.Count())
}

func NewOrderedList[T constraints.Ordered](ascending bool) *OrderedList[T] {
	list := &OrderedList[T]{}
	list.Clear(ascending)
	return list
}

func NewIndexedOrderedList[T constraints.Ordered](ascending bool) *IndexedOrderedList[T] {
	list := &IndexedOrderedList[T]{}
	list.Clear(ascending)
	return list
}
