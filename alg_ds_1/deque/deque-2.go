package main

import (
	"errors"
	"os"
	"unicode"
)

func IsPalindrome(s string) bool {
	d := Deque[rune]{}

	for _, r := range s {
		if unicode.IsLetter(r) || unicode.IsNumber(r) {
			d.AddTail(unicode.ToLower(r))
		}
	}

	for d.Size() > 1 {
		front, _ := d.RemoveFront()
		tail, _ := d.RemoveTail()
		if front != tail {
			return false
		}
	}
	return true
}

// Честно скажу - это было самое сложно задание на данный момент
// Честно скажу еще - пришлось гуглить, как подобные вещи делаются на плюсах
// В итоге две стека с ребалансировкой, но зато структура работает.
// Зубодробительновато.
type MinStack struct {
	stack []item
}

type item struct {
	value int
	min   int
}

func (ms *MinStack) Push(x int) {
	min := x
	if !ms.Empty() && ms.GetMin() < x {
		min = ms.GetMin()
	}
	ms.stack = append(ms.stack, item{x, min})
}

func (ms *MinStack) Pop() (int, error) {
	if ms.Empty() {
		return 0, errors.New("stack is empty")
	}
	val := ms.stack[len(ms.stack)-1].value
	ms.stack = ms.stack[:len(ms.stack)-1]
	return val, nil
}

func (ms *MinStack) Top() (int, error) {
	if ms.Empty() {
		return 0, errors.New("stack is empty")
	}
	return ms.stack[len(ms.stack)-1].value, nil
}

func (ms *MinStack) GetMin() int {
	if ms.Empty() {
		panic("stack is empty")
	}
	return ms.stack[len(ms.stack)-1].min
}

func (ms *MinStack) Empty() bool {
	return len(ms.stack) == 0
}

func (ms *MinStack) Size() int {
	return len(ms.stack)
}

func (ms *MinStack) Swap(other *MinStack) {
	ms.stack, other.stack = other.stack, ms.stack
}

type MinDeque struct {
	left  MinStack
	right MinStack
	temp  MinStack
}

func (md *MinDeque) rebalance() {
	if md.right.Empty() {
		md.left.Swap(&md.right)
	}

	size := md.right.Size() / 2
	for i := 0; i < size; i++ {
		val, _ := md.right.Top()
		md.right.Pop()
		md.temp.Push(val)
	}

	for !md.right.Empty() {
		val, _ := md.right.Top()
		md.right.Pop()
		md.left.Push(val)
	}

	for !md.temp.Empty() {
		val, _ := md.temp.Top()
		md.temp.Pop()
		md.right.Push(val)
	}
}

func (md *MinDeque) GetMin() (int, error) {
	if md.Empty() {
		return 0, errors.New("deque is empty")
	}

	if md.left.Empty() {
		return md.right.GetMin(), nil
	}
	if md.right.Empty() {
		return md.left.GetMin(), nil
	}

	leftMin := md.left.GetMin()
	rightMin := md.right.GetMin()

	if leftMin < rightMin {
		return leftMin, nil
	}
	return rightMin, nil
}

func (md *MinDeque) Empty() bool {
	return md.left.Empty() && md.right.Empty()
}

func (md *MinDeque) Size() int {
	return md.left.Size() + md.right.Size()
}

func (md *MinDeque) AddFront(x int) {
	md.left.Push(x)
}

func (md *MinDeque) AddTail(x int) {
	md.right.Push(x)
}

func (md *MinDeque) RemoveFront() (int, error) {
	if md.left.Empty() {
		md.rebalance()
	}
	return md.left.Pop()
}

func (md *MinDeque) RemoveTail() (int, error) {
	if md.right.Empty() {
		md.rebalance()
	}
	return md.right.Pop()
}

func (md *MinDeque) Front() (int, error) {
	if md.left.Empty() {
		md.rebalance()
	}
	return md.left.Top()
}

func (md *MinDeque) Tail() (int, error) {
	if md.right.Empty() {
		md.rebalance()
	}
	return md.right.Top()
}

type ArrayDeque[T any] struct {
	data  []T
	start int
	size  int
}

func (ad *ArrayDeque[T]) Size() int {
	return ad.size
}

func (ad *ArrayDeque[T]) grow() {
	newCapacity := max(2*len(ad.data), 1)
	newData := make([]T, newCapacity)

	for i := 0; i < ad.size; i++ {
		newData[i] = ad.data[(ad.start+i)%len(ad.data)]
	}

	ad.data = newData
	ad.start = 0
}

func (ad *ArrayDeque[T]) AddFront(itm T) {
	if ad.size == len(ad.data) {
		ad.grow()
	}
	ad.start = (ad.start - 1 + len(ad.data)) % len(ad.data)
	ad.data[ad.start] = itm
	ad.size++
}

func (ad *ArrayDeque[T]) AddTail(itm T) {
	if ad.size == len(ad.data) {
		ad.grow()
	}
	pos := (ad.start + ad.size) % len(ad.data)
	ad.data[pos] = itm
	ad.size++
}

func (ad *ArrayDeque[T]) RemoveFront() (T, error) {
	var zero T
	if ad.size == 0 {
		return zero, errors.New("deque is empty")
	}
	val := ad.data[ad.start]
	ad.start = (ad.start + 1) % len(ad.data)
	ad.size--
	return val, nil
}

func (ad *ArrayDeque[T]) RemoveTail() (T, error) {
	var zero T
	if ad.size == 0 {
		return zero, errors.New("deque is empty")
	}
	pos := (ad.start + ad.size - 1) % len(ad.data)
	val := ad.data[pos]
	ad.size--
	return val, nil
}

func max(a, b int) int {
	if a > b {
		return a
	}
	return b
}
