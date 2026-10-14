# GCP Fundamentals — Interview Guide & Q&A
> **Round mapping:** R2 (technical deep dive). This file covers general, service-agnostic GCP topics —
> for BigQuery specifically, see [../bigquery/guide.md](../bigquery/guide.md).

## Interview Guide
These are the "general GCP" questions that come up independent of any single service: choosing the right
storage/database service for a given workload, and IAM/security fundamentals that apply across every
service in this stack. Interviewers use these to check breadth before drilling into BigQuery/Dataflow/
etc. specifically.

---

## Q&A

**Q1: Compare BigQuery, Bigtable, Cloud Spanner, Cloud SQL, and Firestore — when would you pick each?**
A:
- **BigQuery**: petabyte-scale analytical (OLAP) SQL, batch/ad hoc analytics, BI. See
  [../bigquery/guide.md](../bigquery/guide.md) for the deep dive.
- **Bigtable**: massive-scale, low-latency NoSQL for time-series/IoT/high-throughput key-value with wide
  rows, not for ad hoc SQL analytics.
- **Cloud Spanner**: globally distributed, strongly consistent relational DB needing horizontal scale with
  ACID transactions (financial systems, global inventory).
- **Cloud SQL**: traditional relational OLTP (Postgres/MySQL/SQL Server) at moderate scale, app
  backends, lift-and-shift from on-prem RDBMS.
- **Firestore**: flexible-schema NoSQL for mobile/web app backends, document model, real-time sync.

**Q2: Describe IAM best practices for a GCP data platform.**
A: Principle of least privilege via predefined roles (e.g., `roles/bigquery.dataViewer`, `dataEditor`,
`jobUser`) scoped at dataset/resource level rather than project-wide; use service accounts (not user
creds) for pipelines with Workload Identity (from GKE — see [../gke/guide.md](../gke/guide.md)) or
attached service accounts (Cloud Run/Functions) instead of downloaded keys; use IAM Conditions for
time/attribute-bound access; group-based IAM bindings (Google Groups) instead of per-user bindings for
maintainability; and authorized views/datasets to expose curated data without granting underlying table
access.
