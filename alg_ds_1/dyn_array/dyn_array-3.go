package main

import (
	"fmt"
	"os"
	"testing"
)

func TestDynArray(t *testing.T) {
	t.Run("Init", func(t *testing.T) {
		da := DynArray[int]{}
		da.Init()
		if da.count != 0 || da.capacity != 16 {
			t.Errorf("Init failed, got count=%d, capacity=%d", da.count, da.capacity)
		}
	})

	t.Run("Append", func(t *testing.T) {
		da := DynArray[int]{}
		da.Init()
		for i := 0; i < 20; i++ {
			da.Append(i)
		}
		if da.count != 20 || da.capacity != 32 {
			t.Errorf("Append resize failed, got count=%d, capacity=%d", da.count, da.capacity)
		}
	})

	t.Run("Insert", func(t *testing.T) {
		da := DynArray[int]{}
		da.Init()
		da.Append(1)
		da.Append(3)
		err := da.Insert(2, 1)
		if err != nil {
			t.Errorf("Insert failed with error: %v", err)
		}
		if da.count != 3 || da.array[1] != 2 {
			t.Errorf("Insert position failed, got array=%v", da.array)
		}

		err = da.Insert(4, 5)
		if err == nil {
			t.Error("Expected error for invalid index")
		}
	})

	t.Run("Remove", func(t *testing.T) {
		da := DynArray[int]{}
		da.Init()
		for i := 0; i < 10; i++ {
			da.Append(i)
		}
		initialCapacity := da.capacity
		for i := 0; i < 6; i++ {
			err := da.Remove(0)
			if err != nil {
				t.Errorf("Remove failed with error: %v", err)
			}
		}

		if da.count != 4 {
			t.Errorf("Remove count failed, got count=%d", da.count)
		}

		if da.capacity >= initialCapacity && initialCapacity > 16 {
			t.Errorf("Remove resize failed, capacity didn't decrease")
		}

		err := da.Remove(10)
		if err == nil {
			t.Error("Expected error for invalid index")
		}
	})

	t.Run("GetItem", func(t *testing.T) {
		da := DynArray[string]{}
		da.Init()
		da.Append("test")
		val, err := da.GetItem(0)
		if err != nil || val != "test" {
			t.Errorf("GetItem failed, got val=%v, err=%v", val, err)
		}

		_, err = da.GetItem(1)
		if err == nil {
			t.Error("Expected error for invalid index")
		}
	})

	t.Run("Edge cases", func(t *testing.T) {
		da := DynArray[float64]{}
		da.Init()
		da.MakeArray(10)
		if da.capacity != 16 {
			t.Errorf("MakeArray min size failed, got capacity=%d", da.capacity)
		}

		for i := 0; i < 16; i++ {
			da.Append(1.1)
		}
		for i := 0; i < 12; i++ {
			err := da.Remove(0)
			if err != nil {
				return
			}
		}
		if da.capacity != 16 {
			t.Errorf("Remove min size failed, got capacity=%d", da.capacity)
		}
	})
}

func TestBankArray(t *testing.T) {
	ba := NewBankArray[int]()

	t.Run("Append and Get", func(t *testing.T) {
		for i := 0; i < 10; i++ {
			ba.Append(i)
		}

		for i := 0; i < 10; i++ {
			val, err := ba.Get(i)
			if err != nil || val != i {
				t.Errorf("Expected %d, got %d, error: %v", i, val, err)
			}
		}
	})

	t.Run("Remove and resize", func(t *testing.T) {
		initialCapacity := ba.capacity

		for i := 0; i < 7; i++ {
			err := ba.Remove(0)
			if err != nil {
				t.Errorf("Remove failed: %v", err)
			}
		}

		if ba.size != 3 {
			t.Errorf("Expected size 3, got %d", ba.size)
		}

		if ba.capacity >= initialCapacity {
			t.Error("Array should have been resized down")
		}
	})
}

func TestMultiArray(t *testing.T) {
	t.Run("Create and access", func(t *testing.T) {
		ma, err := NewMultiArray[int](3, 2, 3, 4)
		if err != nil {
			t.Fatalf("Creation failed: %v", err)
		}

		err = ma.Set(42, 1, 2, 3)
		if err != nil {
			t.Errorf("Set failed: %v", err)
		}

		val, err := ma.Get(1, 2, 3)
		if err != nil || val != 42 {
			t.Errorf("Get failed, expected 42, got %d, error: %v", val, err)
		}
	})

	t.Run("Resize", func(t *testing.T) {
		ma, err := NewMultiArray[int](2, 3, 3)
		if err != nil {
			t.Fatalf("Creation failed: %v", err)
		}

		for i := 0; i < 3; i++ {
			for j := 0; j < 3; j++ {
				err := ma.Set(i*10+j, i, j)
				if err != nil {
					return
				}
			}
		}

		err = ma.Resize(4, 4)
		if err != nil {
			t.Fatalf("Resize failed: %v", err)
		}

		for i := 0; i < 3; i++ {
			for j := 0; j < 3; j++ {
				val, err := ma.Get(i, j)
				if err != nil || val != i*10+j {
					t.Errorf("After resize, expected %d at (%d,%d), got %d", i*10+j, i, j, val)
				}
			}
		}
	})
}
