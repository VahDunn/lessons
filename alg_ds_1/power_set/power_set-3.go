package main

import (
	"testing"
)

func TestPowerSet(t *testing.T) {
	t.Run("Init and Size", func(t *testing.T) {
		set := Init[int]()
		if set.Size() != 0 {
			t.Errorf("Expected size 0, got %d", set.Size())
		}
	})

	t.Run("Put and Get", func(t *testing.T) {
		set := Init[string]()
		set.Put("hello")
		set.Put("world")

		if !set.Get("hello") {
			t.Error("Expected 'hello' to be in set")
		}
		if !set.Get("world") {
			t.Error("Expected 'world' to be in set")
		}
		if set.Get("missing") {
			t.Error("Expected 'missing' not to be in set")
		}
		if set.Size() != 2 {
			t.Errorf("Expected size 2, got %d", set.Size())
		}
	})

	t.Run("Remove", func(t *testing.T) {
		set := Init[int]()
		set.Put(1)
		set.Put(2)

		if !set.Remove(1) {
			t.Error("Expected to remove 1")
		}
		if set.Remove(3) {
			t.Error("Expected not to remove 3")
		}
		if set.Get(1) {
			t.Error("Expected 1 to be removed")
		}
		if set.Size() != 1 {
			t.Errorf("Expected size 1, got %d", set.Size())
		}
	})

	t.Run("Intersection", func(t *testing.T) {
		set1 := Init[int]()
		set2 := Init[int]()
		set1.Put(1)
		set1.Put(2)
		set1.Put(3)
		set2.Put(2)
		set2.Put(3)
		set2.Put(4)

		intersection := set1.Intersection(set2)
		if intersection.Size() != 2 {
			t.Errorf("Expected intersection size 2, got %d", intersection.Size())
		}
		if !intersection.Get(2) || !intersection.Get(3) {
			t.Error("Intersection should contain 2 and 3")
		}
	})

	t.Run("Union", func(t *testing.T) {
		set1 := Init[string]()
		set2 := Init[string]()
		set1.Put("a")
		set1.Put("b")
		set2.Put("b")
		set2.Put("c")

		union := set1.Union(set2)
		if union.Size() != 3 {
			t.Errorf("Expected union size 3, got %d", union.Size())
		}
		if !union.Get("a") || !union.Get("b") || !union.Get("c") {
			t.Error("Union should contain a, b and c")
		}
	})

	t.Run("Difference", func(t *testing.T) {
		set1 := Init[int]()
		set2 := Init[int]()
		set1.Put(1)
		set1.Put(2)
		set1.Put(3)
		set2.Put(2)
		set2.Put(4)

		difference := set1.Difference(set2)
		if difference.Size() != 2 {
			t.Errorf("Expected difference size 2, got %d", difference.Size())
		}
		if !difference.Get(1) || !difference.Get(3) {
			t.Error("Difference should contain 1 and 3")
		}
	})

	t.Run("IsSubset", func(t *testing.T) {
		set1 := Init[int]()
		set2 := Init[int]()
		set1.Put(1)
		set1.Put(2)
		set1.Put(3)
		set2.Put(2)
		set2.Put(3)

		if !set1.IsSubset(set2) {
			t.Error("Expected set2 to be subset of set1")
		}

		set2.Put(4)
		if set1.IsSubset(set2) {
			t.Error("Expected set2 not to be subset of set1")
		}
	})

	t.Run("Equals", func(t *testing.T) {
		set1 := Init[string]()
		set2 := Init[string]()
		set1.Put("a")
		set1.Put("b")
		set2.Put("b")
		set2.Put("a")

		if !set1.Equals(set2) {
			t.Error("Expected sets to be equal")
		}

		set2.Put("c")
		if set1.Equals(set2) {
			t.Error("Expected sets not to be equal")
		}

		set3 := Init[string]()
		set3.Put("a")
		if set1.Equals(set3) {
			t.Error("Expected sets of different sizes not to be equal")
		}
	})

	t.Run("EmptySetOperations", func(t *testing.T) {
		empty := Init[float64]()
		nonEmpty := Init[float64]()
		nonEmpty.Put(1.1)
		nonEmpty.Put(2.2)

		// Intersection with empty
		intersection := empty.Intersection(nonEmpty)
		if intersection.Size() != 0 {
			t.Error("Intersection with empty set should be empty")
		}

		// Union with empty
		union := empty.Union(nonEmpty)
		if union.Size() != nonEmpty.Size() {
			t.Error("Union with empty set should equal non-empty set")
		}

		// Difference of empty
		diff := empty.Difference(nonEmpty)
		if diff.Size() != 0 {
			t.Error("Difference of empty set should be empty")
		}

		// IsSubset
		if !empty.IsSubset(empty) {
			t.Error("Empty set should be subset of itself")
		}
		if !nonEmpty.IsSubset(empty) {
			t.Error("Empty set should be subset of any set")
		}
	})
}
