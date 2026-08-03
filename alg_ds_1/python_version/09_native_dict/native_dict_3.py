import pytest

from native_dict import NativeDictionary
from native_dict_2 import BitStringDictionary, OrderedDictionary


def test_put_new_and_existing_key():
    dictionary = NativeDictionary(7)

    slot = dictionary.put('key', 10)

    assert dictionary.slots[slot] == 'key'
    assert dictionary.values[slot] == 10

    updated_slot = dictionary.put('key', 20)

    assert updated_slot == slot
    assert dictionary.get('key') == 20
    assert dictionary.slots.count('key') == 1


def test_is_key():
    dictionary = NativeDictionary(7)
    dictionary.put('present', 10)

    assert dictionary.is_key('present') is True
    assert dictionary.is_key('missing') is False


def test_get():
    dictionary = NativeDictionary(7)
    dictionary.put('number', 0)
    dictionary.put('nothing', None)

    assert dictionary.get('number') == 0
    assert dictionary.get('nothing') is None
    assert dictionary.is_key('nothing') is True
    assert dictionary.get('missing') is None


def test_collisions_and_full_dictionary():
    dictionary = NativeDictionary(3)

    slots = list(map(
        lambda pair: dictionary.put(*pair),
        (('a', 1), ('d', 2), ('g', 3)),
    ))

    assert len(set(slots)) == 3
    assert list(map(dictionary.get, ('a', 'd', 'g'))) == [1, 2, 3]
    assert dictionary.put('j', 4) is None

    dictionary.put('d', 20)
    assert dictionary.get('d') == 20


def test_ordered_dictionary():
    dictionary = OrderedDictionary()

    list(map(
        lambda pair: dictionary.put(*pair),
        (('c', 3), ('a', 1), ('d', 4), ('b', 2)),
    ))

    assert dictionary.keys == ['a', 'b', 'c', 'd']
    assert list(map(dictionary.get, dictionary.keys)) == [1, 2, 3, 4]
    assert dictionary.is_key('c') is True
    assert dictionary.is_key('missing') is False
    assert dictionary.get('missing') is None

    dictionary.put('b', 20)
    assert dictionary.get('b') == 20

    assert dictionary.delete('c') is True
    assert dictionary.delete('c') is False
    assert dictionary.keys == ['a', 'b', 'd']


def test_bit_string_dictionary():
    dictionary = BitStringDictionary(4)

    assert dictionary.put('0000', 'zero') == 0
    assert dictionary.put('0011', 'three') == 3
    assert dictionary.put('1111', 'fifteen') == 15
    assert dictionary.get('0011') == 'three'
    assert dictionary.is_key('1111') is True
    assert dictionary.is_key('0101') is False

    dictionary.put('0011', 'updated')
    assert dictionary.get('0011') == 'updated'

    assert dictionary.delete('0011') is True
    assert dictionary.delete('0011') is False
    assert dictionary.get('0011') is None


def test_bit_string_dictionary_validates_keys():
    dictionary = BitStringDictionary(4)

    with pytest.raises(ValueError, match='length'):
        dictionary.put('101', 'short')

    with pytest.raises(ValueError, match='only 0 and 1'):
        dictionary.put('10a1', 'invalid')
