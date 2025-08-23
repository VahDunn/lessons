
11.5.2
SELECT *
FROM Customers AS c
         LEFT JOIN Orders AS o
                   ON c.CustomerID = o.CustomerID
WHERE o.OrderID IS NULL;


11.5.3
SELECT
    ContactName  AS PersonName,
    City,
    Country,
    'Customer'   AS GroupType
FROM Customers

UNION ALL

SELECT
    ContactName  AS PersonName,
    City,
    Country,
    'Supplier'   AS GroupType
FROM Suppliers;