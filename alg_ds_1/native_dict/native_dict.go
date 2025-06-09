package main

import (
	"errors"
	//      "fmt"
	"os"
	"strconv"
)

type NativeDictionary[T any] struct {
	size   int
	slots  []string
	values []T
	filled []bool
}

// создание экземпляра словаря
func Init[T any](sz int) NativeDictionary[T] {
	if sz <= 0 {
		sz = 1 // минимальный размер, чтобы избежать деления на 0
	}
	nd := NativeDictionary[T]{size: sz, slots: nil, values: nil}
	nd.slots = make([]string, sz)
	nd.values = make([]T, sz)
	nd.filled = make([]bool, sz)
	return nd
}

func (nd *NativeDictionary[T]) HashFun(value string) int {
	if nd.size == 0 {
		return 0 // защита от деления на 0
	}
	hash := 1
	for i, c := range value {
		hash += int(c) * (i + 1)
	}
	return hash % nd.size
}

func (nd *NativeDictionary[T]) IsKey(key string) bool {
	keyIndex := nd.HashFun(key)
	return nd.filled[keyIndex] && nd.slots[keyIndex] == key
}

func (nd *NativeDictionary[T]) Get(key string) (T, error) {
	var result T
	keyIndex := nd.HashFun(key)
	if !nd.filled[keyIndex] || nd.slots[keyIndex] != key {
		return result, errors.New("not found")
	}
	return nd.values[keyIndex], nil
}

func (nd *NativeDictionary[T]) Put(key string, value T) {
	keyIndex := nd.HashFun(key)
	nd.slots[keyIndex] = key
	nd.values[keyIndex] = value
	nd.filled[keyIndex] = true
}
