package main

import (
	"io"
	"os"
	"testing"
)

func TestQueueSize(t *testing.T) {
	q := Queue[int]{}
	if q.Size() != 0 {
		t.Error("Size() должен вернуть 0 для пустой очереди")
	}

	q.Enqueue(1)
	if q.Size() != 1 {
		t.Error("Size() должен вернуть 1 после добавления элемента")
	}
}

func TestQueueDequeue(t *testing.T) {
	q := Queue[int]{}
	_, err := q.Dequeue()
	if err == nil {
		t.Error("Dequeue() должен вернуть ошибку для пустой очереди")
	}

	q.Enqueue(1)
	val, err := q.Dequeue()
	if err != nil || val != 1 {
		t.Error("Dequeue() должен вернуть первый добавленный элемент")
	}
}

func TestQueueEnqueue(t *testing.T) {
	q := Queue[int]{}
	q.Enqueue(1)
	q.Enqueue(2)

	if q.head.val != 1 || q.tail.val != 2 {
		t.Error("head и tail должны указывать на первый и последний элементы")
	}

	val, _ := q.Dequeue()
	if val != 1 {
		t.Error("Порядок элементов должен соответствовать FIFO")
	}
}

func TestRotateQueueEmpty(t *testing.T) {
	q := Queue[int]{}
	RotateQueue(&q, 3)
	if q.Size() != 0 {
		t.Error("Вращение пустой очереди не должно изменять ее размер")
	}
}

func TestRotateQueueSingle(t *testing.T) {
	q := Queue[int]{}
	q.Enqueue(1)
	RotateQueue(&q, 5)
	val, _ := q.Dequeue()
	if val != 1 {
		t.Error("Вращение очереди с одним элементом не должно изменять ее содержимое")
	}
}

func TestRotateQueuePositive(t *testing.T) {
	q := Queue[int]{}
	for i := 1; i <= 5; i++ {
		q.Enqueue(i)
	}

	RotateQueue(&q, 2)
	val, _ := q.Dequeue()
	if val != 3 {
		t.Error("После вращения на +2 первым должен быть элемент 3")
	}
}

func TestRotateQueueNegative(t *testing.T) {
	q := Queue[int]{}
	for i := 1; i <= 5; i++ {
		q.Enqueue(i)
	}

	RotateQueue(&q, -2)
	val, _ := q.Dequeue()
	if val != 4 {
		t.Error("После вращения на -2 первым должен быть элемент 4")
	}
}

func TestRotateQueueLargeN(t *testing.T) {
	q := Queue[int]{}
	for i := 1; i <= 5; i++ {
		q.Enqueue(i)
	}

	RotateQueue(&q, 17)
	val, _ := q.Dequeue()
	if val != 3 {
		t.Error("После вращения на 17 (size=5) первым должен быть элемент 3")
	}
}

func TestRotateQueueLargeNegativeN(t *testing.T) {
	q := Queue[int]{}
	for i := 1; i <= 5; i++ {
		q.Enqueue(i)
	}

	RotateQueue(&q, -12)
	val, _ := q.Dequeue()
	if val != 4 {
		t.Error("После вращения на -12 (size=5) первым должен быть элемент 4")
	}
}
