# Informatica PowerCenter — Interview Guide & Q&A
> **Round mapping:** R2 (technical deep dive) and often revisited as the centerpiece story in R4. Hands-on
> drills: [coding.md](coding.md). See also
> [../informatica_cloud/guide.md](../informatica_cloud/guide.md) (the iPaaS successor, and the full
> Informatica-to-GCP migration narrative).

## Interview Guide
PowerCenter questions check core legacy ETL fundamentals: mappings, sessions, workflows, transformations,
and performance tuning. This combination (legacy Informatica + modern GCP stack) signals you've likely
worked on a migration/modernization project — have a clear narrative ready (see
[../informatica_cloud/guide.md](../informatica_cloud/guide.md) Q5-Q10), since it's often the most
differentiating round for this specific profile.

---

## Q&A

**Q1: Explain the core PowerCenter architecture: Repository, Integration Service, Designer, Workflow
Manager/Monitor.**
A: The **Repository** (metadata DB) stores mappings, sessions, workflows, and transformation logic.
**Designer** is where developers build **mappings** (source → transformations → target data flow).
**Workflow Manager** schedules/sequences **sessions** (a session = a run-time instance of a mapping with
connection/config details) into **workflows** (DAG of sessions and other tasks: Decision, Email, Command,
Event-Wait). The **Integration Service** is the engine that actually executes workflows/sessions, reading
source data, applying transformation logic, and writing to targets. **Workflow Monitor** gives run-time
visibility (status, logs, row counts, errors).

**Q2: What are the most common PowerCenter transformations and when do you use each?**
A: **Source Qualifier** (default read transformation for relational sources, where you can push filters/
joins to the DB), **Expression** (row-level derived columns/calculations), **Filter** (row-level
conditional pass-through), **Router** (multi-way filter, like a switch/case, sending rows to different
outputs), **Aggregator** (GROUP BY-style aggregation, supports sorted-input optimization), **Joiner**
(join two heterogeneous sources that can't be joined at the DB level), **Lookup** (connected/unconnected,
cached/uncached — enrich rows with reference data, e.g., surrogate key lookups for SCD), **Update
Strategy** (mark rows as insert/update/delete/reject for SCD/target DML behavior), **Sequence Generator**
(surrogate key generation), **Normalizer** (denormalize/flatten repeating groups, e.g., COBOL/VSAM
sources), **Sorter**, **Rank**, **Stored Procedure/Transaction Control**.

**Q3: Connected vs unconnected Lookup — difference and when to use unconnected.**
A: A connected Lookup sits inline in the data flow pipeline, receiving input and passing output downstream
for every row. An unconnected Lookup is called like a function from an Expression transformation
(`:LKP.lookup_name(args)`), only when needed (e.g., conditionally, or to avoid lookup overhead for rows
that don't need it) — useful for conditional lookups, returning a single port, or reusing the same lookup
logic from multiple places in a mapping without wiring it into the main pipeline multiple times.

**Q4: How do you implement SCD Type 1 and Type 2 in PowerCenter?**
A: Type 1 (overwrite): Lookup on the natural/business key against the target, Expression to detect changed
attributes, Update Strategy to mark changed rows as `DD_UPDATE`. Type 2 (versioned history): Lookup to find
the current row, compare attributes, if changed: Update Strategy marks the old row's `end_date`/
`is_current` update (`DD_UPDATE`) and generates a new row via `DD_INSERT` with a new surrogate key (via
Sequence Generator), new `effective_start_date`, `is_current = Y`; typically implemented with two target
instances (or a Router splitting update vs insert rows) feeding the same physical table.

**Q5: What's the difference between a mapplet and a reusable transformation?**
A: A reusable transformation is a single transformation (e.g., one Expression or Lookup) that can be
reused across multiple mappings. A mapplet is a reusable *set* of transformations (a mini sub-pipeline
with its own input/output) that can be dropped into multiple mappings — used to standardize common
multi-step logic (e.g., a standard "cleanse address" sequence) across many mappings without duplicating
the logic.

**Q6: How do you tune a slow PowerCenter session?**
A: Push down as much as possible to the source DB (filters/joins via Source Qualifier override SQL or
pushdown optimization), use sorted input for Aggregator/Joiner where possible to use the more efficient
sorted-merge mode, tune cache sizes for Lookup/Aggregator/Joiner (undersized cache spills to disk,
oversized wastes memory), increase session-level DTM buffer size and partition the session (pipeline/
source/target partitioning) to parallelize across CPUs, minimize unconnected/uncached lookups on
high-volume paths, and review session logs for bottleneck stage (reader/transformation/writer busy %). See
[../informatica_cloud/guide.md](../informatica_cloud/guide.md) Q9 for how these principles carry over to
IICS plus cloud-specific levers.

**Q7: What is Pushdown Optimization (PDO)?**
A: PDO translates mapping logic into native SQL executed by the source or target database instead of row-
by-row processing in the Integration Service engine — full pushdown runs the entire mapping as a single
generated SQL statement when all transformations are pushdown-compatible, source-side or target-side
partial pushdown pushes only part of the logic. It dramatically improves performance for DB-heavy
transformations by leveraging the database engine's own optimizer instead of PowerCenter's row engine.

**Q8: How do you handle error handling / rejected rows in PowerCenter?**
A: Update Strategy `DD_REJECT` plus session-level error-row file settings capture rejected rows to a bad
file with reject reason codes; Transaction Control transformation manages commit/rollback boundaries;
session-level "on error" behavior (stop vs continue) and email/task failure notifications in Workflow
Manager handle run-level failure response; reusable error-handling mapplets standardize logging rejected
records to an error table for later triage/reprocessing.
