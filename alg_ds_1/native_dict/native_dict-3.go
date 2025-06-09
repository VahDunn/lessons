package main

import (
	"testing"
	//      "fmt"
	"os"
	"strconv"
)

func TestNativeDictionary(t *testing.T) {
	dict := Init[int](10)
	if dict.size != 10 {
		t.Errorf("Expected size 10, got %d", dict.size)
	}

	// 1. Добавление значения по новому ключу
	dict.Put("key1", 42)
	// 5. Извлечение значения по существующему ключу
	if val, err := dict.Get("key1"); err != nil || val != 42 {
		t.Errorf("Expected 42, got %d with error %v", val, err)
	}
	// 3. Проверка присутствующего ключа
	if !dict.IsKey("key1") {
		t.Error("Expected key1 to be present")
	}
	if dict.IsKey("nonexistent") {
		t.Error("Expected nonexistent key to be absent")
	}
	// 2. Добавление значения по существующему ключу (перезапись)
	dict.Put("key1", 100)
	if val, _ := dict.Get("key1"); val != 100 {
		t.Errorf("Expected 100 after overwrite, got %d", val)
	}
	// 4. Проверка отсутствующего ключа
	if dict.IsKey("Barsik") {
		t.Error("IsKey() should return false for missing key")
	}
	// 6. Извлечение значения по отсутствующему ключу
	if _, err := dict.Get("nonexistent"); err == nil {
		t.Error("Expected error for nonexistent key")
	}

	dict2 := Init[string](1)
	dict2.Put("key1", "value1")
	dict2.Put("key2", "value2")

	if dict2.IsKey("key1") {
		t.Error("Expected key1 to be overwritten due to collision")
	}
	if val, _ := dict2.Get("key2"); val != "value2" {
		t.Errorf("Expected value2, got %s", val)
	}

	// 7. Проверка нескольких ключей
	dict3 := Init[int](10)
	dict3.Put("apple", 26777)
	dict3.Put("carrot", 456546)
	dict3.Put("milk", 47457457)

	testCases := []struct {
		key    string
		value  int
		exists bool
	}{
		{"apple", 26777, true},
		{"carrot", 456546, true},
		{"milk", 47457457, true},
		{"bread", 0, false},
	}

	for _, tc := range testCases {
		if dict3.IsKey(tc.key) != tc.exists {
			t.Errorf("IsKey(%s) mismatch, expected %v", tc.key, tc.exists)
		}

		val, err := dict3.Get(tc.key)
		if tc.exists {
			if err != nil || val != tc.value {
				t.Errorf("Get(%s) mismatch, expected %d, got %d", tc.key, tc.value, val)
			}
		} else if err == nil {
			t.Errorf("Get(%s) should return error for missing key", tc.key)
		}
	}
}

func TestHashFun(t *testing.T) {
	dict := Init[int](10)
	hash1 := dict.HashFun("hello")
	hash2 := dict.HashFun("world")

	if hash1 < 0 || hash1 >= dict.size {
		t.Errorf("Hash value %d out of bounds", hash1)
	}
	if hash2 < 0 || hash2 >= dict.size {
		t.Errorf("Hash value %d out of bounds", hash2)
	}

	if dict.HashFun("hello") != hash1 {
		t.Error("Hash function not consistent")
	}
}

func TestEdgeCases(t *testing.T) {
	dict := Init[string](5)
	if dict.IsKey("any") {
		t.Error("Empty dictionary should not have keys")
	}

	dictZero := Init[int](0)
	if dictZero.size != 1 {
		t.Errorf("Expected size 1 for zero initialization, got %d", dictZero.size)
	}
	hash := dictZero.HashFun("test")
	if hash < 0 || hash >= dictZero.size {
		t.Errorf("Hash value %d out of bounds for size %d", hash, dictZero.size)
	}

	dict.Put("zero", "")
	if val, _ := dict.Get("zero"); val != "" {
		t.Error("Failed to store zero value")
	}
}
