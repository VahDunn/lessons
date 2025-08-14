6.3.1

SELECT ContactType, COUNT(*) AS ContactCount
FROM Contacts
GROUP BY ContactType;

6.3.2
SELECT CategoryID, AVG(UnitPrice) AS AvgPrice
FROM Products
GROUP BY CategoryID
ORDER BY AvgPrice ASC;