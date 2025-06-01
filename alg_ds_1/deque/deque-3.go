package main

import (
	"os"
	"testing"
)

func TestDeque(t *testing.T) {
	t.Run("Empty deque", func(t *testing.T) {
		d := Deque[int]{}
		if d.Size() != 0 {
			t.Errorf("Init failed, got count=%d, want 0", d.Size())
		}

		_, err := d.RemoveFront()
		if err == nil {
			t.Error("Expected error when removing from empty deque")
		}

		_, err = d.RemoveTail()
		if err == nil {
			t.Error("Expected error when removing from empty deque")
		}
	})

	t.Run("AddFront and RemoveFront", func(t *testing.T) {
		d := Deque[int]{}
		d.AddFront(1)
		d.AddFront(2)

		if d.Size() != 2 {
			t.Errorf("Append failed, got count=%d, want 2", d.Size())
		}

		val, err := d.RemoveFront()
		if err != nil {
			t.Errorf("RemoveFront failed with error: %v", err)
		}
		if val != 2 {
			t.Errorf("RemoveFront value failed, got %d, want 2", val)
		}

		val, err = d.RemoveFront()
		if err != nil {
			t.Errorf("RemoveFront failed with error: %v", err)
		}
		if val != 1 {
			t.Errorf("RemoveFront value failed, got %d, want 1", val)
		}

		if d.Size() != 0 {
			t.Errorf("Size after remove failed, got %d, want 0", d.Size())
		}
	})

	t.Run("AddTail and RemoveTail", func(t *testing.T) {
		d := Deque[string]{}
		d.AddTail("a")
		d.AddTail("b")

		if d.Size() != 2 {
			t.Errorf("Append failed, got count=%d, want 2", d.Size())
		}

		val, err := d.RemoveTail()
		if err != nil {
			t.Errorf("RemoveTail failed with error: %v", err)
		}
		if val != "b" {
			t.Errorf("RemoveTail value failed, got '%s', want 'b'", val)
		}

		val, err = d.RemoveTail()
		if err != nil {
			t.Errorf("RemoveTail failed with error: %v", err)
		}
		if val != "a" {
			t.Errorf("RemoveTail value failed, got '%s', want 'a'", val)
		}

		if d.Size() != 0 {
			t.Errorf("Size after remove failed, got %d, want 0", d.Size())
		}
	})

	t.Run("Mixed operations", func(t *testing.T) {
		d := Deque[int]{}
		d.AddFront(1)
		d.AddTail(2)
		d.AddFront(0)
		d.AddTail(3)

		if d.Size() != 4 {
			t.Errorf("Mixed operations count failed, got %d, want 4", d.Size())
		}

		val, err := d.RemoveFront()
		if err != nil {
			t.Errorf("RemoveFront failed with error: %v", err)
		}
		if val != 0 {
			t.Errorf("RemoveFront value failed, got %d, want 0", val)
		}

		val, err = d.RemoveTail()
		if err != nil {
			t.Errorf("RemoveTail failed with error: %v", err)
		}
		if val != 3 {
			t.Errorf("RemoveTail value failed, got %d, want 3", val)
		}

		val, err = d.RemoveFront()
		if err != nil {
			t.Errorf("RemoveFront failed with error: %v", err)
		}
		if val != 1 {
			t.Errorf("RemoveFront value failed, got %d, want 1", val)
		}

		val, err = d.RemoveTail()
		if err != nil {
			t.Errorf("RemoveTail failed with error: %v", err)
		}
		if val != 2 {
			t.Errorf("RemoveTail value failed, got %d, want 2", val)
		}

		if d.Size() != 0 {
			t.Errorf("Size after mixed operations failed, got %d, want 0", d.Size())
		}
	})

	t.Run("Single element", func(t *testing.T) {
		d := Deque[float64]{}
		d.AddFront(3.14)

		if d.Size() != 1 {
			t.Errorf("Single element count failed, got %d, want 1", d.Size())
		}

		val, err := d.RemoveTail()
		if err != nil {
			t.Errorf("RemoveTail failed with error: %v", err)
		}
		if val != 3.14 {
			t.Errorf("RemoveTail value failed, got %f, want 3.14", val)
		}

		if d.Size() != 0 {
			t.Errorf("Size after remove failed, got %d, want 0", d.Size())
		}

		// Add again and remove from front
		d.AddTail(2.71)
		val, err = d.RemoveFront()
		if err != nil {
			t.Errorf("RemoveFront failed with error: %v", err)
		}
		if val != 2.71 {
			t.Errorf("RemoveFront value failed, got %f, want 2.71", val)
		}
	})

	t.Run("Complex type", func(t *testing.T) {
		type person struct {
			name string
			age  int
		}

		d := Deque[person]{}
		d.AddFront(person{"Alice", 30})
		d.AddTail(person{"Bob", 25})

		p, err := d.RemoveFront()
		if err != nil {
			t.Errorf("RemoveFront failed with error: %v", err)
		}
		if p.name != "Alice" || p.age != 30 {
			t.Errorf("RemoveFront value failed, got %s/%d, want Alice/30", p.name, p.age)
		}

		p, err = d.RemoveTail()
		if err != nil {
			t.Errorf("RemoveTail failed with error: %v", err)
		}
		if p.name != "Bob" || p.age != 25 {
			t.Errorf("RemoveTail value failed, got %s/%d, want Bob/25", p.name, p.age)
		}
	})

	t.Run("Edge cases", func(t *testing.T) {
		d := Deque[int]{}
		for i := 0; i < 100; i++ {
			d.AddFront(i)
		}

		if d.Size() != 100 {
			t.Errorf("Large add count failed, got %d, want 100", d.Size())
		}

		for i := 0; i < 100; i++ {
			_, err := d.RemoveTail()
			if err != nil {
				t.Errorf("RemoveTail failed with error: %v", err)
			}
		}

		if d.Size() != 0 {
			t.Errorf("Size after large remove failed, got %d, want 0", d.Size())
		}
	})
}

