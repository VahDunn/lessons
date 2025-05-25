package main

import (
	"testing"
)

func TestLinkedList2(t *testing.T) {
	t.Run("AddInTail", func(t *testing.T) {
		l := LinkedList2{}
		l.AddInTail(Node{value: 1})
		l.AddInTail(Node{value: 2})
		l.AddInTail(Node{value: 3})

		if l.Count() != 3 {
			t.Error("Count() должен вернуть 3 после добавления трех элементов")
		}

		if l.head.value != 1 || l.tail.value != 3 {
			t.Error("head должен быть 1, tail должен быть 3")
		}
	})

	t.Run("Find", func(t *testing.T) {
		l := LinkedList2{}
		l.AddInTail(Node{value: 1})
		l.AddInTail(Node{value: 2})
		l.AddInTail(Node{value: 3})

		node, err := l.Find(2)
		if err != nil || node.value != 2 {
			t.Error("Find должен вернуть узел со значением 2")
		}

		_, err = l.Find(4)
		if err == nil {
			t.Error("должна быть ошибка при поиске несуществующего элемента")
		}
	})

	t.Run("FindAll", func(t *testing.T) {
		l := LinkedList2{}
		l.AddInTail(Node{value: 1})
		l.AddInTail(Node{value: 2})
		l.AddInTail(Node{value: 2})
		l.AddInTail(Node{value: 3})

		nodes := l.FindAll(2)
		if len(nodes) != 2 {
			t.Error("FindAll должен вернуть 2 узла со значением 2")
		}
	})

	t.Run("Delete", func(t *testing.T) {
		l := LinkedList2{}
		l.AddInTail(Node{value: 1})
		l.AddInTail(Node{value: 2})
		l.AddInTail(Node{value: 3})

		l.Delete(2, false)
		if l.Count() != 2 || l.head.next.value != 3 {
			t.Error("элемент 2 должен быть удален")
		}

		l.AddInTail(Node{value: 2})
		l.AddInTail(Node{value: 2})
		l.Delete(2, true)
		if l.Count() != 2 || l.head.next.value != 3 {
			t.Error("все элементы со значением 2 должны быть удалены")
		}
	})

	t.Run("Insert", func(t *testing.T) {
		l := LinkedList2{}
		l.AddInTail(Node{value: 1})
		l.AddInTail(Node{value: 3})
		node, _ := l.Find(1)
		var realNode *Node
		for curr := l.head; curr != nil; curr = curr.next {
			if curr.value == node.value {
				realNode = curr
				break
			}
		}

		l.Insert(realNode, Node{value: 2})
		if l.Count() != 3 || l.head.next.value != 2 {
			t.Error("элемент 2 должен быть вставлен после элемента 1")
		}

		l.Insert(nil, Node{value: 0})
		if l.Count() != 4 || l.head.value != 0 {
			t.Error("элемент 0 должен быть вставлен в начало списка")
		}
	})

	t.Run("InsertFirst", func(t *testing.T) {
		l := LinkedList2{}
		l.InsertFirst(Node{value: 1})
		l.InsertFirst(Node{value: 0})

		if l.Count() != 2 || l.head.value != 0 {
			t.Error("элемент 0 должен быть в начале списка")
		}
	})

	t.Run("Clean", func(t *testing.T) {
		l := LinkedList2{}
		l.AddInTail(Node{value: 1})
		l.AddInTail(Node{value: 2})
		l.Clean()

		if l.Count() != 0 || l.head != nil || l.tail != nil {
			t.Error("список должен быть пуст после Clean()")
		}
	})

	t.Run("Reverse", func(t *testing.T) {
		l := LinkedList2{}
		l.AddInTail(Node{value: 1})
		l.AddInTail(Node{value: 2})
		l.AddInTail(Node{value: 3})
		l.Reverse()

		if l.head.value != 3 || l.tail.value != 1 || l.head.next.value != 2 {
			t.Error("список должен быть развернут в обратном порядке")
		}
	})

	t.Run("HasCycle", func(t *testing.T) {
		l := LinkedList2{}
		l.AddInTail(Node{value: 1})
		l.AddInTail(Node{value: 2})
		l.AddInTail(Node{value: 3})

		if l.HasCycle() {
			t.Error("список без цикла должен вернуть false")
		}

		// Создаем цикл
		l.tail.next = l.head
		if !l.HasCycle() {
			t.Error("список с циклом должен вернуть true")
		}
	})

	t.Run("Sort", func(t *testing.T) {
		l := LinkedList2{}
		l.AddInTail(Node{value: 3})
		l.AddInTail(Node{value: 1})
		l.AddInTail(Node{value: 2})
		l.Sort()

		if l.head.value != 1 || l.head.next.value != 2 || l.tail.value != 3 {
			t.Error("список должен быть отсортирован по возрастанию")
		}
	})

	t.Run("MergeSortedLists", func(t *testing.T) {
		l1 := LinkedList2{}
		l1.AddInTail(Node{value: 1})
		l1.AddInTail(Node{value: 3})

		l2 := LinkedList2{}
		l2.AddInTail(Node{value: 2})
		l2.AddInTail(Node{value: 4})

		merged := l1.MergeSortedLists(&l2)
		if merged.Count() != 4 || merged.head.value != 1 || merged.head.next.value != 2 ||
			merged.head.next.next.value != 3 || merged.tail.value != 4 {
			t.Error("списки должны быть корректно объединены в отсортированном порядке")
		}
	})
}
