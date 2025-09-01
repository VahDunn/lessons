1.
SELECT s.*
FROM Squads s
WHERE s.leader_id IS NULL
   OR s.leader_id NOT IN (SELECT d.dwarf_id FROM Dwarves d);

2.
SELECT d.*
FROM Dwarves d
WHERE d.age > 150
  AND d.profession = 'Warrior';

3.
SELECT DISTINCT d.*
FROM Dwarves d
JOIN Items i ON i.owner_id = d.dwarf_id AND i.type = 'weapon';

4.
SELECT d.dwarf_id, d.name, t.status, COUNT(*) AS task_count
FROM Dwarves d
         JOIN Tasks   t ON t.assigned_to = d.dwarf_id
GROUP BY d.dwarf_id, d.name, t.status
ORDER BY d.name, t.status;

5.
SELECT t.*
FROM Tasks   t
         JOIN Dwarves d ON d.dwarf_id = t.assigned_to
         JOIN Squads  s ON s.squad_id = d.squad_id
WHERE s.name = 'Guardians';

6.
SELECT
    d.dwarf_id        AS dwarf_id,
    d.name            AS dwarf_name,
    r.relationship    AS relationship_type,
    dr.dwarf_id       AS relative_id,
    dr.name           AS relative_name
FROM Relationships r
         JOIN Dwarves d  ON d.dwarf_id  = r.dwarf_id
         JOIN Dwarves dr ON dr.dwarf_id = r.related_to
ORDER BY d.name, relationship_type, relative_name;