func TestIsPalindrome(t *testing.T) {
	tests := []struct {
		name     string
		input    string
		expected bool
	}{
		{"empty string", "", true},
		{"single character", "a", true},
		{"simple palindrome", "madam", true},
		{"complex palindrome", "A man, a plan, a canal: Panama", true},
		{"not palindrome", "hello", false},
		{"with spaces", "was it a car or a cat i saw", true},
		{"mixed case", "RaceCar", true},
		{"numbers", "12321", true},
		{"numbers not palindrome", "12345", false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := IsPalindrome(tt.input)
			if result != tt.expected {
				t.Errorf("IsPalindrome(%q) = %v, want %v", tt.input, result, tt.expected)
			}
		})
	}
}

func TestMinDeque(t *testing.T) {
	t.Run("Basic operations", func(t *testing.T) {
		md := MinDeque{}

		_, err := md.GetMin()
		if err == nil {
			t.Error("Expected error for empty deque")
		}

		md.AddTail(3)
		checkMin(t, &md, 3)

		md.AddTail(1)
		checkMin(t, &md, 1)

		md.AddTail(2)
		checkMin(t, &md, 1)

		md.AddFront(0)
		checkMin(t, &md, 0)

		val, err := md.RemoveFront()
		if err != nil || val != 0 {
			t.Errorf("RemoveFront() = %d, %v, want 0, nil", val, err)
		}
		checkMin(t, &md, 1)

		val, err = md.RemoveTail()
		if err != nil || val != 2 {
			t.Errorf("RemoveTail() = %d, %v, want 2, nil", val, err)
		}
		checkMin(t, &md, 1)

		val, err = md.RemoveTail()
		if err != nil || val != 1 {
			t.Errorf("RemoveTail() = %d, %v, want 1, nil", val, err)
		}
		checkMin(t, &md, 3)
	})

	t.Run("Duplicate minimums", func(t *testing.T) {
		md := MinDeque{}

		md.AddTail(2)
		md.AddTail(1)
		md.AddTail(1)
		md.AddTail(3)
		checkMin(t, &md, 1)

		// Remove non-min element
		val, err := md.RemoveTail()
		if err != nil || val != 3 {
			t.Errorf("RemoveTail() = %d, %v, want 3, nil", val, err)
		}
		checkMin(t, &md, 1)

		// Remove one of duplicate mins
		val, err = md.RemoveTail()
		if err != nil || val != 1 {
			t.Errorf("RemoveTail() = %d, %v, want 1, nil", val, err)
		}
		checkMin(t, &md, 1)

		// Remove last min
		val, err = md.RemoveTail()
		if err != nil || val != 1 {
			t.Errorf("RemoveTail() = %d, %v, want 1, nil", val, err)
		}
		checkMin(t, &md, 2)
	})
}

