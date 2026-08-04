from time import perf_counter

import pytest

from power_set import PowerSet
from power_set_2 import Bag, PowerSet as ExtendedPowerSet, intersection_many


def build_set(*values, set_class=PowerSet):
    result = set_class()
    list(map(result.put, values))

    return result


def assert_set(power_set, expected_values):
    assert power_set.size() == len(expected_values)
    assert all(map(power_set.get, expected_values))


def test_put_and_get():
    power_set = PowerSet()

    power_set.put('value')
    power_set.put('value')

    assert power_set.size() == 1
    assert power_set.get('value') is True
    assert power_set.get('missing') is False


def test_remove():
    power_set = build_set(1, 2, 3)

    assert power_set.remove(2) is True
    assert power_set.remove(2) is False
    assert_set(power_set, [1, 3])


def test_intersection():
    left = build_set(1, 2, 3)
    right = build_set(2, 3, 4)
    disjoint = build_set(5, 6)

    assert_set(left.intersection(right), [2, 3])
    assert_set(left.intersection(disjoint), [])


def test_union():
    left = build_set(1, 2)
    right = build_set(2, 3)
    empty = PowerSet()

    assert_set(left.union(right), [1, 2, 3])
    assert_set(left.union(empty), [1, 2])
    assert_set(empty.union(right), [2, 3])


def test_difference():
    left = build_set(1, 2, 3)
    right = build_set(2, 3, 4)
    same = build_set(1, 2, 3)

    assert_set(left.difference(right), [1])
    assert_set(left.difference(same), [])


def test_issubset():
    current = build_set(1, 2, 3)
    subset = build_set(1, 2)
    superset = build_set(1, 2, 3, 4)
    partial = build_set(2, 4)

    assert current.issubset(subset) is True
    assert current.issubset(superset) is False
    assert current.issubset(partial) is False
    assert current.issubset(PowerSet()) is True


def test_equals():
    left = build_set(1, 2, 3)
    equal = build_set(3, 2, 1)
    different = build_set(1, 2, 4)

    assert left.equals(equal) is True
    assert equal.equals(left) is True
    assert left.equals(different) is False
    assert left.equals(build_set(1, 2)) is False


def test_large_sets_performance():
    started_at = perf_counter()
    left = build_set(*range(20_000))
    right = build_set(*range(10_000, 30_000))
    intersection = left.intersection(right)
    union = left.union(right)
    difference = left.difference(right)
    elapsed = perf_counter() - started_at

    assert intersection.size() == 10_000
    assert union.size() == 30_000
    assert difference.size() == 10_000
    assert elapsed < 2


def test_cartesian_product():
    left = build_set(1, 2, set_class=ExtendedPowerSet)
    right = build_set('a', 'b', set_class=ExtendedPowerSet)
    result = left.cartesian_product(right)

    assert isinstance(result, ExtendedPowerSet)
    assert_set(result, [(1, 'a'), (1, 'b'), (2, 'a'), (2, 'b')])
    assert left.cartesian_product(ExtendedPowerSet()).size() == 0


def test_intersection_many():
    first = build_set(1, 2, 3, 4)
    second = build_set(2, 3, 4, 5)
    third = build_set(0, 2, 4, 6)
    fourth = build_set(2, 4, 8)

    assert_set(
        intersection_many([first, second, third, fourth]),
        [2, 4],
    )

    with pytest.raises(ValueError, match='three'):
        intersection_many([first, second])


def test_bag():
    bag = Bag()

    list(map(bag.add, ('apple', 'apple', 'banana', 'apple')))

    assert dict(bag.get_frequencies()) == {'apple': 3, 'banana': 1}
    assert bag.size() == 4
    assert bag.remove('apple') is True
    assert dict(bag.get_frequencies()) == {'apple': 2, 'banana': 1}
    assert bag.remove('banana') is True
    assert bag.remove('banana') is False
    assert bag.size() == 2
