    4.3.1
    SELECT CustomerID, CompanyName, ContactName
    FROM Customers
    WHERE ContactName LIKE '% C%';

    4.3.2
    SELECT OrderID, CustomerID, ShipCountry, Freight, OrderDate
    FROM Orders
    WHERE Freight BETWEEN 100 AND 200
      AND ShipCountry IN ('USA', 'France');

    4.3.3
    SELECT EmployeeID, TerritoryID
    FROM EmployeeTerritories
    WHERE CAST(TerritoryID AS int) BETWEEN 6897 AND 31000;