import ctypes


# Задание на курсе: 3
# Задача: 5
# Название: динамический массив на основе банковского метода
class BankDynArray:

    OPERATION_PRICE = 3

    def __init__(self):
        self.count = 0
        self.capacity = 16
        self.array = self.make_array(self.capacity)
        self.balance = 0
        self.charged_cost = 0
        self.actual_cost = 0

    def __len__(self):
        return self.count

    def make_array(self, new_capacity):
        return (new_capacity * ctypes.py_object)()

    def __getitem__(self, i):
        if i < 0 or i >= self.count:
            raise IndexError('Index is out of bounds')

        return self.array[i]

    def _pay(self, cost):
        self.actual_cost += cost
        self.balance -= cost

        if self.balance < 0:
            raise RuntimeError('Bank balance cannot be negative')

    def _resize(self, new_capacity):
        new_array = self.make_array(new_capacity)

        for i in range(self.count):
            new_array[i] = self.array[i]

        self._pay(self.count)
        self.array = new_array
        self.capacity = new_capacity

    # Реальная сложность отдельной операции: O(n) при реаллокации.
    # Амортизированная сложность по банковскому методу: O(1).
    # Пространственная сложность: O(n).
    def append(self, itm):
        self.charged_cost += self.OPERATION_PRICE
        self.balance += self.OPERATION_PRICE

        if self.count == self.capacity:
            self._resize(2 * self.capacity)

        self.array[self.count] = itm
        self.count += 1
        self._pay(1)


# Задание на курсе: 3
# Задача: 6
# Название: многомерный динамический массив
class MultiDynArray:

    def __init__(self, dimensions, *sizes):
        sizes = self._unpack_sizes(sizes)

        if type(dimensions) is not int or dimensions <= 0:
            raise ValueError('Dimensions count must be a positive integer')

        if len(sizes) != dimensions:
            raise ValueError('Dimensions count does not match sizes count')

        self._validate_sizes(sizes)
        self.dimensions = dimensions
        self.shape = tuple(sizes)
        self.size = self._calculate_size(self.shape)
        self.array = self.make_array(self.shape)

    def __len__(self):
        return self.size

    @staticmethod
    def _unpack_sizes(sizes):
        if len(sizes) == 1 and isinstance(sizes[0], (list, tuple)):
            return tuple(sizes[0])

        return tuple(sizes)

    @staticmethod
    def _validate_sizes(sizes):
        if any(type(size) is not int for size in sizes):
            raise TypeError('Dimension sizes must be integers')

        if any(size <= 0 for size in sizes):
            raise ValueError('Dimension sizes must be positive')

    @staticmethod
    def _calculate_size(shape):
        size = 1

        for dimension_size in shape:
            size *= dimension_size

        return size

    def make_array(self, sizes):
        if len(sizes) == 1:
            return [None] * sizes[0]

        next_sizes = sizes[1:]

        return [
            self.make_array(next_sizes)
            for _ in range(sizes[0])
        ]

    def _normalize_indices(self, indices):
        if not isinstance(indices, tuple):
            indices = (indices,)

        if len(indices) != self.dimensions:
            raise IndexError('Wrong number of indices')

        if any(type(index) is not int for index in indices):
            raise TypeError('Indices must be integers')

        return indices

    @staticmethod
    def _expanded_size(current_size, index):
        new_size = current_size

        while index >= new_size:
            new_size *= 2

        return new_size

    def _copy_values(
        self,
        old_array,
        new_array,
        common_shape,
        dimension=0,
    ):
        if dimension == self.dimensions - 1:
            for index in range(common_shape[dimension]):
                new_array[index] = old_array[index]

            return

        for index in range(common_shape[dimension]):
            self._copy_values(
                old_array[index],
                new_array[index],
                common_shape,
                dimension + 1,
            )

    # Временная сложность: O(n) - линейно по количеству измерений
    # Пространственная сложность: O(1).
    def __getitem__(self, indices):
        indices = self._normalize_indices(indices)

        if any(
            index < 0 or index >= dimension_size
            for index, dimension_size in zip(indices, self.shape)
        ):
            raise IndexError('Index is out of bounds')

        current_array = self.array

        for index in indices:
            current_array = current_array[index]

        return current_array

    # Без расширения: O(d), с расширением: O(n * d).
    # Пространственная сложность при расширении: O(n), n - новый размер.
    def __setitem__(self, indices, value):
        indices = self._normalize_indices(indices)

        if any(index < 0 for index in indices):
            raise IndexError('Index is out of bounds')

        new_shape = tuple(
            self._expanded_size(dimension_size, index)
            for index, dimension_size in zip(indices, self.shape)
        )

        if new_shape != self.shape:
            self.resize(*new_shape)

        current_array = self.array

        for index in indices[:-1]:
            current_array = current_array[index]

        current_array[indices[-1]] = value

    # Временная сложность: O(n + m).
    # Пространственная сложность: O(n), n - новый размер.
    def resize(self, *new_sizes):
        new_sizes = self._unpack_sizes(new_sizes)

        if len(new_sizes) != self.dimensions:
            raise ValueError('Dimensions count does not match sizes count')

        self._validate_sizes(new_sizes)
        new_shape = tuple(new_sizes)

        if new_shape == self.shape:
            return

        new_size = self._calculate_size(new_shape)
        new_array = self.make_array(new_shape)
        common_shape = tuple(
            min(old_size, new_size)
            for old_size, new_size in zip(self.shape, new_shape)
        )
        self._copy_values(
            self.array,
            new_array,
            common_shape,
        )

        self.shape = new_shape
        self.size = new_size
        self.array = new_array



# Рефлексия
# Рад, что получилось быстро и (относительно) беспроблемно сделать мерж двух списков, сортировка показалась сложнее.
# На прошлом подходе изрядно помучился, возможно из-за go.
# Решал аналогичную задачу для n списков на литкоде, показалась интересной.

# Об многомерный динамический массив второй раз спотыкаюсь. Не получается с наскока интуитивно представить.
# Обычно я достаточно легко и компактно представляю себе какие-либо функции, но из-за многомерности
# здесь сложнее. Однако, это заставило меня задуматься о данной структуре в другом ключе.
# Точнее, заставило задуматься не о самой структуре, а непосредственно о функции, которая ее задает.
# И все прошло гораздо легче, рекурсия помогла.
