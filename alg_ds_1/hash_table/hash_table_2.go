package main

import (
	"os"
	"strconv"
)

// Задание 3 - динамическая хэш-таблица
// Добавлена функция, которая расширяет (удваивает) таблицу при ее заполненности больше,
// чем пороговое значение
type DynamicHashTable struct {
	size                int
	step                int
	slots               []string
	filled              []bool
	loadFactor          float64
	thresholdWhenResize float64
	initialSize         int
}

func InitDynamic(sz int, stp int, threshold float64) DynamicHashTable {
	ht := DynamicHashTable{
		size:                sz,
		step:                stp,
		slots:               make([]string, sz),
		filled:              make([]bool, sz),
		loadFactor:          0,
		thresholdWhenResize: threshold,
		initialSize:         sz,
	}
	return ht
}

func (ht *DynamicHashTable) HashFun(value string) int {
	hash := 1
	for _, c := range value {
		hash += int(c)
	}
	return hash % ht.size
}

func (ht *DynamicHashTable) full() bool {
	return ht.loadFactor >= ht.thresholdWhenResize
}

func (ht *DynamicHashTable) resize() {
	newSize := ht.size * 2
	newSlots := make([]string, newSize)
	newFilled := make([]bool, newSize)

	oldSlots := ht.slots
	oldFilled := ht.filled
	oldSize := ht.size

	ht.size = newSize
	ht.slots = newSlots
	ht.filled = newFilled
	ht.loadFactor = 0

	for i := 0; i < oldSize; i++ {
		if oldFilled[i] {
			ht.Put(oldSlots[i])
		}
	}
}

func (ht *DynamicHashTable) seek(value string) int {
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

func (ht *DynamicHashTable) SeekSlot(value string) int {
	if ht.full() {
		ht.resize()
	}
	key := ht.seek(value)
	return key
}

func (ht *DynamicHashTable) Put(value string) int {
	key := ht.SeekSlot(value)
	if key != -1 {
		ht.filled[key] = true
		ht.slots[key] = value
		ht.loadFactor = float64(ht.countFilled()) / float64(ht.size)
	}
	return key
}

func (ht *DynamicHashTable) countFilled() int {
	count := 0
	for _, b := range ht.filled {
		if b {
			count++
		}
	}
	return count
}

func (ht *DynamicHashTable) Find(value string) int {
	key := ht.seek(value)

	if key == -1 {
		return -1
	}

	if ht.slots[key] != value {
		return -1
	}
	return key
}

// Задание 4 - хэш-таблица с несколькими функциями
// и распределением их по нескольким "шагам" для уменьшения коллизий
// Почитал про подобные таблицы - без шагов коллизий много, с шагами линейное ( 1 - 2 - 3) пробирание превращается
// в нелинейное
type MultiHashTable struct {
	size      int
	steps     []int
	slots     []string
	filled    []bool
	hashFuncs []func(string) int
}

func InitMultiHash(sz int, steps []int, hashFuncs []func(string) int) MultiHashTable {
	ht := MultiHashTable{
		size:      sz,
		steps:     steps,
		slots:     make([]string, sz),
		filled:    make([]bool, sz),
		hashFuncs: hashFuncs,
	}
	return ht
}

func (ht *MultiHashTable) full() bool {
	for _, b := range ht.filled {
		if !b {
			return false
		}
	}
	return true
}

func (ht *MultiHashTable) seek(value string) int {
	for i, hashFunc := range ht.hashFuncs {
		key := hashFunc(value) % ht.size
		step := ht.steps[i]
		start := key
		fromStart := false

		for ht.filled[key] {
			if ht.slots[key] == value {
				return key
			}
			key = (step + key) % ht.size

			if key <= start {
				fromStart = true
			}

			if fromStart && key >= start {
				break
			}
		}

		if !ht.filled[key] {
			return key
		}
	}
	return -1
}

func (ht *MultiHashTable) SeekSlot(value string) int {
	if ht.full() {
		return -1
	}
	return ht.seek(value)
}

func (ht *MultiHashTable) Put(value string) int {
	key := ht.SeekSlot(value)
	if key != -1 {
		ht.filled[key] = true
		ht.slots[key] = value
	}
	return key
}

func (ht *MultiHashTable) Find(value string) int {
	for i, hashFunc := range ht.hashFuncs {
		key := hashFunc(value) % ht.size
		step := ht.steps[i]
		start := key
		fromStart := false

		for ht.filled[key] {
			if ht.slots[key] == value {
				return key
			}
			key = (step + key) % ht.size

			if key <= start {
				fromStart = true
			}

			if fromStart && key >= start {
				break
			}
		}
	}
	return -1
}

// Задание 5 - соленая хэш-таблица
type SecureHashTable struct {
	size   int
	step   int
	slots  []string
	filled []bool
	salt   string
}

func InitSecure(sz int, stp int, salt string) SecureHashTable {
	ht := SecureHashTable{
		size:   sz,
		step:   stp,
		slots:  make([]string, sz),
		filled: make([]bool, sz),
		salt:   salt,
	}
	return ht
}

func (ht *SecureHashTable) HashFun(value string) int {
	hash := 1
	salted := value + ht.salt
	for _, c := range salted {
		hash += int(c)
		hash += hash << 10
		hash ^= hash >> 6
	}
	hash += hash << 3
	hash ^= hash >> 11
	hash += hash << 15
	return hash % ht.size
}

func (ht *SecureHashTable) full() bool {
	for _, b := range ht.filled {
		if !b {
			return false
		}
	}
	return true
}

func (ht *SecureHashTable) seek(value string) int {
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

func (ht *SecureHashTable) SeekSlot(value string) int {
	if ht.full() {
		return -1
	}
	return ht.seek(value)
}

func (ht *SecureHashTable) Put(value string) int {
	key := ht.SeekSlot(value)
	if key != -1 {
		ht.filled[key] = true
		ht.slots[key] = value
	}
	return key
}

func (ht *SecureHashTable) Find(value string) int {
	key := ht.seek(value)

	if key == -1 {
		return -1
	}

	if ht.slots[key] != value {
		return -1
	}
	return key
}
