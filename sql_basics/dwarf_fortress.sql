1.

SELECT d.*, s.*
FROM Dwarves d
         JOIN Squads  s ON s.squad_id = d.squad_id;

2

SELECT d.*
FROM Dwarves d
WHERE d.profession = 'miner'
  AND d.squad_id IS NULL;

3.

SELECT t.*
FROM Tasks t
WHERE t.status = 'pending'
  AND t.priority = (
    SELECT MAX(priority) FROM Tasks WHERE status = 'pending'
);

4.

SELECT d.dwarf_id, d.name, COUNT(i.item_id) AS item_count
FROM Dwarves d
         JOIN Items   i ON i.owner_id = d.dwarf_id
GROUP BY d.dwarf_id, d.name;

5.

SELECT s.squad_id, s.name, COUNT(d.dwarf_id) AS dwarf_count
FROM Squads s
         LEFT JOIN Dwarves d ON d.squad_id = s.squad_id
GROUP BY s.squad_id, s.name
ORDER BY s.name;

6. SELECT d.profession, COUNT(*) AS open_tasks
   FROM Tasks t
            JOIN Dwarves d ON d.dwarf_id = t.assigned_to
   WHERE t.status IN ('pending', 'in_progress')
   GROUP BY d.profession
   ORDER BY open_tasks DESC;


7.
WITH owners AS (
  SELECT DISTINCT i.type, d.dwarf_id, d.age
  FROM Items i
  JOIN Dwarves d ON d.dwarf_id = i.owner_id
  WHERE i.owner_id IS NOT NULL
)
SELECT type, AVG(age) AS avg_age
FROM owners
GROUP BY type
ORDER BY type;

8.

SELECT d.*
FROM Dwarves d
WHERE d.age > (SELECT AVG(age) FROM Dwarves)
  AND NOT EXISTS (
    SELECT 1
    FROM Items i
    WHERE i.owner_id = d.dwarf_id
);

