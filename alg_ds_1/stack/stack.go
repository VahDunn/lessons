package main

import (
	"errors"
	"os"
)

// Задание 1/2
// Стек - реализован через связанный список, работает с головой списка

var ErrStackEmpty = errors.New("stack is empty")

type Node[T any] struct {
	next  *Node[T]
	value T
}

type Stack[T any] struct {
	head *Node[T]
}

func (st *Stack[T]) Size() int {
	size := 0
	n := st.head
	for n != nil {
		n = n.next
		size++
	}
	return size
}

func (st *Stack[T]) Peek() (T, error) {
	var result T
	if st.head == nil {
		return result, ErrStackEmpty
	}
	return st.head.value, nil
}

func (st *Stack[T]) Pop() (T, error) {
	var result T

	if st.head == nil {
		return result, ErrStackEmpty
	}

	result = st.head.value
	st.head = st.head.next

	return result, nil
}

func (st *Stack[T]) Push(itm T) {
	n := &Node[T]{value: itm}
	n.next = st.head
	st.head = n
}

// Задание 3
// В случае, если количество элементов в стеке четное - цикл последовательно вернет все его элементы,
// пока тот не опустеет
// В случае, если количество элементов в стеке нечетное - на последнем элементе цикл выдаст ошибку, потому что
// второй pop() попытается обратиться к несуществующему элементу (верхний элемент пустого стека)
