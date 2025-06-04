package main

import (
	"constraints"
	"errors"
	"fmt"
	"os"
	"reflect"
)

// 8. Удаление всех дубликатов из упорядоченного списка
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
			l.count--
		} else {
			current = current.next
		}
	}
}

// 9. Слияние двух упорядоченных списков
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
		l.count = other.count
		return nil
	}

	// Создаем новый список с результатом слияния
	merged := &OrderedList[T]{}
	merged.Clear(l._ascending)

	current1 := l.head
	current2 := other.head

	// Сливаем списки, поддерживая порядок
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

	// Добавляем оставшиеся элементы
	for current1 != nil {
		merged.Add(current1.value)
		current1 = current1.next
	}

	for current2 != nil {
		merged.Add(current2.value)
		current2 = current2.next
	}

	// Заменяем текущий список результатом слияния
	l.head = merged.head
	l.tail = merged.tail
	l.count = merged.count

	return nil
}

// 10. Проверка наличия упорядоченного под-списка
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
	for i := 0; i < len(sublist) && current != nil; i++ {
		if l.Compare(current.value, sublist[i]) != 0 {
			return false
		}
		current = current.next
	}
	return current != nil || len(sublist) <= l.getDistanceToEnd(startNode)
}

func (l *OrderedList[T]) getDistanceToEnd(node *Node[T]) int {
	count := 0
	current := node
	for current != nil {
		count++
		current = current.next
	}
	return count
}

// 11. Поиск наиболее часто встречающегося значения
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

// 12. Поиск индекса элемента за O(log N) - требует изменения структуры
// Для эффективного поиска по индексу добавим массив указателей на узлы
type IndexedOrderedList[T constraints.Ordered] struct {
	OrderedList[T]
	nodes []*Node[T] // массив указателей на узлы для быстрого доступа по индексу
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
	l.nodes = make([]*Node[T], 0, l.count)
	current := l.head
	for current != nil {
		l.nodes = append(l.nodes, current)
		current = current.next
	}
}

// Бинарный поиск индекса элемента за O(log N)
func (l *IndexedOrderedList[T]) FindIndex(item T) (int, error) {
	if l.count == 0 {
		return -1, errors.New("список пуст")
	}

	left, right := 0, l.count-1

	for left <= right {
		mid := (left + right) / 2
		cmp := l.Compare(l.nodes[mid].value, item)

		if cmp == 0 {
			// Найден элемент, но может быть не первое вхождение
			// Ищем первое вхождение
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

// Получение элемента по индексу за O(1)
func (l *IndexedOrderedList[T]) GetByIndex(index int) (T, error) {
	var zeroValue T
	if index < 0 || index >= l.count {
		return zeroValue, errors.New("индекс вне диапазона")
	}
	return l.nodes[index].value, nil
}

// Утилитарные функции для демонстрации и отладки
func (l *OrderedList[T]) ToSlice() []T {
	result := make([]T, 0, l.count)
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
	fmt.Printf("(порядок: %t, количество: %d)\n", l._ascending, l.count)
}

// Создание нового упорядоченного списка
func NewOrderedList[T constraints.Ordered](ascending bool) *OrderedList[T] {
	list := &OrderedList[T]{}
	list.Clear(ascending)
	return list
}

// Создание нового индексированного упорядоченного списка
func NewIndexedOrderedList[T constraints.Ordered](ascending bool) *IndexedOrderedList[T] {
	list := &IndexedOrderedList[T]{}
	list.Clear(ascending)
	return list
}
