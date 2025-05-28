package main

import (
	"os"
	"testing"
)

func TestStack(t *testing.T) {
	t.Run("Empty stack", func(t *testing.T) {
		st := Stack[int]{}
		if st.Size() != 0 {
			t.Error("Size() должен вернуть 0 для пустого стека")
		}

		_, err := st.Peek()
		if err == nil || err.Error() != "stack is empty" {
			t.Error("Peek() должен вернуть ошибку для пустого стека")
		}

		_, err = st.Pop()
		if err == nil || err.Error() != "stack is empty" {
			t.Error("Pop() должен вернуть ошибку для пустого стека")
		}
	})

	t.Run("Push and Peek", func(t *testing.T) {
		st := Stack[string]{}
		st.Push("first")
		st.Push("second")

		if st.Size() != 2 {
			t.Error("Size() должен вернуть 2 после добавления двух элементов")
		}

		val, err := st.Peek()
		if err != nil {
			t.Error("Peek() не должен возвращать ошибку для непустого стека")
		}
		if val != "second" {
			t.Error("Peek() должен вернуть последний добавленный элемент")
		}

		if st.Size() != 2 {
			t.Error("Size() не должен изменяться после Peek()")
		}
	})

	t.Run("Push and Pop", func(t *testing.T) {
		st := Stack[float64]{}
		st.Push(1.5)
		st.Push(2.7)
		st.Push(3.9)

		if st.Size() != 3 {
			t.Error("Size() должен вернуть 3 после добавления трех элементов")
		}

		val, err := st.Pop()
		if err != nil {
			t.Error("Pop() не должен возвращать ошибку для непустого стека")
		}
		if val != 3.9 {
			t.Error("Pop() должен вернуть последний добавленный элемент")
		}
		if st.Size() != 2 {
			t.Error("Size() должен уменьшиться после Pop()")
		}

		val, err = st.Pop()
		if err != nil {
			t.Error("Pop() не должен возвращать ошибку для непустого стека")
		}
		if val != 2.7 {
			t.Error("Pop() должен вернуть предпоследний добавленный элемент")
		}

		val, err = st.Pop()
		if err != nil {
			t.Error("Pop() не должен возвращать ошибку для непустого стека")
		}
		if val != 1.5 {
			t.Error("Pop() должен вернуть первый добавленный элемент")
		}

		if st.Size() != 0 {
			t.Error("Size() должен вернуть 0 после удаления всех элементов")
		}

		_, err = st.Pop()
		if err == nil || err.Error() != "stack is empty" {
			t.Error("Pop() должен вернуть ошибку для пустого стека")
		}
	})

	t.Run("Multiple operations", func(t *testing.T) {
		st := Stack[rune]{}
		st.Push('a')
		st.Push('b')
		st.Push('c')

		if st.Size() != 3 {
			t.Error("Size() должен вернуть 3 после добавления трех элементов")
		}

		st.Pop()
		st.Pop()
		st.Push('d')
		st.Push('e')

		if st.Size() != 3 {
			t.Error("Size() должен вернуть 3 после комбинации операций")
		}

		val, err := st.Pop()
		if err != nil {
			t.Error("Pop() не должен возвращать ошибку для непустого стека")
		}
		if val != 'e' {
			t.Error("Pop() должен вернуть последний добавленный элемент")
		}

		val, err = st.Peek()
		if err != nil {
			t.Error("Peek() не должен возвращать ошибку для непустого стека")
		}
		if val != 'd' {
			t.Error("Peek() должен вернуть предпоследний добавленный элемент")
		}
	})
}
