# Looker & LookML — Interview Guide & Q&A
> **Round mapping:** R2 (technical deep dive) — usually lighter-weight than BigQuery/Spark questions.

## Interview Guide
For a data engineer (not a dedicated analytics engineer), Looker questions focus on: how you model data
for LookML (views/explores), performance (PDTs, aggregate awareness, caching), governance (access
filters, row-level security), and how your pipeline/warehouse design decisions upstream affect Looker's
performance downstream. Depth expectations are lighter than for BigQuery/Spark but you should speak
fluently about LookML structure and real dashboard performance troubleshooting.

---

## Q&A

**Q1: Explain the core LookML concepts: view, explore, model.**

**Answer:** A **view** maps to a table/derived table and defines dimensions (columns, SQL expressions, filters) and
measures (aggregations: count, sum, average). An **explore** defines a queryable starting point — a base
view plus joins to other views (with join type, relationship, SQL ON clause) that users build queries
against in the Looker UI. A **model** is a collection of explores tied to a specific database connection,
plus model-level settings (access grants, datagroups for caching).

**Q2: Dimension vs Measure — give examples and explain how they affect generated SQL.**

**Answer:** A dimension is a row-level attribute (`order_status`, `DATE(created_at)`) — appears in `GROUP BY`/
`SELECT` and can be filtered directly. A measure is an aggregate (`SUM(revenue)`, `COUNT(DISTINCT
user_id)`) — appears in `SELECT` with the aggregate function and is affected by whatever dimensions are
also selected (since Looker generates a single SQL query with all selected dimensions in `GROUP BY` and
all measures aggregated at that grain). Picking the wrong dimension grain (e.g., including a very
high-cardinality dimension alongside a measure) can blow up result size and query cost.

**Q3: What is a derived table in LookML, and PDT (persistent derived table) specifically?**

**Answer:** A derived table lets you define a view backed by a custom SQL query (or LookML-generated SQL) instead
of a raw table — useful for pre-aggregating, reshaping, or combining data before it's exposed as a view.
A **PDT** materializes that derived table's results into a real table in the database (in a Looker-managed
scratch schema) on a trigger/schedule (`datagroup_trigger`, `sql_trigger_value`, or `persist_for`), so
repeated queries against it hit a small pre-built table instead of recomputing the derived SQL every time
— critical for performance on expensive aggregations or multi-table joins.

**Q4: How do you control PDT rebuild triggers, and why does trigger choice matter?**

**Answer:** `sql_trigger_value` runs a lightweight SQL check (e.g., `SELECT MAX(updated_at) FROM source_table`) on
an interval and rebuilds the PDT only if the value changed — ties freshness to actual upstream data
changes rather than a blind timer. `datagroup`-based triggers let multiple PDTs/caches share one
freshness signal (e.g., one datagroup tied to "ETL pipeline completed" that many derived tables and
query caches key off), which is more efficient than each PDT polling independently and keeps rebuilds
synchronized with your actual ETL completion (often triggered by the pipeline itself calling the Looker
API or updating a sentinel table/value at the end of a successful Airflow DAG run).

**Q5: How does Looker's caching work (query result cache vs PDT) and how do you tune it?**

