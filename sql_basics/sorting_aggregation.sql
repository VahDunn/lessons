
5.4.1
SELECT *
FROM Employees
ORDER BY BirthDate DESC, Country;

5.4.2
SELECT *
FROM Employees
WHERE Region IS NOT NULL
ORDER BY BirthDate DESC, Country;

5.4.3
SELECT
    AVG(UnitPrice) AS AvgPrice,
    MIN(UnitPrice) AS MinPrice,
    MAX(UnitPrice) AS MaxPrice
FROM [Order Details];

5.4.4
SELECT COUNT(DISTINCT City) AS UniqueCities
FROM Customers;