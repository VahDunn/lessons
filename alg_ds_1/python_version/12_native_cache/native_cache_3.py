import pytest

from native_cache import NativeCache


def test_put_get_and_hits():
    cache = NativeCache(5)
    slot = cache.put('key', 'value')

    assert cache.slots[slot] == 'key'
    assert cache.values[slot] == 'value'
    assert cache.hits[slot] == 0
    assert cache.get('key') == 'value'
    assert cache.get('key') == 'value'
    assert cache.hits[slot] == 2

    updated_slot = cache.put('key', 'updated')

    assert updated_slot == slot
    assert cache.hits[slot] == 2
    assert cache.get('key') == 'updated'
    assert cache.hits[slot] == 3


def test_is_key_and_missing_key():
    cache = NativeCache(5)
    slot = cache.put('present', None)

    assert cache.is_key('present') is True
    assert cache.is_key('missing') is False
    assert cache.get('missing') is None
    assert cache.hits[slot] == 0
    assert cache.get('present') is None
    assert cache.hits[slot] == 1


def test_collisions_and_least_frequently_used_eviction():
    cache = NativeCache(3)
    keys = ('a', 'd', 'g')

    slots = list(map(
        lambda pair: cache.put(*pair),
        zip(keys, (1, 2, 3)),
    ))

    assert len(set(slots)) == cache.size
    assert len(set(map(cache.hash_fun, keys))) == 1

    cache.get('a')
    cache.get('a')
    cache.get('d')

    evicted_slot = slots[keys.index('g')]
    inserted_slot = cache.put('j', 4)

    assert inserted_slot == evicted_slot
    assert cache.is_key('g') is False
    assert cache.is_key('j') is True
    assert cache.is_key('a') is True
    assert cache.is_key('d') is True
    assert cache.values[inserted_slot] == 4
    assert cache.hits[inserted_slot] == 0


def test_eviction_uses_current_hit_counts():
    cache = NativeCache(2)
    first_slot = cache.put('a', 1)
    second_slot = cache.put('c', 2)

    cache.get('a')
    cache.get('a')
    cache.get('c')
    cache.put('e', 3)

    assert cache.slots[first_slot] == 'a'
    assert cache.slots[second_slot] == 'e'
    assert cache.is_key('c') is False
    assert cache.hits[first_slot] == 2
    assert cache.hits[second_slot] == 0


def test_positive_cache_size():
    with pytest.raises(ValueError, match='positive'):
        NativeCache(0)
