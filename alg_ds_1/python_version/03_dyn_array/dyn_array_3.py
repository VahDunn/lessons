import pytest

from dyn_array import DynArray
from dyn_array_2 import BankDynArray, MultiDynArray


def array_values(array):
    return [array[i] for i in range(len(array))]


def build_array(*values):
    array = DynArray()

    for value in values:
        array.append(value)

    return array


def test_insert_without_resize():
    array = build_array(1, 3)

    array.insert(1, 2)
    array.insert(0, 0)
    array.insert(len(array), 4)

    assert array_values(array) == [0, 1, 2, 3, 4]
    assert array.count == 5
    assert array.capacity == 16


def test_insert_with_resize():
    array = build_array(*range(16))

    array.insert(8, 'new')

    assert array_values(array) == list(range(8)) + ['new'] + list(range(8, 16))
    assert array.count == 17
    assert array.capacity == 32


@pytest.mark.parametrize('index', (-1, 3))
def test_insert_rejects_invalid_index(index):
    array = build_array(1, 2)

    with pytest.raises(IndexError, match='Index is out of bounds'):
        array.insert(index, 10)

    assert array_values(array) == [1, 2]
    assert array.capacity == 16


def test_delete_without_resize():
    array = build_array(*range(16))

    array.delete(7)

    assert array_values(array) == list(range(7)) + list(range(8, 16))
    assert array.count == 15
    assert array.capacity == 16


def test_delete_shrinks_below_half_full():
    array = build_array(*range(17))

    array.delete(0)
    assert array.count == 16
    assert array.capacity == 32

    array.delete(0)
    assert array_values(array) == list(range(2, 17))
    assert array.count == 15
    assert array.capacity == 21


def test_delete_keeps_minimum_capacity():
    array = build_array(*range(17))

    while len(array) > 0:
        array.delete(0)

    assert array_values(array) == []
    assert array.count == 0
    assert array.capacity == 16


@pytest.mark.parametrize('index', (-1, 2))
def test_delete_rejects_invalid_index(index):
    array = build_array(1, 2)

    with pytest.raises(IndexError, match='Index is out of bounds'):
        array.delete(index)

    assert array_values(array) == [1, 2]
    assert array.capacity == 16


def test_delete_rejects_index_in_empty_array():
    array = DynArray()

    with pytest.raises(IndexError, match='Index is out of bounds'):
        array.delete(0)


def test_bank_array_keeps_non_negative_balance():
    array = BankDynArray()

    for value in range(5000):
        array.append(value)
        assert array.balance >= 0

    assert [array[i] for i in range(len(array))] == list(range(5000))
    assert array.capacity == 8192
    assert array.charged_cost == 3 * len(array)
    assert array.balance == array.charged_cost - array.actual_cost


@pytest.mark.parametrize('index', (-1, 1))
def test_bank_array_rejects_invalid_index(index):
    array = BankDynArray()
    array.append('value')

    with pytest.raises(IndexError, match='Index is out of bounds'):
        _ = array[index]


def test_multidimensional_array_get_and_set():
    array = MultiDynArray(3, 2, 3, 4)

    assert len(array) == 24
    assert array.shape == (2, 3, 4)
    assert isinstance(array.array, list)
    assert isinstance(array.array[0], list)
    assert isinstance(array.array[0][0], list)
    assert array[1, 2, 3] is None

    array[1, 2, 3] = 'value'

    assert array[1, 2, 3] == 'value'
    assert array.array[1][2][3] == 'value'


def test_multidimensional_array_expands_required_dimensions():
    array = MultiDynArray(3, 2, 2, 2)
    preserved_value = object()
    new_value = object()
    array[1, 1, 1] = preserved_value

    array[4, 2, 7] = new_value

    assert array.shape == (8, 4, 8)
    assert len(array) == 256
    assert array[1, 1, 1] is preserved_value
    assert array[4, 2, 7] is new_value
    assert array[7, 3, 7] is None


def test_multidimensional_array_resize_preserves_intersection():
    array = MultiDynArray(2, (2, 3))
    first_value = object()
    removed_value = object()
    array[0, 0] = first_value
    array[1, 2] = removed_value

    array.resize(4, 5)

    assert array.shape == (4, 5)
    assert array[0, 0] is first_value
    assert array[1, 2] is removed_value

    array.resize(1, 2)

    assert array.shape == (1, 2)
    assert array[0, 0] is first_value

    with pytest.raises(IndexError, match='Index is out of bounds'):
        _ = array[1, 2]


def test_one_dimensional_array_uses_regular_index():
    array = MultiDynArray(1, 2)

    array[3] = 'value'

    assert array.shape == (4,)
    assert array[3] == 'value'


@pytest.mark.parametrize(
    ('dimensions', 'sizes', 'error'),
    (
        (0, (2,), ValueError),
        (2, (2,), ValueError),
        (2, (2, 0), ValueError),
        (2, (2, 1.5), TypeError),
    ),
)
def test_multidimensional_array_rejects_invalid_shape(
    dimensions,
    sizes,
    error,
):
    with pytest.raises(error):
        MultiDynArray(dimensions, *sizes)


@pytest.mark.parametrize('index', ((-1, 0), (2, 0), (0,), (0, 0, 0)))
def test_multidimensional_array_rejects_invalid_read_index(index):
    array = MultiDynArray(2, 2, 2)

    with pytest.raises(IndexError):
        _ = array[index]


def test_multidimensional_array_rejects_negative_write_index():
    array = MultiDynArray(2, 2, 2)

    with pytest.raises(IndexError, match='Index is out of bounds'):
        array[-1, 0] = 'value'

    assert array.shape == (2, 2)

