10.4.1

SELECT Products.ProductName, [Order Details].UnitPrice
FROM Products
JOIN [Order Details]
      ON ProductID
WHERE [Order Details].UnitPrice < 20

10.4.2

За счет того, что при FULL JOIN берет все строки и "подставляет" к ним null в случае,
если пары к данной строке нет - получается заказ без заказчика/заказчик без заказа

10.4.3

SELECT *
FROM Products CROSS JOIN [Order Details]
WHERE Products.ProductID = [Order Details].ProductID;
Декартово произведение и поиск совпадений

10.4.4

SELECT p.ProductName, od.UnitPrice
FROM Products AS p
         INNER JOIN [Order Details] AS od
ON p.ProductID = od.ProductID;