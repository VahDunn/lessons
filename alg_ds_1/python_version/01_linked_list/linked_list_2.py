# Задание на курсе: 1
# Задача: 1.8
# Название: сумма соответствующих элементов двух связанных списков
# Временная сложность: O(n)
# Пространственная сложность: O(n)

from linked_list import LinkedList, Node


def sum_linked_lists(first_list, second_list):
    if first_list.len() != second_list.len():
        return None

    result = LinkedList()
    first_node = first_list.head
    second_node = second_list.head

    while first_node is not None:
        result.add_in_tail(Node(first_node.value + second_node.value))
        first_node = first_node.next
        second_node = second_node.next

    return result


# Рефлексия
# На родном питоне писать конечно поприятнее, чем на Go.
# В целом ничего сложного, по крайней мере, повторно. Доп. задание показалось легче, чем основное
#  (помучился с delete - забывал отсекать хвост, обложил тестами, ошибка нашлась).
#  Здесь вроде бы линейная скорость оптимальна.
#  Стало значительно легче думать, по сравнению с тем,
# что было год назад, тоже очень радует. В остальном, пожалуй, без сюрпризов.
