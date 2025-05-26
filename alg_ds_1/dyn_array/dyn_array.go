package main

import (
	"fmt"
	"os"
)

const (
	increaseArraySize = 2
	decreaseArraySize = 1.5

	decreasePercent = 0.5
)

type DynArray[T any] struct {
	count    int
	capacity int
	array    []T
}

func (da *DynArray[T]) Init() {
	da.count = 0
	da.MakeArray(16)
}

func (da *DynArray[T]) MakeArray(sz int) {
	if sz < 16 {
		sz = 16
	}
	var arr = make([]T, sz)
	if da.count != 0 {
		copy(arr, da.array)
	}
	da.capacity = sz
	da.array = arr
}

func (da *DynArray[T]) Insert(itm T, index int) error {
	if index > da.count || index < 0 {
		return fmt.Errorf("index '%d' out of range", index)
	}

	if index == da.count {
		da.Append(itm)
		return nil
	}
	if da.capacity == da.count {
		da.MakeArray(da.capacity * increaseArraySize)
	}

	for i := da.count; i > index; i-- {
		if i != 0 {
			da.array[i] = da.array[i-1]
		}
	}

	da.array[index] = itm
	da.count++
	return nil
}

func (da *DynArray[T]) Remove(index int) error {
	if index > da.count || index < 0 {
		return fmt.Errorf("index '%d' out of range", index)
	}
	for i := index; i < da.count-1; i++ {
		da.array[i] = da.array[i+1]
	}
	da.count--
	decreasedCapacity := int(float64(da.capacity) * decreasePercent)
	if da.count < decreasedCapacity {
		newSize := int(float64(da.capacity) / decreaseArraySize)

		da.MakeArray(newSize)
	}
	return nil
}

func (da *DynArray[T]) Append(itm T) {
	if da.capacity == da.count {
		da.MakeArray(da.capacity * increaseArraySize)
	}

	da.array[da.count] = itm
	da.count++
}

func (da *DynArray[T]) GetItem(index int) (T, error) {
	var result T
	if index >= da.count || index < 0 {
		return result, fmt.Errorf("index out of range %d", index)
	}
	result = da.array[index]
	return result, nil
}

//Оценка сложности:
//Insert - В худшем случае (вставка в начало) - O(n), так как нужно сдвинуть все элементы
//Remove: В худшем случае (удаление из начала) - O(n), так как нужно сдвинуть все элементы
