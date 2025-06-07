package main

import (
	"os"
	"strconv"
)

type HashTable struct {
	size   int
	step   int
	slots  []string
	filled []bool
}

func Init(sz int, stp int) HashTable {
	ht := HashTable{size: sz, step: stp, slots: nil}
	ht.slots = make([]string, sz)
	ht.filled = make([]bool, sz)
	return ht
}

func (ht *HashTable) HashFun(value string) int {
	hash := 1
	for _, c := range value {
		hash += int(c)
	}
	return hash % ht.size
}

func (ht *HashTable) SeekSlot(value string) int {
	if ht.full() {
		return -1
	}
	key := ht.seek(value)
	return key
}

func (ht *HashTable) full() bool {
	for _, b := range ht.filled {
		if !b {
			return false
		}
	}
	return true
}

func (ht *HashTable) Put(value string) int {
	key := ht.SeekSlot(value)
	if key != -1 {
		ht.filled[key] = true
		ht.slots[key] = value
	}
	return key
}

func (ht *HashTable) Find(value string) int {
	key := ht.seek(value)

	if key == -1 {
		return -1
	}

	if ht.slots[key] != value {
		return -1
	}
	return key
}

func (ht *HashTable) seek(value string) int {
	key := ht.HashFun(value)
	start := key
	fromStart := false
	for ht.filled[key] {
		if ht.slots[key] == value {
			return key
		}
		key = (ht.step + key) % ht.size

		if key <= start {
			fromStart = true
		}

		if fromStart && key >= start {
			return -1
		}
	}
	return key
}
