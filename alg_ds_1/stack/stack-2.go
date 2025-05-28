package main

import (
	"errors"
	"fmt"
	"os"
	"strconv"
	"strings"
)

// задания 4-7 - обновленный стек и доп. функции (для скобок, минимум и среднее значение)
var ErrStackEmpty = errors.New("stack is empty")

type Node[T any] struct {
	next  *Node[T]
	value T
}

type Stack[T any] struct {
	head     *Node[T]
	minStack *Stack[T]
	sum      float64
	count    int
}

func NewStack[T any]() *Stack[T] {
	return &Stack[T]{
		minStack: &Stack[T]{},
	}
}

func (st *Stack[T]) Size() int {
	return st.count
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

	if st.minStack.head != nil {
		currentMin, err := st.minStack.Peek()
		if err != nil {
			return result, err
		}
		if compare(result, currentMin) == 0 {
			_, err = st.minStack.Pop()
			if err != nil {
				return result, err
			}
		}
	}
	st.sum -= toFloat(result)
	st.count--

	return result, nil
}

func (st *Stack[T]) Push(itm T) {
	n := &Node[T]{value: itm}
	n.next = st.head
	st.head = n
	if st.minStack.head == nil {
		st.minStack.Push(itm)
	} else {
		currentMin, _ := st.minStack.Peek()
		if compare(itm, currentMin) <= 0 {
			st.minStack.Push(itm)
		}
	}

	st.sum += toFloat(itm)
	st.count++
}

func (st *Stack[T]) GetMin() (T, error) {
	var result T
	if st.minStack.head == nil {
		return result, ErrStackEmpty
	}
	return st.minStack.Peek()
}

func (st *Stack[T]) GetAverage() (float64, error) {
	if st.count == 0 {
		return 0, ErrStackEmpty
	}
	return st.sum / float64(st.count), nil
}

func compare[T any](a, b T) int {
	switch va := any(a).(type) {
	case int:
		vb := any(b).(int)
		if va < vb {
			return -1
		} else if va > vb {
			return 1
		}
		return 0
	case float32:
		vb := any(b).(float32)
		if va < vb {
			return -1
		} else if va > vb {
			return 1
		}
		return 0
	case float64:
		vb := any(b).(float64)
		if va < vb {
			return -1
		} else if va > vb {
			return 1
		}
		return 0
	default:
		panic("unsupported type")
	}
}

func toFloat[T any](val T) float64 {
	switch v := any(val).(type) {
	case int:
		return float64(v)
	case float32:
		return float64(v)
	case float64:
		return v
	// Можно добавить другие числовые типы
	default:
		panic("unsupported type")
	}
}

func isBalanced(s string) bool {
	stack := &Stack[rune]{}
	pairs := map[rune]rune{
		')': '(',
		'}': '{',
		']': '[',
	}

	for _, char := range s {
		switch char {
		case '(', '{', '[':
			stack.Push(char)
		case ')', '}', ']':
			top, err := stack.Pop()
			if err != nil || top != pairs[char] {
				return false
			}
		}
	}

	return stack.Size() == 0
}

// Задание 8 - Постфиксная запись выражения
func evaluatePostfix(expr string) (int, error) {
	s1 := NewStack[string]()
	s2 := NewStack[int]()
	tokens := strings.Fields(expr)

	for i := len(tokens) - 1; i >= 0; i-- {
		s1.Push(tokens[i])
	}

	for s1.Size() > 0 {
		token, err := s1.Pop()
		if err != nil {
			return 0, err
		}

		switch token {
		case "+", "*", "=":
			if token == "=" {
				result, err := s2.Peek()
				if err != nil {
					return 0, errors.New("nothing to return")
				}
				return result, nil
			}

			if s2.Size() < 2 {
				return 0, errors.New("not enough operands")
			}

			a, err := s2.Pop()
			if err != nil {
				return 0, err
			}
			b, err := s2.Pop()
			if err != nil {
				return 0, err
			}

			var res int
			switch token {
			case "+":
				res = b + a
			case "*":
				res = b * a
			}

			s2.Push(res)
		default:
			num, err := strconv.Atoi(token)
			if err != nil {
				return 0, fmt.Errorf("invalid token: %s", token)
			}
			s2.Push(num)
		}
	}

	if s2.Size() == 1 {
		return s2.Pop()
	}

	return 0, errors.New("invalid expression")
}
