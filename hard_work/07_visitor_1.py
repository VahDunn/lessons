# Код все таки немного не "настоящий" (писал по воспоминаниям о структуре без реальной логики),
# но отражает ситуацию, с которой я столкнулся некоторое время назад.

from abc import ABC, abstractmethod
from typing import Any


# Базовый класс сервиса и репозитория, которым сервис пользуется.

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



# Наследники. Переопределяют методы родителя с сохранением сигнатур.
# В целом такой подход выглядит как антипаттерн, по крайней мере, я столкнулся
# с большим количеством обусловленных данным решением проблем на прошлой
# работе (код оттуда). Еще там был единственный контроллер, который брал из url
# название вызываемого класса и метода, чтобы "быстро и удобно" сделать инъекции зависимостей.
# Предполагалось, что у каждого сервиса будет всего 4 публичных метода и стандартный набор зависимостей.
# Как у людей с 10+ годами могла сохраниться такая наивность - до сих пор не понимаю.

class UserService(BaseService):
    def get_by_id(self, obj_id: int) -> Any:
        print("UserService: custom get_by_id logic")
        return self.repo.get_by_id(obj_id)

    def create(self, data: dict[str, Any]) -> Any:
        print("UserService: validate user before create")

        if "email" not in data:
            raise ValueError("email is required")

        return self.repo.create(data)

    def update(self, obj_id: int, data: dict[str, Any]) -> Any:
        print("UserService: custom update logic")
        return self.repo.update(obj_id, data)

    def delete(self, obj_id: int) -> None:
        print("UserService: check permissions before delete")
        return self.repo.delete(obj_id)


class VirtualServerService(BaseService):
    def get_by_id(self, obj_id: int) -> Any:
        print("VirtualServerService: custom get_by_id logic")
        return self.repo.get_by_id(obj_id)

    def create(self, data: dict[str, Any]) -> Any:
        print("VirtualServerService: validate virtual server before create")

        if "image_id" not in data:
            raise ValueError("image_id is required")

        return self.repo.create(data)

    def update(self, obj_id: int, data: dict[str, Any]) -> Any:
        print("VirtualServerService: custom update logic")
        return self.repo.update(obj_id, data)

    def delete(self, obj_id: int) -> None:
        print("VirtualServerService: check state before delete")
        return self.repo.delete(obj_id)


# Изначально предполагалось наследование через super(), но из-за специфики проекта.
# коллеги решили перейти на вот такое вот.



class ServiceVisitor(ABC):
    @abstractmethod
    def visit_user_service(self, service: UserService) -> Any:
        pass

    @abstractmethod
    def visit_virtual_server_service(
        self,
        service: VirtualServerService,
    ) -> Any:
        pass


class VisitableService(ABC):
    @abstractmethod
    def accept(self, visitor: ServiceVisitor) -> Any:
        pass


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


class UserService(BaseService, VisitableService):
    def accept(self, visitor: ServiceVisitor) -> Any:
        return visitor.visit_user_service(self)


class VirtualServerService(BaseService, VisitableService):
    def accept(self, visitor: ServiceVisitor) -> Any:
        return visitor.visit_virtual_server_service(self)


class GetByIdVisitor(ServiceVisitor):
    def __init__(self, obj_id: int) -> None:
        self.obj_id = obj_id

    def visit_user_service(self, service: UserService) -> Any:
        print("UserService: custom get_by_id logic")
        return super(UserService, service).get_by_id(self.obj_id)

    def visit_virtual_server_service(
        self,
        service: VirtualServerService,
    ) -> Any:
        print("VirtualServerService: custom get_by_id logic")
        return super(VirtualServerService, service).get_by_id(self.obj_id)


class CreateVisitor(ServiceVisitor):
    def __init__(self, data: dict[str, Any]) -> None:
        self.data = data

    def visit_user_service(self, service: UserService) -> Any:
        print("UserService: validate user before create")

        if "email" not in self.data:
            raise ValueError("email is required")

        return super(UserService, service).create(self.data)

    def visit_virtual_server_service(
        self,
        service: VirtualServerService,
    ) -> Any:
        print("VirtualServerService: validate virtual server before create")

        if "image_id" not in self.data:
            raise ValueError("image_id is required")

        return super(VirtualServerService, service).create(self.data)


class UpdateVisitor(ServiceVisitor):
    def __init__(self, obj_id: int, data: dict[str, Any]) -> None:
        self.obj_id = obj_id
        self.data = data

    def visit_user_service(self, service: UserService) -> Any:
        print("UserService: custom update logic")
        return super(UserService, service).update(self.obj_id, self.data)

    def visit_virtual_server_service(
        self,
        service: VirtualServerService,
    ) -> Any:
        print("VirtualServerService: custom update logic")
        return super(VirtualServerService, service).update(
            self.obj_id,
            self.data,
        )


class DeleteVisitor(ServiceVisitor):
    def __init__(self, obj_id: int) -> None:
        self.obj_id = obj_id

    def visit_user_service(self, service: UserService) -> None:
        print("UserService: check permissions before delete")
        return super(UserService, service).delete(self.obj_id)

    def visit_virtual_server_service(
        self,
        service: VirtualServerService,
    ) -> None:
        print("VirtualServerService: check state before delete")
        return super(VirtualServerService, service).delete(self.obj_id)

# Рефлексия
# Если правильно понял, как это решается.
# Понадобилось некоторое время, чтобы разобраться. Было совсем не очевидно, как это так сделать,
# чтобы не попасть в циркулирующие импорты, да и в целом как-то аккуратно. Но потом картинка сложилась. Вроде бы.
# Если честно, на текущих проектах не вижу особого смысла встраивать функциональность именно так,
# через дополнительный узел, находящийся как бы "сбоку" от основной линии наследования.
# Однако, теоретически такую ситуацию я представить могу. Особенно в контексте рассказа
# о прошлом проекте. Юнит-тестов в нем, разумеется, не было (по настоянию лида),
# и отсутствие непредсказуемого поведения (или, по крайней мере, выявленного непредсказуемого поведения)
# на момент сдачи я считаю удачным стечением обстоятельств
# для меня и неудачным для тех, кто после меня будет этот проект поддерживать.
# Стоит сказать, что в ситуации с хотя бы немного структурированным проектом на Python я бы, вероятно,
# в первую очередь попытался все же добавить стандартный вызов super().__init__().
# Однако, могу представить, насколько сложнее было бы провернуть что-то такое в ООП-ориентированных языках.