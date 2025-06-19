package main

import (
	"fmt"
	"testing"
)

func TestNativeCache(t *testing.T) {
	nc := NewNativeCache(5)

	nc.Put("foo", "bar")
	result := nc.Get("foo")
	if result == nil || *result != "bar" {
		t.Errorf("Expected 'bar', got %v", result)
	}

	nc.Put("foo", "baz")
	result = nc.Get("foo")
	if result == nil || *result != "baz" {
		t.Errorf("Expected 'baz', got %v", result)
	}

	result = nc.Get("bar")
	if result != nil {
		t.Errorf("Expected nil, got %v", result)
	}

	nc.Put("1", "2")
	nc.Put("3", "4")
	nc.Put("5", "6")
	nc.Put("6", "7")

	result = nc.Get("3")
	if result == nil || *result != "4" {
		t.Errorf("Expected '4', got %v", result)
	}

	result = nc.Get("5")
	if result == nil || *result != "6" {
		t.Errorf("Expected '6', got %v", result)
	}

	result = nc.Get("6")
	if result == nil || *result != "7" {
		t.Errorf("Expected '7', got %v", result)
	}

	nc.Put("6", "9")
	result = nc.Get("6")
	if result == nil || *result != "9" {
		t.Errorf("Expected '9', got %v", result)
	}

	nc.Get("6")
	nc.Get("6")

	nc.Put("7", "8")

	result = nc.Get("7")
	if result == nil || *result != "8" {
		t.Errorf("Expected '8', got %v", result)
	}
}

func TestCollisionsAndEviction(t *testing.T) {
	nc := NewNativeCache(4)

	nc.Put("key1", "value1")
	nc.Put("key2", "value2")
	nc.Put("key3", "value3")
	nc.Put("key4", "value4")

	for i := 0; i < 5; i++ {
		nc.Get("key1")
	}
	for i := 0; i < 2; i++ {
		nc.Get("key2")
	}
	nc.Get("key3")

	nc.Put("key5", "value5")

	result := nc.Get("key5")
	if result == nil || *result != "value5" {
		t.Errorf("New key was not added correctly")
	}

	result = nc.Get("key4")
	if result != nil {
		t.Errorf("Least used key should have been evicted, but key4 still exists")
	}

	result = nc.Get("key1")
	if result == nil || *result != "value1" {
		t.Errorf("Most used key should not be evicted")
	}
}

func TestHitCounterAccuracy(t *testing.T) {
	nc := NewNativeCache(5)

	keys := []string{"key1", "key2", "key3"}
	for i, key := range keys {
		nc.Put(key, fmt.Sprintf("value%d", i))
	}

	expectedHits := []int{3, 7, 1}

	for i, key := range keys {
		for j := 0; j < expectedHits[i]; j++ {
			nc.Get(key)
		}
	}

	for i, key := range keys {
		index := nc.find(key)
		if index == -1 {
			t.Errorf("Key %s not found", key)
			continue
		}
		if nc.hits[index] != expectedHits[i] {
			t.Errorf("For key %s expected %d hits, got %d",
				key, expectedHits[i], nc.hits[index])
		}
	}
}
