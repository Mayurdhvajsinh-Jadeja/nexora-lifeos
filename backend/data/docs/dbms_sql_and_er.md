# DBMS Notes: SQL and ER Modeling

## SQL command groups
- **DDL (definition):** CREATE, ALTER, DROP, TRUNCATE
- **DML (manipulation):** SELECT, INSERT, UPDATE, DELETE
- **DCL (control):** GRANT, REVOKE
- **TCL (transaction control):** COMMIT, ROLLBACK, SAVEPOINT

## Query structure and order of evaluation
Written order: SELECT, FROM, WHERE, GROUP BY, HAVING, ORDER BY.
Logical evaluation order: FROM, WHERE, GROUP BY, HAVING, SELECT, ORDER BY.
- WHERE filters rows before grouping.
- HAVING filters groups after aggregation (COUNT, SUM, AVG, MIN, MAX).

## Joins
- **INNER JOIN:** only rows that match in both tables.
- **LEFT JOIN:** all rows from the left table, with NULL where there is no match on the right.
- **RIGHT JOIN:** all rows from the right table, with NULL where there is no match on the left.
- **FULL OUTER JOIN:** all rows from both tables.
- **CROSS JOIN:** every combination of rows.

Example:
SELECT s.Name, c.CourseName
FROM Student s
INNER JOIN Enrollment e ON s.StudentID = e.StudentID
INNER JOIN Course c ON e.CourseID = c.CourseID;

## Keys and constraints
- **Primary key:** unique and not NULL; identifies each row.
- **Foreign key:** refers to a primary key in another table; enforces referential integrity.
- **Unique, NOT NULL, CHECK, DEFAULT:** other common constraints.

## ER modeling
- **Entity:** a thing with an independent existence (Student). A **weak entity** depends on another entity and has only a partial key (Dependent of Employee).
- **Attribute types:** simple, composite, multivalued, derived.
- **Relationship cardinality:** one-to-one, one-to-many, many-to-many.
- Many-to-many relationships become a separate table in the relational model, whose key combines both foreign keys.

## Indexing basics
An index speeds up reads on the indexed column but slows down inserts and updates. B-tree indexes suit range queries and equality; hash indexes suit equality only.
