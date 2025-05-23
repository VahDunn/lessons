package main

import "testing"

func TestAddInTail(t *testing.T) {
	l := LinkedList{}
	n1 := &Node{value: 1}
	n2 := &Node{value: 2}

	l.AddInTail(n1)
	if l.head != n1 || l.tail != n1 {
		t.Error("head и tail должны указывать на первый добавленный элемент")
	}

	l.AddInTail(n2)
	if l.tail != n2 || l.head.next != n2 {
		t.Error("tail должен обновляться при добавлении нового элемента")
	}
}

func TestCount(t *testing.T) {
	l := LinkedList{}
	if l.Count() != 0 {
		t.Error("Count() должен вернуть 0 для пустого списка")
	}

	l.AddInTail(&Node{value: 1})
	l.AddInTail(&Node{value: 2})
	if l.Count() != 2 {
		t.Error("неверное возвращаемое значение")
	}
}

func TestFind(t *testing.T) {
	l := LinkedList{}
	_, err := l.Find(1)
	if err == nil {
		t.Error("должна быть ошибка при поиске в пустом списке")
	}

	l.AddInTail(&Node{value: 1})
	l.AddInTail(&Node{value: 2})

	node, err := l.Find(2)
	if err != nil || node.value != 2 {
		t.Error("Find  должен вернуть узел со значением 2")
	}

	_, err = l.Find(3)
	if err == nil {
		t.Error("должна быть ошибка, если элемент не найден")
	}
}

func TestFindAll(t *testing.T) {
	l := LinkedList{}
	if len(l.FindAll(1)) != 0 {
		t.Error("должен быть пустой слайс для пустого списка")
	}

	l.AddInTail(&Node{value: 1})
	l.AddInTail(&Node{value: 2})
	l.AddInTail(&Node{value: 1})

	nodes := l.FindAll(1)
	if len(nodes) != 2 {
		t.Error("FindAll должен вернуть 2 узла со значением 1")
	}
}

func TestDelete(t *testing.T) {
	l := LinkedList{}
	l.Delete(1, false)

	l.AddInTail(&Node{value: 1})
	l.AddInTail(&Node{value: 2})
	l.AddInTail(&Node{value: 3})

	l.Delete(2, false)
	if l.Count() != 2 || l.head.next.value != 3 {
		t.Error("элемент 2 должен быть удален")
	}

	l.AddInTail(&Node{value: 1})
	l.Delete(1, true)
	if l.Count() != 1 || l.head.value != 3 {
		t.Error("все элементы со значением 1 должны быть удалены")
	}

	l.Clean()
	l.Delete(1, false)
}

func TestInsert(t *testing.T) {
	l := LinkedList{}
	n1 := &Node{value: 1}
	n2 := &Node{value: 2}

	l.InsertFirst(n1)
	l.Insert(n1, n2)
	if l.head.next != n2 || l.tail != n2 {
		t.Error("n2 должен быть добавлен после n1")
	}
}

func TestInsertFirst(t *testing.T) {
	l := LinkedList{}
	n1 := &Node{value: 1}
	n2 := &Node{value: 2}

	l.InsertFirst(n1)
	if l.head != n1 || l.tail != n1 {
		t.Error("n1 должен быть добавлен в начало")
	}

	l.InsertFirst(n2)
	if l.head != n2 || l.head.next != n1 {
		t.Error("n2 должен быть добавлен перед n1")
	}
}

func TestClean(t *testing.T) {
	l := LinkedList{}
	l.AddInTail(&Node{value: 1})
	l.AddInTail(&Node{value: 2})

	l.Clean()
	if l.head != nil || l.tail != nil {
		t.Error("список должен быть пуст после Clean()")
	}
}

func TestSumTwoLists(t *testing.T) {
	l1 := LinkedList{}
	l2 := LinkedList{}

	if res := l1.SumTwoLists(&l2); res != nil {
		println(res)
		t.Error("должно быть nil для двух пустых списков")
	}

	l1.AddInTail(&Node{value: 1})
	if res := l1.SumTwoLists(&l2); res != nil {
		t.Error("должно быть nil при разных длинах")
	}

	l2.AddInTail(&Node{value: 2})
	res := l1.SumTwoLists(&l2)
	if res == nil || res.head.value != 3 || res.Count() != 1 {
		t.Error("должен быть список из 1 элемента со значением 3")
	}

	if res := l1.SumTwoLists(nil); res != nil {
		t.Error("Ожидается nil, если один из списков nil")
	}
}
