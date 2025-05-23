package main

func (l1 *LinkedList) SumTwoLists(l2 *LinkedList) *LinkedList {
	if l1 == nil || l2 == nil || l1.Count() != l2.Count() ||
		l2.Count() == 0 || l1.Count() == 0 {
		return nil
	}
	res := &LinkedList{}
	first := l1.head
	second := l2.head
	for first != nil && second != nil {
		newNode := Node{value: first.value + second.value}
		res.AddInTail(&newNode)
		first = first.next
		second = second.next
	}
	return res
}
