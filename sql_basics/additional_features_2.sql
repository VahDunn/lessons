

9.4.1
SELECT
    c1.CustomerID  AS Customer1,
    c2.CustomerID  AS Customer2,
FROM Customers c1
         JOIN Customers c2
              ON c1.CustomerID < c2.CustomerID
WHERE c1.Region IS NULL
  AND c2.Region IS NULL;

9.4.2
SELECT *
FROM Orders o
WHERE o.CustomerID IN (
    SELECT c.CustomerID
    FROM Customers c
    WHERE c.Region IS NOT NULL AND LTRIM(RTRIM(c.Region)) <> ''
);

9.4.3
SELECT *
FROM Orders
WHERE Freight > ALL (SELECT UnitPrice FROM Products);