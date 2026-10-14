# Glossary

| Term | Meaning |
|---|---|
| Idempotent | Re-running an operation yields the same result; key for safe retries |
| Watermark | Streaming marker for how far event time has progressed; drives late-data handling |
| Windowing | Grouping unbounded stream data by time (fixed, sliding, session) |
| Exactly-once | Each record affects results once, despite retries |
| Partitioning | Splitting a table by a column (often date) to prune scans |
| Clustering | Sorting data within partitions to speed filtered queries |
| Backfill | Reprocessing historical data after a fix or schema change |
| SCD | Slowly changing dimension; how dimension history is tracked |
| DAG | Directed acyclic graph of tasks, as in Airflow |
| Dead-letter queue | Destination for messages that repeatedly fail processing |
| Data lineage | Record of where data came from and how it was transformed |
