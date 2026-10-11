# DBMS Notes: Normalization

## Why normalize
Normalization organizes tables to reduce redundancy and avoid three anomalies:
- **Insertion anomaly:** you cannot add some data without adding unrelated data.
- **Deletion anomaly:** deleting one fact accidentally removes another fact.
- **Update anomaly:** the same fact is stored in many rows, so a change must be made everywhere.

## Functional dependency (FD)
X -> Y means that if two rows have the same value of X, they must have the same value of Y.
Example: StudentID -> StudentName.

A **candidate key** is a minimal set of attributes that determines all other attributes. A **prime attribute** is part of some candidate key.

## Normal forms
- **1NF:** every column holds atomic (single) values and there are no repeating groups.
- **2NF:** the table is in 1NF and no non-prime attribute depends on only part of a composite candidate key (no partial dependency).
- **3NF:** the table is in 2NF and has no transitive dependency. For every FD X -> A, either X is a superkey or A is a prime attribute.
- **BCNF:** for every non-trivial FD X -> Y, X must be a superkey. BCNF is stricter than 3NF.
- **4NF:** the table is in BCNF and has no non-trivial multivalued dependency unless it is on a superkey.
- **5NF:** the table is in 4NF and every join dependency is implied by the candidate keys. 5NF is about lossless decomposition, not about partial or transitive dependencies.

## Worked example
Table Enrollment(StudentID, CourseID, StudentName, CourseName, Grade), key = (StudentID, CourseID).
- StudentID -> StudentName is a partial dependency, which violates 2NF.
- CourseID -> CourseName is also a partial dependency.

Decompose into:
- Student(StudentID, StudentName)
- Course(CourseID, CourseName)
- Enrollment(StudentID, CourseID, Grade)

## Good decomposition properties
- **Lossless join:** joining the pieces gives back exactly the original table.
- **Dependency preservation:** all original FDs can still be checked in the smaller tables.