func checkMin(t *testing.T, md *MinDeque, expected int) {
	t.Helper()
	min, err := md.GetMin()
	if err != nil {
		t.Fatalf("GetMin failed: %v", err)
	}
	if min != expected {
		t.Errorf("GetMin() = %d, want %d", min, expected)
	}
}

func TestArrayDeque(t *testing.T) {
	t.Run("basic operations", func(t *testing.T) {
		ad := ArrayDeque[int]{}
		ad.AddFront(1)
		ad.AddTail(2)
		ad.AddFront(0)

		if ad.Size() != 3 {
			t.Errorf("Size() = %d, want 3", ad.Size())
		}

		val, err := ad.RemoveFront()
		if err != nil {
			t.Fatalf("RemoveFront failed: %v", err)
		}
		if val != 0 {
			t.Errorf("RemoveFront() = %d, want 0", val)
		}

		val, err = ad.RemoveTail()
		if err != nil {
			t.Fatalf("RemoveTail failed: %v", err)
		}
		if val != 2 {
			t.Errorf("RemoveTail() = %d, want 2", val)
		}

		val, err = ad.RemoveFront()
		if err != nil {
			t.Fatalf("RemoveFront failed: %v", err)
		}
		if val != 1 {
			t.Errorf("RemoveFront() = %d, want 1", val)
		}

		if ad.Size() != 0 {
			t.Errorf("Size() = %d, want 0", ad.Size())
		}
	})

	t.Run("resizing", func(t *testing.T) {
		ad := ArrayDeque[int]{}
		for i := 0; i < 10; i++ {
			ad.AddTail(i)
		}

		if ad.Size() != 10 {
			t.Errorf("Size() = %d, want 10", ad.Size())
		}

		for i := 0; i < 10; i++ {
			val, err := ad.RemoveFront()
			if err != nil {
				t.Fatalf("RemoveFront failed: %v", err)
			}
			if val != i {
				t.Errorf("RemoveFront() = %d, want %d", val, i)
			}
		}

		if ad.Size() != 0 {
			t.Errorf("Size() = %d, want 0", ad.Size())
		}
	})

	t.Run("mixed operations with resizing", func(t *testing.T) {
		ad := ArrayDeque[int]{}
		for i := 0; i < 5; i++ {
			ad.AddFront(i)
			ad.AddTail(i + 5)
		}

		if ad.Size() != 10 {
			t.Errorf("Size() = %d, want 10", ad.Size())
		}

		for i := 4; i >= 0; i-- {
			val, err := ad.RemoveFront()
			if err != nil {
				t.Fatalf("RemoveFront failed: %v", err)
			}
			if val != i {
				t.Errorf("RemoveFront() = %d, want %d", val, i)
			}
		}

		for i := 9; i >= 5; i-- {
			val, err := ad.RemoveTail()
			if err != nil {
				t.Fatalf("RemoveTail failed: %v", err)
			}
			if val != i {
				t.Errorf("RemoveTail() = %d, want %d", val, i)
			}
		}

		if ad.Size() != 0 {
			t.Errorf("Size() = %d, want 0", ad.Size())
		}
	})

	t.Run("empty deque", func(t *testing.T) {
		ad := ArrayDeque[int]{}
		_, err := ad.RemoveFront()
		if err == nil {
			t.Error("Expected error for empty deque")
		}

		_, err = ad.RemoveTail()
		if err == nil {
			t.Error("Expected error for empty deque")
		}
	})
}
