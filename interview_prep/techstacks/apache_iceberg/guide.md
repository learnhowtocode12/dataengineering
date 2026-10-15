# Apache Iceberg & Lakehouse Table Formats — Interview Guide & Q&A
> **Round mapping:** R2 (technical deep dive), increasingly common given the industry shift toward open
> lakehouse architectures. Hands-on drills:
> [coding](coding.md).

## Interview Guide
Apache Iceberg questions are showing up more and more in GCP data engineer loops because BigQuery/BigLake,
Dataproc, and the broader industry have converged on open table formats as the answer to "how do we get
warehouse-like reliability on top of plain files in GCS/S3." At 6+ years, you're expected to explain *why*
Iceberg exists (what was broken about plain Hive-style tables), how its metadata model delivers ACID/time
travel/schema evolution, and how it plugs into this specific stack (BigLake, Dataproc, BigQuery). You are
**not** expected to have memorized the full spec — reasoning about the metadata-tree model correctly is
what matters.

---

## Q&A

**Q1: What problem does Iceberg actually solve? Why not just use Parquet files in GCS directly?**

**Answer:** Plain "Hive-style" tables (a directory of Parquet files, partitioned by folder structure) have real
production problems at scale: listing thousands/millions of files in object storage to plan a query is
slow; there's no atomic multi-file commit, so a failed write can leave readers seeing a half-written,
inconsistent table; schema changes often require rewriting data or breaking old partitions; and the
partition scheme is physically baked into the directory layout, so changing it means rewriting the entire
historical dataset. Iceberg adds a **metadata layer** on top of the same underlying Parquet/ORC/Avro files
that solves all of this without changing how the data itself is stored.

**Q2: Describe Iceberg's metadata architecture (the "metadata tree").**

**Answer:** A **catalog** (Hive Metastore, BigLake Metastore, a REST catalog, etc.) holds one pointer: the current
**metadata file** for a table. That metadata file lists the table's schema (with stable column IDs, not
just names), partition spec, and a pointer to the current **snapshot**. A snapshot points to a **manifest
list**, which lists **manifest files**, each of which lists the actual **data files** (with stats like
min/max per column for pruning) that make up that snapshot. Every write produces a brand-new metadata file
and snapshot — readers always see one complete, consistent snapshot, never a partial write.

**Q3: How does Iceberg provide ACID guarantees and handle concurrent writers?**

**Answer:** Every commit is an atomic **compare-and-swap** on the catalog's pointer to the metadata file — a writer
builds the new metadata file for its proposed snapshot, then atomically swaps the catalog pointer from the
old metadata file to the new one only if it hasn't changed since the writer started (optimistic
concurrency). If another writer committed first, the swap fails and the losing writer retries by rebuilding
its change on top of the new current state. Readers always read via one consistent metadata-file pointer,
so they never observe a partially-committed state.

**Q4: How does schema evolution work without rewriting existing data files?**

**Answer:** Iceberg tracks columns by a **stable internal ID**, not by name or physical position. Adding a column
just adds a new ID to the schema going forward — old data files simply don't have a value for it (read as
null); renaming a column changes only the name mapped to that ID, so old data doesn't need touching;
widening a type (int → long) is metadata-only since it's a safe read-time promotion. This is the core
mechanical reason Iceberg schema changes are instant metadata operations instead of data-rewrite jobs.

**Q5: What is "partition evolution," and why is it a bigger deal than it sounds?**

**Answer:** In Hive-style tables, the partition columns are physically encoded in the directory path — changing
partitioning (e.g., from daily to hourly) means rewriting the entire table's directory structure. Iceberg
decouples partitioning into metadata (**hidden partitioning**): you can change the partition spec going
forward, and Iceberg tracks which spec applies to which data files internally, transparently querying
across files written under old *and* new partition schemes without the user needing to know or specify
which scheme applies to which date range. This is one of Iceberg's most-cited practical advantages over
raw Hive tables.

**Q6: Explain Iceberg's time travel and rollback.**

**Answer:** Because every write creates a new, retained snapshot (until expired), you can query the table **as of**
a past snapshot ID or timestamp (`FOR SYSTEM_TIME AS OF` / `VERSION AS OF` depending on engine syntax) to
see exactly what the table looked like at that point — useful for debugging a bad pipeline run or
reproducing a report. **Rollback** goes further: it atomically moves the catalog's current-snapshot pointer
back to an earlier snapshot, effectively undoing one or more bad commits (e.g., a corrupted nightly load)
without restoring from a separate backup.

