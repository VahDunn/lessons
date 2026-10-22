from abc import ABC, abstractmethod


class Delivery(ABC):
    @abstractmethod
    def get_price(self) -> int:
        ...


class CourierDelivery(Delivery):
    def get_price(self) -> int:
        return 500


class PickupDelivery(Delivery):
    def get_price(self) -> int:
        return 0


class ExpressDelivery(Delivery):
    def get_price(self) -> int:
        return 1000


def print_delivery_price(delivery: Delivery) -> None:
    print(delivery.get_price())





# и вместо
if delivery_type == "courier":
    price = 500
elif delivery_type == "pickup":
    price = 0
elif delivery_type == "express":
    price = 1000

# получаем, например,

print_delivery_price(CourierDelivery())
print_delivery_price(PickupDelivery())
print_delivery_price(ExpressDelivery())

# Аналогично с возвратом значения в зависимости от поля, и тд - вместо раздувания методов и добавления состояний
# расширяем иерархию.