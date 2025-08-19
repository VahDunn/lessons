8.3.1

SELECT ProductName, CategoryName
FROM Products, Categories
WHERE Products.CategoryID = Categories.CategoryID;

8.3.2

SELECT Products.ProductName, [Order Details].UnitPrice
FROM Products, [Order Details]
WHERE Products.ProductID = [Order Details].ProductID AND [Order Details].UnitPrice < 20;


8.3.3
SELECT
    Products.ProductName,
    [Order Details].UnitPrice,
    Categories.CategoryName
FROM Products, [Order Details], Categories
WHERE Products.ProductID = [Order Details].ProductID
    AND Products.CategoryID = Categories.CategoryID
    AND [Order Details].UnitPrice < 20;