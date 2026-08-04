from functools import reduce

import pytest

from bloom_filter import BloomFilter
from bloom_filter_2 import (
    CountingBloomFilter,
    merge_filters,
    recover_possible_values,
)


BASE_VALUE = '0123456789'
TEST_VALUES = tuple(map(
    lambda index: BASE_VALUE[index:] + BASE_VALUE[:index],
    range(10),
))


def build_filter(*values, filter_class=BloomFilter, filter_len=32):
    bloom_filter = filter_class(filter_len)
    list(map(bloom_filter.add, values))

    return bloom_filter


def test_hash_functions():
    bloom_filter = BloomFilter(32)
    value = '0123456789'
    expected_hash1 = reduce(
        lambda result, symbol: (result * 17 + ord(symbol)) % 32,
        value,
        0,
    )
    expected_hash2 = reduce(
        lambda result, symbol: (result * 223 + ord(symbol)) % 32,
        value,
        0,
    )

    assert bloom_filter.hash1(value) == expected_hash1
    assert bloom_filter.hash2(value) == expected_hash2
    assert bloom_filter.hash1('') == 0
    assert bloom_filter.hash2('') == 0


def test_add_and_is_value():
    bloom_filter = BloomFilter(32)

    assert bloom_filter.is_value(TEST_VALUES[0]) is False

    list(map(bloom_filter.add, TEST_VALUES))

    assert all(map(bloom_filter.is_value, TEST_VALUES))
    assert isinstance(bloom_filter.bit_array, int)
    assert 0 <= bloom_filter.bit_array < 1 << bloom_filter.filter_len


def test_false_positive_rate():
    bloom_filter = build_filter(*TEST_VALUES)
    missing_values = tuple(map(
        lambda index: f'missing-{index}',
        range(1_000),
    ))
    false_positives = sum(map(bloom_filter.is_value, missing_values))

    assert false_positives < len(missing_values) // 2


def test_merge_filters():
    left = build_filter(*TEST_VALUES[:5])
    right = build_filter(*TEST_VALUES[5:])
    left_before_merge = left.bit_array
    right_before_merge = right.bit_array

    merged = merge_filters([left, right])

    assert merged.bit_array == left.bit_array | right.bit_array
    assert all(map(merged.is_value, TEST_VALUES))
    assert left.bit_array == left_before_merge
    assert right.bit_array == right_before_merge

    with pytest.raises(ValueError, match='same length'):
        merge_filters([left, BloomFilter(64)])

    with pytest.raises(ValueError, match='one filter'):
        merge_filters([])


def test_counting_bloom_filter_remove():
    bloom_filter = CountingBloomFilter(32)

    bloom_filter.add('alpha')
    bloom_filter.add('alpha')
    bloom_filter.add('beta')

    assert bloom_filter.remove('alpha') is True
    assert bloom_filter.is_value('alpha') is True
    assert bloom_filter.is_value('beta') is True
    assert bloom_filter.remove('alpha') is True
    assert bloom_filter.is_value('alpha') is False
    assert bloom_filter.is_value('beta') is True
    assert bloom_filter.remove('missing-value') is False


def test_recover_possible_values():
    original_values = TEST_VALUES[:5]
    bloom_filter = build_filter(*original_values)
    candidates = original_values + ('missing-1', 'missing-2', 'missing-3')
    recovered = recover_possible_values(bloom_filter, candidates)

    assert all(map(lambda value: value in recovered, original_values))
    assert all(map(bloom_filter.is_value, recovered))


def test_filter_length_validation():
    with pytest.raises(ValueError, match='positive'):
        BloomFilter(0)