**Answer:** Query result caching stores the result of a specific generated SQL query for a datagroup's cache TTL,
so repeated identical dashboard loads don't re-hit the warehouse. PDTs are separate — they materialize
intermediate tables so even cache-miss queries run against a small precomputed table rather than raw
joins/aggregations. Tune by aligning datagroup triggers with actual data refresh cadence (don't cache
longer than data changes, don't rebuild more often than data changes — wasted compute), and by identifying
expensive explores (via Looker's query performance/slow query logs or the System Activity explore) that
need a PDT.

**Q6: How do you implement row-level security (e.g., each sales rep sees only their region) in Looker?**

**Answer:** **Access filters** / **user attributes**: define a user attribute (e.g., `region`) populated per user
(via SSO/SAML attribute mapping, LDAP, or manually), then apply an `access_filter` on the relevant
explore/view tying a dimension (`region`) to `{{ _user_attributes['region'] }}`, so Looker injects a
`WHERE` filter automatically into every query that user runs against that explore — enforced at the SQL
generation layer, consistent regardless of which dashboard/look the user views.

**Q7: How do you manage LookML project structure and deployment (dev/prod, version control)?**

**Answer:** LookML projects are Git-backed — developers work in personal dev branches/dev mode, validate with the
LookML validator (and ideally CI checks: `lookml-validator`/content validator run in a CI pipeline on PR),
then merge to production branch which Looker deploys. Use `.view.lkml`/`.explore.lkml` file organization
per subject area, shared/common fields via `extends:`/refinements, and environment-specific connection
overrides if dev/staging/prod point at different warehouse datasets.

**Q8: How do upstream BigQuery schema/partitioning decisions affect Looker dashboard performance, and
what would you change as the data engineer if dashboards are slow?**

**Answer:** Looker generates SQL against the explore's underlying tables, so if the BigQuery tables aren't
partitioned/clustered appropriately for the filters Looker dashboards commonly apply (e.g., date range
filters), every dashboard load triggers a large scan. As the data engineer, I'd: ensure fact tables are
date-partitioned matching the default date filter dimension, add clustering on commonly-filtered/joined
dimensions, pre-aggregate heavy metrics into a dedicated BI-serving table (reducing join complexity
Looker needs to express), and coordinate with analytics engineers on which explores need a PDT versus
querying the base warehouse table directly.

**Q9: What's Looker's "aggregate awareness" (`aggregate_table`) feature and when do you use it?**

**Answer:** `aggregate_table` lets you define pre-aggregated summary tables (e.g., daily/monthly rollups) within a
view, and Looker automatically rewrites a query to use the smallest sufficient aggregate table instead of
the full-grain base table when the requested dimensions/measures can be satisfied by it — transparent to
the end user. Use it for very large fact tables where most dashboard queries only need a coarser grain
(e.g., monthly revenue by region) so you avoid scanning billions of row-level records for a chart that
only needs a few hundred summary rows.

**Q10: How would you expose a governed "single source of truth" metric (e.g., "revenue") across many
explores without duplicating logic?**

**Answer:** Define the measure once in a shared base view (or via LookML `extends`/a central "metrics" view) and
reference/join it into the relevant explores rather than redefining the SQL expression in multiple
places — any change to the business definition (e.g., how refunds are handled) is made in one place and
propagates everywhere, which is the core governance value proposition of a semantic layer like LookML
versus every analyst writing ad hoc SQL.

**Q11: As a data engineer (not analytics engineer), what's your typical involvement with Looker in a
project?**

**Answer:** Building/maintaining the curated BigQuery tables and views the LookML layer sits on top of (schema
design, partitioning/clustering for query performance, SCD handling for dimensions), ensuring pipeline
freshness/SLA so PDT triggers and dashboards reflect timely data, sometimes writing or reviewing LookML
for derived tables that are closer to "pipeline logic" than "business metric logic," setting up the
service account/IAM Looker uses to query BigQuery, and troubleshooting performance issues that trace back
to the warehouse layer rather than LookML itself.

**Q12: How do you debug a Looker dashboard returning incorrect numbers?**

**Answer:** Use "Explore from here"/"Get SQL" (or SQL Runner) to inspect the exact generated SQL, verify the join
paths/fan-out (a classic bug: joining a one-to-many relationship without a count-distinct-safe measure
causes a fan-out that inflates sums), check symmetric aggregates are being applied correctly by Looker
for multi-join explores, verify the underlying table's data directly in BigQuery for the same filter
conditions, and check PDT/cache staleness (is the dashboard reading a stale cached result or an
out-of-date PDT because a trigger didn't fire).
