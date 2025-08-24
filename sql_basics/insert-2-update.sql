13.3.1
UPDATE od
SET Discount = 0.20
    FROM [Order Details] AS od
WHERE od.Quantity > 50
  AND od.Discount < 0.20;

13.3.2

UPDATE Contacts
SET City = 'Piter',
    Country = 'Russia'
WHERE LTRIM(RTRIM(City)) = 'Berlin'
  AND LTRIM(RTRIM(Country)) = 'Germany';

13.3.3

INSERT INTO Shippers (CompanyName, Phone) VALUES
('ABCD: Test A', '(000) 000-0001'),
('ABCD: Test B', '(000) 000-0002');

а после этого
DELETE FROM Shippers
WHERE CompanyName LIKE 'TMP:%';