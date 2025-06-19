package main

import "fmt"

type NativeCache struct {
	size   int
	slots  []string
	values []string
	hits   []int
}

func NewNativeCache(sz int) *NativeCache {
	return &NativeCache{
		size:   sz,
		slots:  make([]string, sz),
		values: make([]string, sz),
		hits:   make([]int, sz),
	}
}

func (nc *NativeCache) hashFun(value string) int {
	sumBytes := 0
	for _, b := range []byte(value) {
		sumBytes += int(b)
	}
	return sumBytes % nc.size
}

func (nc *NativeCache) Get(key string) *string {
	index := nc.find(key)
	if index == -1 {
		return nil
	}
	nc.hits[index]++
	return &nc.values[index]
}

func (nc *NativeCache) Put(key, value string) {
	existingIndex := nc.find(key)
	if existingIndex != -1 {
		nc.values[existingIndex] = value
		return
	}

	index := nc.seekSlot(key)
	nc.slots[index] = key
	nc.values[index] = value
	nc.hits[index] = 0
}

func (nc *NativeCache) seekSlot(key string) int {
	index := nc.hashFun(key)

	for i := 0; i < nc.size; i++ {
		currentIndex := (index + i) % nc.size
		if nc.slots[currentIndex] == "" {
			return currentIndex
		}
	}

	minHits := nc.hits[0]
	minIndex := 0
	for i := 1; i < nc.size; i++ {
		if nc.hits[i] < minHits {
			minHits = nc.hits[i]
			minIndex = i
		}
	}
	return minIndex
}

func (nc *NativeCache) find(key string) int {
	index := nc.hashFun(key)

	for i := 0; i < nc.size; i++ {
		currentIndex := (index + i) % nc.size
		if nc.slots[currentIndex] == key {
			return currentIndex
		}
		if nc.slots[currentIndex] == "" {
			return -1
		}
	}

	return -1
}

func (nc *NativeCache) Debug() {
	fmt.Printf("Slots: %v\n", nc.slots)
	fmt.Printf("Values: %v\n", nc.values)
	fmt.Printf("Hits: %v\n", nc.hits)
}
