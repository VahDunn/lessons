package main

import (
	"constraints"
	"os"
	"testing"
)

func slicesEqual[T comparable](a, b []T) bool {
	if len(a) != len(b) {
		return false
	}
	for i := range a {
		if a[i] != b[i] {
			return false
		}
	}
	return true
}

func TestOrderedList_Add_Ascending(t *testing.T) {
	list := NewOrderedList[int](true)

	list.Add(3)
	list.Add(1)
	list.Add(4)
	list.Add(2)

	expected := []int{1, 2, 3, 4}
	actual := list.ToSlice()

	if !slicesEqual(actual, expected) {
		t.Errorf("Ожидался %v, получен %v", expected, actual)
	}

	if list.Count() != 4 {
		t.Errorf("Ожидался count=4, получен %d", list.Count())
	}
}

func TestOrderedList_Add_Descending(t *testing.T) {
	list := NewOrderedList[int](false)

	list.Add(3)
	list.Add(1)
	list.Add(4)
	list.Add(2)

	expected := []int{4, 3, 2, 1}
	actual := list.ToSlice()

	if !slicesEqual(actual, expected) {
		t.Errorf("Ожидался %v, получен %v", expected, actual)
	}
}

func TestOrderedList_Add_Strings_Ascending(t *testing.T) {
	list := NewOrderedList[string](true)

	list.Add("банан")
	list.Add("яблоко")
	list.Add("апельсин")

	expected := []string{"апельсин", "банан", "яблоко"}
	actual := list.ToSlice()

	if !slicesEqual(actual, expected) {
		t.Errorf("Ожидался %v, получен %v", expected, actual)
	}
}

func TestOrderedList_Add_Strings_Descending(t *testing.T) {
	list := NewOrderedList[string](false)

	list.Add("банан")
	list.Add("яблоко")
	list.Add("апельсин")

	expected := []string{"яблоко", "банан", "апельсин"}
	actual := list.ToSlice()

	if !slicesEqual(actual, expected) {
		t.Errorf("Ожидался %v, получен %v", expected, actual)
	}
}

func TestOrderedList_Find_Ascending(t *testing.T) {
	list := NewOrderedList[int](true)
	list.Add(1)
	list.Add(3)
	list.Add(5)

	// Поиск существующего элемента
	node, err := list.Find(3)
	if err != nil {
		t.Errorf("Элемент должен быть найден: %v", err)
	}
	if node.value != 3 {
		t.Errorf("Ожидалось значение 3, получено %v", node.value)
	}

	_, err = list.Find(4)
	if err == nil {
		t.Error("Должна быть ошибка для несуществующего элемента")
	}

	_, err = list.Find(6)
	if err == nil {
		t.Error("Должна быть ошибка для элемента за пределами диапазона")
	}
}

func TestOrderedList_Find_Descending(t *testing.T) {
	list := NewOrderedList[int](false)
	list.Add(5)
	list.Add(3)
	list.Add(1)

	node, err := list.Find(3)
	if err != nil {
		t.Errorf("Элемент должен быть найден: %v", err)
	}
	if node.value != 3 {
		t.Errorf("Ожидалось значение 3, получено %v", node.value)
	}

	_, err = list.Find(0)
	if err == nil {
		t.Error("Должна быть ошибка для элемента меньше минимального")
	}
}

func TestOrderedList_Delete_Ascending(t *testing.T) {
	list := NewOrderedList[int](true)
	list.Add(1)
	list.Add(2)
	list.Add(3)
	list.Add(4)

	list.Delete(2)
	expected := []int{1, 3, 4}
	actual := list.ToSlice()
	if !slicesEqual(actual, expected) {
		t.Errorf("После удаления 2: ожидался %v, получен %v", expected, actual)
	}

	list.Delete(1)
	expected = []int{3, 4}
	actual = list.ToSlice()
	if !slicesEqual(actual, expected) {
		t.Errorf("После удаления 1: ожидался %v, получен %v", expected, actual)
	}

	list.Delete(4)
	expected = []int{3}
	actual = list.ToSlice()
	if !slicesEqual(actual, expected) {
		t.Errorf("После удаления 4: ожидался %v, получен %v", expected, actual)
	}

	if list.Count() != 1 {
		t.Errorf("Ожидался count=1, получен %d", list.Count())
	}
}

func TestOrderedList_Delete_Descending(t *testing.T) {
	list := NewOrderedList[int](false)
	list.Add(4)
	list.Add(3)
	list.Add(2)
	list.Add(1)

	list.Delete(3)
	expected := []int{4, 2, 1}
	actual := list.ToSlice()
	if !slicesEqual(actual, expected) {
		t.Errorf("После удаления 3: ожидался %v, получен %v", expected, actual)
	}
}

