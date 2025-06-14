package main

import (
	"os"
)

// Задание 2 - Merge объединяет несколько фильтров Блюма в один
// Сложность по памяти и времени О(n)
func Merge(filters ...*BloomFilter) *BloomFilter {
	if len(filters) == 0 {
		return &BloomFilter{}
	}

	size := filters[0].filter_len
	for _, f := range filters {
		if f.filter_len != size {
			return nil
		}
	}

	merged := &BloomFilter{
		filter_len: size,
	}

	for _, f := range filters {
		merged.filter |= f.filter
	}

	return merged
}

// Задание 3 - считающий фильтр - по времени О(n) - по длине строки, по памяти О(1)(изменение счетчиков)
type CountingBloomFilter struct {
	counters   []uint8
	filter_len int
}

func (f *CountingBloomFilter) Hash1(s string) int {
	sum := 0
	for _, char := range s {
		code := int(char)
		sum = ((sum * 17) + code) % f.filter_len
	}
	return sum
}

func (f *CountingBloomFilter) Hash2(s string) int {
	sum := 0
	for _, char := range s {
		code := int(char)
		sum = ((sum * 223) + code) % f.filter_len
	}
	return sum
}

func (f *CountingBloomFilter) Add(s string) {
	h1 := f.Hash1(s)
	h2 := f.Hash2(s)

	f.counters[h1]++
	f.counters[h2]++
}

func (f *CountingBloomFilter) IsValue(s string) bool {
	h1 := f.Hash1(s)
	h2 := f.Hash2(s)

	return f.counters[h1] > 0 && f.counters[h2] > 0
}

func (f *CountingBloomFilter) Remove(s string) bool {
	if !f.IsValue(s) {
		return false
	}

	h1 := f.Hash1(s)
	h2 := f.Hash2(s)

	f.counters[h1]--
	f.counters[h2]--

	return true
}

// Задание 4 - единственный спосооб, который реализовать "легко" - хранить словарь со значениями.
// Что, в общем-то, не имеет смысла, поскольку тогда фильтр и не нужен - мы всегда знаем точно,
// есть элемент во множестве или нет. Можно пробовать генерировать предположительные значения и хэшировать,
// но это ресурсозатратно.
