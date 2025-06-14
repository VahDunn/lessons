package main

import (
	"os"
	"testing"
)

func TestBloomFilter(t *testing.T) {
	t.Run("Пустой фильтр", func(t *testing.T) {
		bf := BloomFilter{filter: 0, filter_len: 32}
		if bf.IsValue("test") {
			t.Error("Пустой фильтр не должен содержать значений")
		}
	})

	t.Run("Одно значение", func(t *testing.T) {
		bf := BloomFilter{filter: 0, filter_len: 32}
		value := "hello"
		bf.Add(value)
		if !bf.IsValue(value) {
			t.Error("Фильтр должен содержать добавленное значение")
		}
	})

	t.Run("Несколько значений", func(t *testing.T) {
		bf := BloomFilter{filter: 0, filter_len: 32}
		values := []string{"foo", "bar", "baz"}
		for _, v := range values {
			bf.Add(v)
		}
		for _, v := range values {
			if !bf.IsValue(v) {
				t.Errorf("Фильтр должен содержать добавленное значение: %s", v)
			}
		}
	})

	t.Run("Разные длины фильтра", func(t *testing.T) {
		lengths := []int{32, 64}
		value := "test"
		for _, l := range lengths {
			bf := BloomFilter{filter: 0, filter_len: l}
			bf.Add(value)
			if !bf.IsValue(value) {
				t.Errorf("Фильтр длиной %d должен содержать добавленное значение", l)
			}
		}
	})

	t.Run("Консистентность хэш-функций", func(t *testing.T) {
		bf := BloomFilter{filter: 0, filter_len: 32}
		value := "consistent"
		h1 := bf.Hash1(value)
		h2 := bf.Hash2(value)

		if bf.Hash1(value) != h1 {
			t.Error("Hash1 должна быть консистентной")
		}
		if bf.Hash2(value) != h2 {
			t.Error("Hash2 должна быть консистентной")
		}
	})

	t.Run("Пустая строка", func(t *testing.T) {
		bf := BloomFilter{filter: 0, filter_len: 32}
		bf.Add("")
		if bf.Hash1("") != 0 || bf.Hash2("") != 0 {
			t.Error("Хэш-функции должны возвращать 0 для пустой строки")
		}
	})
}

func TestEdgeCases(t *testing.T) {
	t.Run("Очень маленькая длина фильтра", func(t *testing.T) {
		bf := BloomFilter{filter: 0, filter_len: 2}
		value := "test"
		bf.Add(value)
		bf.IsValue(value)
	})

	t.Run("Не-ASCII символы", func(t *testing.T) {
		bf := BloomFilter{filter: 0, filter_len: 32}
		values := []string{"日本語", "русский", "€uro"}
		for _, v := range values {
			bf.Add(v)
			bf.IsValue(v)
		}
	})
}
