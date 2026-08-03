from hash_table import HashTable
from hash_table_2 import DynamicHashTable, MultiHashTable, SecureHashTable


def find_collisions(hash_table, count):
    target_slot = hash_table.hash_fun('target')
    values = []
    candidate = 0

    while len(values) < count:
        value = f'value-{candidate}'
        candidate += 1

        if hash_table.hash_fun(value) != target_slot:
            continue

        values.append(value)

    return values


def test_hash_fun():
    hash_table = HashTable(17, 3)

    assert hash_table.hash_fun('') == 0
    assert hash_table.hash_fun('consistent') == hash_table.hash_fun('consistent')

    for value in ('a', 'abc', 'строка', '123456'):
        assert 0 <= hash_table.hash_fun(value) < hash_table.size


def test_seek_slot():
    hash_table = HashTable(7, 3)
    values = find_collisions(hash_table, 8)
    first_slot = hash_table.hash_fun(values[0])

    for attempt, value in enumerate(values[:7]):
        expected_slot = (first_slot + attempt * hash_table.step) % hash_table.size
        assert hash_table.seek_slot(value) == expected_slot
        hash_table.put(value)

    assert hash_table.seek_slot(values[-1]) is None


def test_put():
    hash_table = HashTable(3, 1)

    first_slot = hash_table.put('first')
    second_slot = hash_table.put('second')
    third_slot = hash_table.put('third')

    assert hash_table.slots[first_slot] == 'first'
    assert hash_table.slots[second_slot] == 'second'
    assert hash_table.slots[third_slot] == 'third'
    assert len({first_slot, second_slot, third_slot}) == 3
    assert hash_table.put('overflow') is None


def test_find():
    hash_table = HashTable(7, 3)
    values = find_collisions(hash_table, 4)
    slots = [hash_table.put(value) for value in values[:3]]

    for value, slot in zip(values, slots):
        assert hash_table.find(value) == slot

    assert hash_table.find(values[-1]) is None
    assert hash_table.find('absent') is None


def test_dynamic_hash_table():
    hash_table = DynamicHashTable(4, 1, threshold=0.75)
    values = [f'value-{index}' for index in range(10)]

    for value in values[:3]:
        hash_table.put(value)

    assert hash_table.size == 4

    hash_table.put(values[3])
    assert hash_table.size == 8

    for value in values[4:]:
        hash_table.put(value)

    assert hash_table.size == 16
    assert hash_table.count == len(values)
    assert sum(value is not None for value in hash_table.slots) == len(values)

    for value in values:
        assert hash_table.find(value) is not None


def test_multi_hash_table():
    first_hash = lambda value: 0
    second_hash = lambda value: 1
    hash_table = MultiHashTable(
        7,
        steps=[2, 3],
        hash_functions=[first_hash, second_hash],
    )

    first_slot = hash_table.put('first')
    second_slot = hash_table.put('second')
    third_slot = hash_table.put('third')

    assert first_slot == 0
    assert second_slot == 1
    assert third_slot == 2
    assert hash_table.find('first') == first_slot
    assert hash_table.find('second') == second_slot
    assert hash_table.find('third') == third_slot
    assert hash_table.find('absent') is None


def test_secure_hash_table():
    base_table = HashTable(31, 3)
    collision_values = find_collisions(base_table, 12)
    secure_table = SecureHashTable(31, 3, salt='course-secret')
    other_salt_table = SecureHashTable(1009, 3, salt='other-secret')
    first_salt_table = SecureHashTable(1009, 3, salt='course-secret')

    assert len({base_table.hash_fun(value) for value in collision_values}) == 1
    assert len({secure_table.hash_fun(value) for value in collision_values}) > 1
    assert (
        first_salt_table.hash_fun('protected-value')
        != other_salt_table.hash_fun('protected-value')
    )

    for value in collision_values:
        slot = secure_table.put(value)
        assert slot is not None
        assert secure_table.find(value) == slot
