package main

import (
	"os"
	"strconv"
	"testing"
)

func TestHashTable(t *testing.T) {
	ht := Init(17, 3)

	hash := ht.HashFun("test")
	if hash < 0 || hash >= ht.size {
		t.Errorf("HashFun returned invalid value: %d", hash)
	}

	key1 := ht.Put("apple")
	if key1 == -1 {
		t.Error("Put failed to insert 'apple'")
	}

	foundKey := ht.Find("apple")
	if foundKey != key1 {
		t.Errorf("Find returned wrong key: expected %d, got %d", key1, foundKey)
	}

	key2 := ht.Put("banana")
	if key2 == -1 {
		t.Error("Put failed to insert 'banana'")
	}
	if key1 == key2 {
		t.Error("Put returned same keys for different values")
	}

	notFound := ht.Find("orange")
	if notFound != -1 {
		t.Error("Find should return -1 for non-existent value")
	}

	for i := 0; i < ht.size; i++ {
		ht.Put("item" + strconv.Itoa(i))
	}

	fullKey := ht.Put("overflow")
	if fullKey != -1 {
		t.Error("Put should return -1 when table is full")
	}

	slot := ht.SeekSlot("new item")
	if slot != -1 {
		t.Error("SeekSlot should return -1 when table is full")
	}
}

func TestHashFunConsistency(t *testing.T) {
	ht := Init(17, 3)
	value := "consistent"
	hash1 := ht.HashFun(value)
	hash2 := ht.HashFun(value)
	if hash1 != hash2 {
		t.Errorf("HashFun inconsistent: %d != %d", hash1, hash2)
	}
}

func TestSeekSlot(t *testing.T) {
	ht := Init(7, 3)

	ht.Put("a")
	ht.Put("b")
	ht.Put("c")

	slot := ht.SeekSlot("d")
	if slot == -1 {
		t.Error("SeekSlot failed to find empty slot")
	}
	if ht.filled[slot] {
		t.Errorf("SeekSlot returned filled slot: %d", slot)
	}

	existingSlot := ht.seek("a")
	if existingSlot == -1 {
		t.Error("seek failed to find existing value")
	}
	if ht.slots[existingSlot] != "a" {
		t.Errorf("seek returned wrong slot: expected 'a', got '%s'", ht.slots[existingSlot])
	}
}