**Q7: How are row-level updates/deletes handled, and what's merge-on-read vs. copy-on-write?**

**Answer:** Rewriting an entire multi-GB data file to delete or update a handful of rows is wasteful, so Iceberg
supports **merge-on-read**: a small **delete file** records which rows (by position or by key) are
logically deleted, and readers merge the delete file against the data file at read time to get the correct
result; a background **compaction** job later rewrites affected data files for real and removes the delete
files. **Copy-on-write** instead rewrites the whole affected data file immediately on every update/delete —
simpler for readers (no merge step, faster reads) but more expensive on the write path. The trade-off is
classic: merge-on-read favors fast/cheap writes at the cost of read-time merge overhead and needing
periodic compaction; copy-on-write favors fast reads at the cost of heavier writes.

**Q8: Why would compaction/maintenance still matter if Iceberg "solves" the small-files problem?**

**Answer:** Iceberg's metadata makes small files *queryable efficiently* (via manifest-level stats and pruning), but
it doesn't eliminate the cost of physically opening many small files during a scan, nor the accumulation of
delete files under merge-on-read. Periodic **compaction** (rewriting many small data files into fewer
larger ones) and **snapshot expiration** (removing old, no-longer-needed snapshots and their orphaned data
files to reclaim storage and keep metadata lookups fast) are still necessary maintenance operations —
usually run as a scheduled Spark/Dataproc job, same operational mindset as vacuuming/maintenance jobs in
any warehouse.

**Q9: How does Iceberg compare to Delta Lake and Apache Hudi, at a level appropriate for an interview?**

**Answer:** All three solve the same core problem (ACID + schema/partition evolution + time travel on top of object
storage) with different trade-offs: **Delta Lake** originated in and is most deeply integrated with
Spark/Databricks, with a transaction log (`_delta_log`) conceptually similar to Iceberg's metadata tree.
**Hudi** leans further into incremental/streaming upserts with built-in indexing for fast point lookups,
popular in CDC-heavy pipelines. **Iceberg** has put the most effort into true multi-engine neutrality (a
vendor-neutral spec with first-class support across Spark, Trino, Flink, and now BigQuery/BigLake), which
is a big reason it's become the common choice for teams that don't want to commit to one engine forever.
Avoid declaring a single "winner" in an interview — frame it as workload/ecosystem fit.

**Q10: How does Iceberg integrate with this specific GCP stack (BigQuery/BigLake, Dataproc)?**

**Answer:** **BigLake tables for Apache Iceberg** let BigQuery read *and write* Iceberg tables stored in GCS with
full BigQuery feature support (via the **BigLake Metastore** acting as the Iceberg catalog), so you get
BigQuery's query engine and governance (IAM, row/column security) directly on open-format data without
copying it into BigQuery-native storage. On **Dataproc**, Spark jobs use the Iceberg Spark connector/
catalog configuration to read and write the exact same tables — meaning a PySpark transformation job and a
BigQuery analyst query can operate on the identical underlying files and catalog, which is the actual
point of a lakehouse: one copy of data, multiple engines.

**Q11: When would you choose Iceberg-on-GCS over just loading everything into native BigQuery storage?**

**Answer:** When you need **multi-engine access** to the same data (Spark/Dataproc jobs and BigQuery both need to
read/write it without duplicating it or building sync pipelines between two copies), when data needs to
remain portable/not locked into one warehouse's proprietary storage format (multi-cloud or "avoid vendor
lock-in" requirements), or in a mixed-maturity migration where some workloads are staying on
Spark/Dataproc longer while others move to BigQuery — Iceberg lets both read the same tables during the
transition instead of forcing an all-or-nothing cutover. For a BigQuery-only shop with no multi-engine
need, native BigQuery storage is usually simpler and higher-performing with less operational overhead.

**Q12: How would this tie into an Informatica/legacy modernization story?** *(cross-reference)*

**Answer:** A common pattern: legacy on-prem Hive tables get lifted into GCS as Iceberg tables during a Hadoop
migration (preserving ACID/schema-evolution behavior the team already relied on in Hive, rather than
losing it by flattening to plain Parquet), letting Dataproc/Spark jobs keep running largely unchanged
against GCS instead of HDFS, while BigQuery is incrementally given direct access to the same Iceberg tables
via BigLake for reporting — avoiding a risky single big-bang cutover to BigQuery-native storage. Mentioning
this unprompted connects this topic directly back to the Informatica → GCP migration narrative in
[../informatica_cloud/guide](../informatica_cloud/guide.md).
