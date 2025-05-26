package main

import (
	"errors"
	"fmt"
	"os"
)

type BankArray[T any] struct {
	array    []T
	capacity int
	size     int
}

func NewBankArray[T any]() *BankArray[T] {
	return &BankArray[T]{
		array:    make([]T, 1),
		capacity: 1,
		size:     0,
	}
}

func (ba *BankArray[T]) Append(item T) {
	if ba.size == ba.capacity {
		newArray := make([]T, ba.capacity*2)
		copy(newArray, ba.array)
		ba.array = newArray
		ba.capacity *= 2
	}
	ba.array[ba.size] = item
	ba.size++
}

func (ba *BankArray[T]) Get(index int) (T, error) {
	var zero T
	if index < 0 || index >= ba.size {
		return zero, fmt.Errorf("index out of range")
	}
	return ba.array[index], nil
}

func (ba *BankArray[T]) Remove(index int) error {
	if index < 0 || index >= ba.size {
		return fmt.Errorf("index out of range")
	}
	copy(ba.array[index:], ba.array[index+1:ba.size])
	ba.size--

	if ba.size <= ba.capacity/4 {
		newCapacity := ba.capacity / 2
		if newCapacity < 1 {
			newCapacity = 1
		}
		newArray := make([]T, newCapacity)
		copy(newArray, ba.array[:ba.size])
		ba.array = newArray
		ba.capacity = newCapacity
	}
	return nil
}

type MultiArray[T any] struct {
	dimensions int
	shape      []int
	data       []T
}

func NewMultiArray[T any](dimensions int, shape ...int) (*MultiArray[T], error) {
	if dimensions != len(shape) {
		return nil, errors.New("dimensions count doesn't match shape length")
	}

	totalSize := 1
	for _, size := range shape {
		if size <= 0 {
			return nil, errors.New("dimension size must be positive")
		}
		totalSize *= size
	}

	return &MultiArray[T]{
		dimensions: dimensions,
		shape:      shape,
		data:       make([]T, totalSize),
	}, nil
}

func (ma *MultiArray[T]) Get(indices ...int) (T, error) {
	var zero T
	if len(indices) != ma.dimensions {
		return zero, errors.New("wrong number of indices")
	}

	index := 0
	stride := 1
	for i := ma.dimensions - 1; i >= 0; i-- {
		if indices[i] < 0 || indices[i] >= ma.shape[i] {
			return zero, fmt.Errorf("index %d out of range for dimension %d", indices[i], i)
		}
		index += indices[i] * stride
		stride *= ma.shape[i]
	}

	return ma.data[index], nil
}

func (ma *MultiArray[T]) Set(value T, indices ...int) error {
	if len(indices) != ma.dimensions {
		return errors.New("wrong number of indices")
	}

	index := 0
	stride := 1
	for i := ma.dimensions - 1; i >= 0; i-- {
		if indices[i] < 0 || indices[i] >= ma.shape[i] {
			return fmt.Errorf("index %d out of range for dimension %d", indices[i], i)
		}
		index += indices[i] * stride
		stride *= ma.shape[i]
	}

	ma.data[index] = value
	return nil
}

func (ma *MultiArray[T]) Resize(newShape ...int) error {
	if len(newShape) != ma.dimensions {
		return errors.New("wrong number of dimensions")
	}

	newTotalSize := 1
	for _, size := range newShape {
		if size <= 0 {
			return errors.New("dimension size must be positive")
		}
		newTotalSize *= size
	}

	newData := make([]T, newTotalSize)

	oldIndices := make([]int, ma.dimensions)
	for i := 0; i < len(ma.data); i++ {
		copyIndices := true
		for j := 0; j < ma.dimensions; j++ {
			if oldIndices[j] >= newShape[j] {
				copyIndices = false
				break
			}
		}

		if copyIndices {
			newIndex := 0
			stride := 1
			for k := ma.dimensions - 1; k >= 0; k-- {
				newIndex += oldIndices[k] * stride
				stride *= newShape[k]
			}
			newData[newIndex] = ma.data[i]
		}

		for j := ma.dimensions - 1; j >= 0; j-- {
			oldIndices[j]++
			if oldIndices[j] < ma.shape[j] {
				break
			}
			oldIndices[j] = 0
		}
	}

	ma.data = newData
	ma.shape = newShape
	return nil
}
