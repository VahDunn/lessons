7.3.1
SELECT
    OrderID,
    ProductID,
    Quantity,
    UnitPrice,
    Discount,
    ROUND(Discount * 100.0, 2) AS DiscountPercent -- скидка в %
FROM [Order Details];

7.3.2
SELECT od.*
FROM [Order Details] AS od
WHERE (
    SELECT p.UnitsInStock
    FROM Products AS p
    WHERE p.ProductID = od.ProductID
    ) > 40;

7.3.3
SELECT od.*
FROM [Order Details] AS od
WHERE (
    SELECT p.UnitsInStock
    FROM Products AS p
    WHERE p.ProductID = od.ProductID
    ) > 40
  AND (
    SELECT o.Freight
    FROM Orders AS o
    WHERE o.OrderID = od.OrderID
    ) >= 50;