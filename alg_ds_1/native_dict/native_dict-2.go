package main

import (
	"errors"
	// "fmt"
	"os"
	"sort"
	"strconv"
)

// Задание 5 - Упорядоченный словарь, хранящий ключи в отсортированном виде
type OrderedDictionary[T any] struct {
	keys   []string
	values []T
}

func InitOrderedDict[T any]() OrderedDictionary[T] {
	return OrderedDictionary[T]{
		keys:   make([]string, 0),
		values: make([]T, 0),
	}
}

// Бинарный поиск
func (od *OrderedDictionary[T]) findKey(key string) (int, bool) {
	i := sort.SearchStrings(od.keys, key)
	if i < len(od.keys) && od.keys[i] == key {
		return i, true
	}
	return i, false
}

func (od *OrderedDictionary[T]) Put(key string, value T) {
	idx, found := od.findKey(key)
	if found {
		od.values[idx] = value
	} else {
		od.keys = append(od.keys, "")
		od.values = append(od.values, value)
		copy(od.keys[idx+1:], od.keys[idx:])
		copy(od.values[idx+1:], od.values[idx:])

		od.keys[idx] = key
		od.values[idx] = value
	}
}

func (od *OrderedDictionary[T]) Get(key string) (T, error) {
	var result T
	idx, found := od.findKey(key)
	if !found {
		return result, errors.New("ключ не найден")
	}
	return od.values[idx], nil
}

func (od *OrderedDictionary[T]) Remove(key string) error {
	idx, found := od.findKey(key)
	if !found {
		return errors.New("ключ не найден")
	}
	od.keys = append(od.keys[:idx], od.keys[idx+1:]...)
	od.values = append(od.values[:idx], od.values[idx+1:]...)
	return nil
}

func (od *OrderedDictionary[T]) IsKey(key string) bool {
	_, found := od.findKey(key)
	return found
}

/*
По сути, это надстройка над словарем, которая позволяет более эффективно проводить операции
над ключами.
Сложность операций:
- Put: O(n) (из-за вставки в отсортированный массив)
- Get: O(log n) (бинарный поиск)
- Remove: O(n) (из-за сдвига массива)
- IsKey: O(log n) (бинарный поиск)
*/

const (
	bitSize = 32 // фиксированный размер битовых строк (32 бита)
)

// Задание 6 - Словарь с битовыми ключами фиксированной длины
type BitStringDictionary[T any] struct {
	keys   []uint32 // массив битовых ключей
	values []T      // соответствующие значения
}

func InitBitStringDict[T any]() BitStringDictionary[T] {
	return BitStringDictionary[T]{
		keys:   make([]uint32, 0),
		values: make([]T, 0),
	}
}

func stringToBit(s string) uint32 {
	var result uint32
	maxLen := bitSize / 8

	if len(s) > maxLen {
		s = s[:maxLen]
	}

	for i, c := range s {
		if i >= maxLen {
			break
		}
		result |= uint32(c) << (8 * i) // упаковываем символы в uint32
	}
	return result
}

func (bsd *BitStringDictionary[T]) findBitKey(key uint32) (int, bool) {
	for i, k := range bsd.keys {
		if k == key {
			return i, true
		}
	}
	return -1, false
}

func (bsd *BitStringDictionary[T]) Put(key string, value T) {
	bitKey := stringToBit(key)
	idx, found := bsd.findBitKey(bitKey)
	if found {
		bsd.values[idx] = value
	} else {
		bsd.keys = append(bsd.keys, bitKey)
		bsd.values = append(bsd.values, value)
	}
}

func (bsd *BitStringDictionary[T]) Get(key string) (T, error) {
	var result T
	bitKey := stringToBit(key)
	idx, found := bsd.findBitKey(bitKey)
	if !found {
		return result, errors.New("ключ не найден")
	}
	return bsd.values[idx], nil
}

func (bsd *BitStringDictionary[T]) Remove(key string) error {
	bitKey := stringToBit(key)
	idx, found := bsd.findBitKey(bitKey)
	if !found {
		return errors.New("ключ не найден")
	}
	bsd.keys = append(bsd.keys[:idx], bsd.keys[idx+1:]...)
	bsd.values = append(bsd.values[:idx], bsd.values[idx+1:]...)
	return nil
}

func (bsd *BitStringDictionary[T]) IsKey(key string) bool {
	bitKey := stringToBit(key)
	_, found := bsd.findBitKey(bitKey)
	return found
}

/*
Битовые операции даются мне сложно, но здесь вроде +- разобрался
- Сложность операций:
  - Put: O(n) (линейный поиск)
  - Get: O(n) (линейный поиск)
  - Remove: O(n) (линейный поиск + сдвиг массива)
  - IsKey: O(n) (линейный поиск)
*/
