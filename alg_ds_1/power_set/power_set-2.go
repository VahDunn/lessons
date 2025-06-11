package main

import (
	"constraints"
	//"fmt"
	"os"
	"strconv"
)

// 4. Декартово произведение множеств
type Pair[T constraints.Ordered] struct {
	First  T
	Second T
}

func (s *PowerSet[T]) CartesianProductSlice(set2 PowerSet[T]) []Pair[T] {
	var result []Pair[T]
	for elem1 := range s.dict {
		for elem2 := range set2.dict {
			result = append(result, Pair[T]{First: elem1, Second: elem2})
		}
	}
	return result
}

// 5. Пересечение трёх и более множеств
func IntersectionOfMany[T constraints.Ordered](sets ...*PowerSet[T]) PowerSet[T] {
	if len(sets) < 3 {
		panic("IntersectionOfMany requires at least 3 sets")
	}

	result := Init[T]()

	// Начинаем с копии первого множества
	for elem := range sets[0].dict {
		result.Put(elem)
	}

	// Последовательно пересекаем с остальными множествами
	for i := 1; i < len(sets); i++ {
		temp := Init[T]()
		for elem := range result.dict {
			if sets[i].Get(elem) {
				temp.Put(elem)
			}
		}
		result = temp
	}

	return result
}

// 6. Реализация мультимножества (Bag)
type Bag[T constraints.Ordered] struct {
	elements map[T]int
}

func NewBag[T constraints.Ordered]() *Bag[T] {
	return &Bag[T]{
		elements: make(map[T]int),
	}
}

// Добавление элемента в мультимножество
func (b *Bag[T]) Add(value T, count int) {
	if count <= 0 {
		return
	}
	b.elements[value] += count
}

// Удаление одного экземпляра элемента
func (b *Bag[T]) RemoveOne(value T) bool {
	if count, exists := b.elements[value]; exists {
		if count > 1 {
			b.elements[value]--
		} else {
			delete(b.elements, value)
		}
		return true
	}
	return false
}

// Получение списка всех элементов с их частотами
func (b *Bag[T]) GetElementsWithFrequencies() map[T]int {
	result := make(map[T]int)
	for elem, count := range b.elements {
		result[elem] = count
	}
	return result
}

// Получение количества вхождений элемента
func (b *Bag[T]) GetCount(value T) int {
	return b.elements[value]
}

// Удаление всех экземпляров элемента
func (b *Bag[T]) RemoveAll(value T) bool {
	if _, exists := b.elements[value]; exists {
		delete(b.elements, value)
		return true
	}
	return false
}

// Размер мультимножества (общее количество элементов с учётом кратности)
func (b *Bag[T]) TotalSize() int {
	total := 0
	for _, count := range b.elements {
		total += count
	}
	return total
}

// Уникальный размер (количество уникальных элементов)
func (b *Bag[T]) UniqueSize() int {
	return len(b.elements)
}
