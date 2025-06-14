package main

import (
	"os"
)

type BloomFilter struct {
	filter     int
	filter_len int
}

func (f *BloomFilter) Hash1(s string) int {
	sum := 0
	for _, char := range s {
		code := int(char)

		sum = ((sum * 17) + code) % f.filter_len
	}
	return sum
}

func (f *BloomFilter) Hash2(s string) int {
	sum := 0
	for _, char := range s {
		code := int(char)

		sum = ((sum * 223) + code) % f.filter_len
	}
	return sum
}

func (f *BloomFilter) Add(s string) {
	h1 := f.Hash1(s)
	h2 := f.Hash2(s)

	f.filter |= h1
	f.filter |= h2
}

func (f *BloomFilter) IsValue(s string) bool {
	h1 := f.Hash1(s)
	h2 := f.Hash2(s)

	return f.filter&h1 > 0 && f.filter&h2 > 0
}
