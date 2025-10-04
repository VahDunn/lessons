def build(input_list, start, end, index, res):
    if start >= end or index >= len(res):
        return
    mid = (start + end) // 2
    res[index] = input_list[mid]
    build(input_list, start, mid, 2 * index + 1, res)
    build(input_list, mid + 1, end, 2 * index + 2, res)

def GenerateBBSTArray(a):
    sorted_list = sorted(a)
    res = [None] * len(sorted_list)
    build(sorted_list, start=0, end=len(sorted_list), index=0, res=res)
    return res


# Задание 2 - сравнение эффективности
# Сложность - и там и там O log(n)
# но по памяти массив эффективнее, так как в нем переход к потомку реализуется
# вычислением. Однако, массив менее выгоден при динамически меняющихся данных.

