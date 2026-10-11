# DBMS Notes: Transactions and Concurrency Control

## Transaction
A transaction is a logical unit of work made of one or more operations that must succeed or fail as a whole.
Example: transferring money means debit account A and credit account B.

## ACID properties
- **Atomicity:** all operations happen or none do. Recovery uses rollback.
- **Consistency:** a transaction takes the database from one valid state to another.
- **Isolation:** concurrent transactions do not interfere with each other.
- **Durability:** once committed, changes survive crashes (logs, write-ahead logging).

## Transaction states
Active -> Partially committed -> Committed. From Active or Partially committed, a failure leads to Failed -> Aborted.

## Concurrency problems
- **Lost update:** two transactions overwrite each other's changes.
- **Dirty read:** reading data written by an uncommitted transaction.
- **Non-repeatable read:** reading the same row twice and getting different values.
- **Phantom read:** running the same query twice and getting a different set of rows.

## SQL isolation levels (standard definitions)
- **Read Uncommitted:** dirty reads, non-repeatable reads and phantoms are possible.
- **Read Committed:** prevents dirty reads only.
- **Repeatable Read:** prevents dirty and non-repeatable reads; phantoms are possible.
- **Serializable:** prevents all of these problems.
Actual behavior differs slightly between database products.

## Serializability
A schedule is serializable if its result equals some serial (one-after-another) execution.
**Conflict serializability** is tested with a precedence graph. If the graph has no cycle, the schedule is conflict serializable.

## Locking
- **Shared (S) lock:** for reading; many transactions can hold it.
- **Exclusive (X) lock:** for writing; only one transaction can hold it.
- **Two-phase locking (2PL):** a growing phase (acquire locks), then a shrinking phase (release locks). 2PL guarantees conflict serializability.
- **Strict 2PL:** holds exclusive locks until commit, which avoids cascading rollbacks.

## Deadlock
Two or more transactions wait for each other forever. Handling methods:
- **Prevention:** wait-die and wound-wait schemes using timestamps.
- **Detection:** find cycles in the wait-for graph, then abort a victim transaction.
- **Timeout:** abort a transaction that waits too long.
