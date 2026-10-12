# Основной способ запретить переопределение - декоратор final. Именно тот, о котором я забыл в предыдущем
#  занятии.
# Однако, это справедливо только для работы с типизатором, в рантайме все отработает.

class General:
    @final
    def clone(self):
        print("General.clone")


class Any(General):
    def clone(self):  # ошибка
        print("Any.clone")