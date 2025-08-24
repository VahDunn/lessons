12.3.1
INSERT INTO Employees
    (LastName, FirstName, Title, TitleOfCourtesy,
     BirthDate, HireDate, Address, City, Region,
     PostalCode, Country, HomePhone, Extension, Notes, PhotoPath)
VALUES
    ('Ivanov', 'Ivan', 'Sales Representative', 'Mr.',
     '1990-05-12', GETDATE(), 'Lenina, 1', 'Moscow', NULL,
     '101000', 'Russia', '+7-000-000-00-00', '123', 'New hire', '');


12.3.2
INSERT INTO EmployeeTerritories (EmployeeID, TerritoryID)
VALUES (10, '01581');

12.3.3
INSERT INTO Orders
    (CustomerID, EmployeeID, OrderDate, RequiredDate,
     ShipVia, Freight, ShipName, ShipAddress, ShipCity,
     ShipRegion, ShipPostalCode, ShipCountry)
VALUES
    ('ALFKI', @NewEmployeeID, GETDATE(), DATEADD(day, 7, GETDATE()),
     1, 25.00, 'Alfreds Futterkiste', 'Obere Str. 57', 'Berlin',
     NULL, '12209', 'Germany');
// потенциальные проблемы -
// FK к Customers: если указать несуществующий CustomerID, ошибка внешнего ключа.

// FK к Employees: если EmployeeID не существует
// ошибка внешнего ключа.

// FK к Shippers должен существовать в Shippers(ShipperID)
// Иначе ошибка внешнего ключа.