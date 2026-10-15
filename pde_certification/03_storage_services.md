# Storage Services — Choosing the Right One

<div class="pde-choice" role="group" aria-label="Storage service decision guide">
  <p class="pde-choice__question">Start with the access pattern and consistency requirement:</p>
  <div class="pde-choice__branches">
    <div class="pde-choice__branch"><strong>SQL analytics at scale</strong><br />BigQuery</div>
    <div class="pde-choice__branch"><strong>Low-latency wide-column reads/writes</strong><br />Bigtable</div>
    <div class="pde-choice__branch"><strong>Global relational transactions</strong><br />Cloud Spanner</div>
    <div class="pde-choice__branch"><strong>Files, backups, or a data lake</strong><br />Cloud Storage</div>
  </div>
</div>

## Quick Decision Table
| Requirement | Service |
|---|---|
| Object storage, any file type, unstructured | **Cloud Storage** |
| Petabyte-scale SQL analytics, serverless | **BigQuery** |
| Low-latency NoSQL, massive scale, time-series/IoT, wide-column | **Bigtable** |
| Flexible schema NoSQL for mobile/web apps, real-time sync | **Firestore** |
| Global, strongly consistent, relational + horizontal scale | **Cloud Spanner** |
| Traditional relational (MySQL/Postgres/SQL Server), lift-and-shift | **Cloud SQL** |
| In-memory cache / session store | **Memorystore (Redis/Memcached)** |
| Data warehouse analytics with ML built-in | **BigQuery (+ BigQuery ML)** |

## 1. Cloud Storage (GCS)
- Object storage; stores data as immutable objects in buckets.
- **Storage classes** (choose based on access frequency):
  - **Standard**: frequently accessed, hot data.
  - **Nearline**: accessed < once/month (30-day min storage duration).
  - **Coldline**: accessed < once/quarter (90-day min).
  - **Archive**: accessed < once/year (365-day min), cheapest, for compliance/backup.
- **Lifecycle management**: auto-transition objects between classes or delete after N days — reduces cost automatically.
- Location types: Regional, Dual-region, Multi-region (trade-off: availability/latency vs cost).
- Used as the **data lake** layer in most GCP architectures — staging area before BigQuery/Dataproc processing.

## 2. BigQuery
- Serverless, fully managed, petabyte-scale **columnar** data warehouse. Pay per query (bytes scanned) or flat-rate slots.
- **Partitioning**: split tables by date/timestamp/integer range — reduces bytes scanned, lowers query cost. ALWAYS partition large time-series tables.
- **Clustering**: sorts data within partitions by column(s) — further reduces scan for filtered/aggregated queries. Use after partitioning for additional pruning (e.g., cluster by `user_id` within date partitions).
- **Nested & repeated fields** (STRUCT/ARRAY): denormalize data to avoid joins — BigQuery is optimized for denormalized, wide tables.
- **Materialized views**: precomputed, auto-refreshed query results for common aggregations — speeds up repeated queries, lower cost.
- **BigQuery ML**: train ML models (linear/logistic regression, k-means, boosted trees, time-series ARIMA) using plain SQL — no need to export data.
- **Authorized views / row-level security / column-level security (policy tags)**: fine-grained access control without copying data.
- **Streaming inserts**: near-real-time data availability (small added cost) vs batch load jobs (free, but latency).
- **BI Engine**: in-memory analysis service for fast dashboard queries (Looker Studio/Looker integration).
- Pricing: **on-demand** (per TB scanned) vs **flat-rate/editions** (reserved slots) — flat-rate for predictable heavy workloads.

## 3. Bigtable
- Wide-column NoSQL, based on HBase API, backs Google Search/Maps/Gmail internally.
- Best for: **time-series data, IoT sensor data, financial market data, recommendation/personalization** — high throughput, low latency (single-digit ms), huge scale (TB–PB).
- **Row key design is critical** — determines performance:
  - Avoid monotonically increasing keys (e.g., raw timestamp) → causes **hotspotting** on a single node.
  - Use **field promotion / salting / reversed timestamp** to distribute writes evenly.
- Not good for: small datasets (<1TB), transactional/relational needs, ad-hoc SQL analytics (no joins, no SQL — though BigQuery can query Bigtable via external tables).
- Scaling: add nodes to increase throughput (linear scaling); replication across regions for availability/DR.

## 4. Firestore (formerly Datastore mode available too)
- Document-based NoSQL, serverless, real-time sync, offline support for mobile/web.
- Good for: user profiles, game state, content management, apps needing flexible schema + real-time listeners.
- Strong consistency for single-document reads; supports transactions across multiple documents.

## 5. Cloud Spanner
- Globally distributed, horizontally scalable **relational** database with strong (external) consistency — "NewSQL."
- Use when you need: SQL + ACID transactions + horizontal scale + global availability (e.g., global financial ledger, inventory system).
- More expensive than Cloud SQL; justified only when single-instance relational DB can't scale or needs multi-region strong consistency.
- **Interleaved tables**: physically co-locate parent/child rows for performance (like a nested schema).

## 6. Cloud SQL
- Fully managed MySQL, PostgreSQL, SQL Server.
- Use for: traditional OLTP apps, lift-and-shift migrations, moderate scale (vertical scaling + read replicas, not horizontally sharded like Spanner).
- High availability via regional configuration (synchronous replica in a second zone).

## 7. Memorystore
- Managed Redis/Memcached. Use for caching, session storage, leaderboard/real-time counters — sits in front of a DB to reduce load/latency.

## 8. Data Modeling Tips (exam favorites)
- **Denormalize for BigQuery** (nested/repeated fields, wide tables) — optimized for analytical scans, not joins.
- **Normalize appropriately for Spanner/Cloud SQL** (OLTP, transactional integrity).
- For Bigtable, **design row keys around query patterns** (what will you filter/scan by?), not around "normalized" entity modeling.
- Schema changes: BigQuery supports adding nullable columns without downtime; avoid frequent schema changes on Bigtable (column families should be stable).
