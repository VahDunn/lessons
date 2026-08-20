from typing import Any


class BaseRepo:
    def get_by_id(self, obj_id: int) -> Any:
        print(f"repo.get_by_id({obj_id})")

    def get(self, **filters: Any) -> list[Any]:
        print(f"repo.get({filters})")
        return []

    def create(self, data: dict[str, Any]) -> Any:
        print(f"repo.create({data})")

    def update(self, obj_id: int, data: dict[str, Any]) -> Any:
        print(f"repo.update({obj_id}, {data})")

    def delete(self, obj_id: int) -> None:
        print(f"repo.delete({obj_id})")


class BaseService:
    def __init__(self, repo: BaseRepo) -> None:
        self.repo = repo

    def get_by_id(self, obj_id: int) -> Any:
        return self.repo.get_by_id(obj_id)

    def get(self, **filters: Any) -> list[Any]:
        return self.repo.get(**filters)

    def create(self, data: dict[str, Any]) -> Any:
        return self.repo.create(data)

    def update(self, obj_id: int, data: dict[str, Any]) -> Any:
        return self.repo.update(obj_id, data)

    def delete(self, obj_id: int) -> None:
        return self.repo.delete(obj_id)


class AuditMixin:
    audit_resource: str

    def audit(self, action: str, obj_id: int | None = None) -> None:
        print(f"audit.{action}({self.audit_resource}, {obj_id})")


class UserService(BaseService, AuditMixin):
    audit_resource = "user"

    def get_by_id(self, obj_id: int) -> Any:
        print("UserService: custom get_by_id logic")
        result = super().get_by_id(obj_id)
        self.audit("get_by_id", obj_id)
        return result

    def create(self, data: dict[str, Any]) -> Any:
        print("UserService: validate user before create")

        if "email" not in data:
            raise ValueError("email is required")

        result = super().create(data)
        self.audit("create")
        return result

    def update(self, obj_id: int, data: dict[str, Any]) -> Any:
        print("UserService: custom update logic")
        result = super().update(obj_id, data)
        self.audit("update", obj_id)
        return result

    def delete(self, obj_id: int) -> None:
        print("UserService: check permissions before delete")
        super().delete(obj_id)
        self.audit("delete", obj_id)


class VirtualServerService(BaseService, AuditMixin):
    audit_resource = "virtual_server"

    def get_by_id(self, obj_id: int) -> Any:
        print("VirtualServerService: custom get_by_id logic")
        result = super().get_by_id(obj_id)
        self.audit("get_by_id", obj_id)
        return result

    def create(self, data: dict[str, Any]) -> Any:
        print("VirtualServerService: validate virtual server before create")

        if "image_id" not in data:
            raise ValueError("image_id is required")

        result = super().create(data)
        self.audit("create")
        return result

    def update(self, obj_id: int, data: dict[str, Any]) -> Any:
        print("VirtualServerService: custom update logic")
        result = super().update(obj_id, data)
        self.audit("update", obj_id)
        return result

    def delete(self, obj_id: int) -> None:
        print("VirtualServerService: check state before delete")
        super().delete(obj_id)
        self.audit("delete", obj_id)


# Рефлексия
# Вариант для ситуации, когда наследование "истинное", но надо расширить функционал.
# Здесь разобрался гораздо быстрее. Впрочем, подобные примеры я видел и ранее, особенно в джанге, поэтому
# особых проблем не составило. Однако, кажется, что такая схема должна применяться очень осторожно, лучше
# ее избегать, чтобы не случился хаос. И, судя по всему, потенциально может быть проблема с тем, что
# миксин не получится сделать совсем универсальным. Даже если мы все пишем на миксинах с нуля, есть
# достаточно высокий риск того, что где-то появится частный случай, который метод миксина обработать не может.
# А потом еще один, и еще (если мы конечно не оперируем очень узким набором очень конкретных типов со
# строго заданным поведением (что возможно, но сложно)). А уж если речь идет о системе, которая ранее без миксинов
# существовала - там вероятность превращается в действительность, потому что если миксин это не желание, а
# необходимость, я бы ожидал большого количества проблем с его встраиванием by design.


class ServiceHooksMixin:
    def before_get_by_id(self, obj_id: int) -> None:
        pass

    def before_create(self, data: dict[str, Any]) -> None:
        pass

    def before_update(self, obj_id: int, data: dict[str, Any]) -> None:
        pass

    def before_delete(self, obj_id: int) -> None:
        pass

    def get_by_id(self, obj_id: int) -> Any:
        self.before_get_by_id(obj_id)
        return super().get_by_id(obj_id)

    def create(self, data: dict[str, Any]) -> Any:
        self.before_create(data)
        return super().create(data)

    def update(self, obj_id: int, data: dict[str, Any]) -> Any:
        self.before_update(obj_id, data)
        return super().update(obj_id, data)

    def delete(self, obj_id: int) -> None:
        self.before_delete(obj_id)
        return super().delete(obj_id)


class UserServiceWithHooks(ServiceHooksMixin, BaseService):
    def before_get_by_id(self, obj_id: int) -> None:
        print("UserService: custom get_by_id logic")

    def before_create(self, data: dict[str, Any]) -> None:
        print("UserService: validate user before create")

        if "email" not in data:
            raise ValueError("email is required")

    def before_update(self, obj_id: int, data: dict[str, Any]) -> None:
        print("UserService: custom update logic")

    def before_delete(self, obj_id: int) -> None:
        print("UserService: check permissions before delete")


class VirtualServerServiceWithHooks(ServiceHooksMixin, BaseService):
    def before_get_by_id(self, obj_id: int) -> None:
        print("VirtualServerService: custom get_by_id logic")

    def before_create(self, data: dict[str, Any]) -> None:
        print("VirtualServerService: validate virtual server before create")

        if "image_id" not in data:
            raise ValueError("image_id is required")

    def before_update(self, obj_id: int, data: dict[str, Any]) -> None:
        print("VirtualServerService: custom update logic")

    def before_delete(self, obj_id: int) -> None:
        print("VirtualServerService: check state before delete")


# Значительно более корявая реализация, которая позволяет имплементировать родительские методы без
# "истинного" наследования. Попробовал сделать, так сказать, реверанс в сторону предыдущего задания.
# Оказалось, это возможно, но от чтения написанного собой же кода у меня начинает болеть голова.
# То есть мы переопределяем метод миксина, наделяя новым функционалом наследуемый "базовый" метод.