func TestOrderedList_Delete_NonExistent(t *testing.T) {
	list := NewOrderedList[int](true)
	list.Add(1)
	list.Add(3)
	list.Add(5)

	initialCount := list.Count()
	list.Delete(4) // Элемент не существует

	if list.Count() != initialCount {
		t.Errorf("Count не должен изменяться при удалении несуществующего элемента")
	}

	expected := []int{1, 3, 5}
	actual := list.ToSlice()
	if !slicesEqual(actual, expected) {
		t.Errorf("Список не должен изменяться при удалении несуществующего элемента")
	}
}

func TestOrderedList_Clear(t *testing.T) {
	list := NewOrderedList[int](true)
	list.Add(1)
	list.Add(2)
	list.Add(3)

	list.Clear(false) // Меняем порядок на убывающий

	if list.Count() != 0 {
		t.Errorf("После Clear count должен быть 0, получен %d", list.Count())
	}

	if list.head != nil || list.tail != nil {
		t.Error("После Clear head и tail должны быть nil")
	}

	list.Add(1)
	list.Add(3)
	list.Add(2)

	expected := []int{3, 2, 1}
	actual := list.ToSlice()
	if !slicesEqual(actual, expected) {
		t.Errorf("После Clear с новым порядком ожидался %v, получен %v", expected, actual)
	}
}

func TestOrderedList_RemoveDuplicates(t *testing.T) {
	list := NewOrderedList[int](true)
	list.Add(1)
	list.Add(2)
	list.Add(2)
	list.Add(3)
	list.Add(3)
	list.Add(3)
	list.Add(4)

	list.RemoveDuplicates()

	expected := []int{1, 2, 3, 4}
	actual := list.ToSlice()
	if !slicesEqual(actual, expected) {
		t.Errorf("После удаления дубликатов: ожидался %v, получен %v", expected, actual)
	}

	if list.Count() != 4 {
		t.Errorf("После удаления дубликатов count должен быть 4, получен %d", list.Count())
	}
}

func TestOrderedList_Merge(t *testing.T) {
	list1 := NewOrderedList[int](true)
	list1.Add(1)
	list1.Add(3)
	list1.Add(5)

	list2 := NewOrderedList[int](true)
	list2.Add(2)
	list2.Add(4)
	list2.Add(6)

	err := list1.Merge(list2)
	if err != nil {
		t.Errorf("Ошибка при слиянии: %v", err)
	}

	expected := []int{1, 2, 3, 4, 5, 6}
	actual := list1.ToSlice()
	if !slicesEqual(actual, expected) {
		t.Errorf("После слияния: ожидался %v, получен %v", expected, actual)
	}
}

func TestOrderedList_Contains(t *testing.T) {
	list := NewOrderedList[int](true)
	list.Add(1)
	list.Add(2)
	list.Add(3)
	list.Add(4)
	list.Add(5)

	if !list.Contains([]int{2, 3, 4}) {
		t.Error("Подсписок [2, 3, 4] должен содержаться в списке")
	}

	if list.Contains([]int{2, 4, 5}) {
		t.Error("Подсписок [2, 4, 5] не должен содержаться в списке")
	}

	if !list.Contains([]int{}) {
		t.Error("Пустой подсписок должен содержаться в любом списке")
	}
}

func TestOrderedList_FindMostFrequent(t *testing.T) {
	list := NewOrderedList[int](true)
	list.Add(1)
	list.Add(2)
	list.Add(2)
	list.Add(3)
	list.Add(3)
	list.Add(3)

	value, count, err := list.FindMostFrequent()
	if err != nil {
		t.Errorf("Ошибка при поиске наиболее частого элемента: %v", err)
	}

	if value != 3 || count != 3 {
		t.Errorf("Ожидался элемент 3 с частотой 3, получен %d с частотой %d", value, count)
	}
}

func TestIndexedOrderedList_FindIndex(t *testing.T) {
	list := NewIndexedOrderedList[int](true)
	list.Add(10)
	list.Add(5)
	list.Add(15)
	list.Add(3)
	list.Add(7)

	index, err := list.FindIndex(7)
	if err != nil {
		t.Errorf("Ошибка при поиске индекса: %v", err)
	}
	if index != 2 {
		t.Errorf("Ожидался индекс 2 для элемента 7, получен %d", index)
	}

	_, err = list.FindIndex(20)
	if err == nil {
		t.Error("Должна быть ошибка при поиске несуществующего элемента")
	}
}

func TestIndexedOrderedList_GetByIndex(t *testing.T) {
	list := NewIndexedOrderedList[int](true)
	list.Add(10)
	list.Add(5)
	list.Add(15)

	value, err := list.GetByIndex(1)
	if err != nil {
		t.Errorf("Ошибка при получении элемента по индексу: %v", err)
	}
	if value != 10 {
		t.Errorf("Ожидался элемент 10 по индексу 1, получен %d", value)
	}

	_, err = list.GetByIndex(5)
	if err == nil {
		t.Error("Должна быть ошибка при обращении к индексу вне диапазона")
	}
}
