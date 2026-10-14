# Quick Service Decision Cheat Sheet

Use this as a last-minute review sheet. When a question describes a need, match the keyword to the service.

## Compute / Processing
| Keyword in question | Service |
|---|---|
| "Unified batch + streaming pipeline, minimal ops" | Dataflow |
| "Existing Hadoop/Spark/Hive jobs, lift-and-shift" | Dataproc (ephemeral clusters) |
| "No-code / visual ETL, many connectors" | Cloud Data Fusion |
| "Orchestrate multi-step, multi-service workflow with dependencies" | Cloud Composer (Airflow) |
| "Simple serverless workflow chaining APIs" | Workflows |
| "Schedule recurring jobs (cron)" | Cloud Scheduler |

## Messaging / Ingestion
| Keyword | Service |
|---|---|
| "Decouple producers/consumers, async, global" | Pub/Sub |
| "Cost-sensitive, high-throughput, manage own partitions" | Pub/Sub Lite |
| "Capture database changes (CDC) in near real time" | Datastream |
| "Large one-time/scheduled transfer from S3/Azure/on-prem" | Storage Transfer Service |
| "Petabyte offline migration, no good network link" | Transfer Appliance |

## Storage
| Keyword | Service |
|---|---|
| "Unstructured files/objects, data lake" | Cloud Storage |
| "Petabyte SQL analytics, serverless warehouse" | BigQuery |
| "Low-latency NoSQL, time-series/IoT, huge throughput" | Bigtable |
| "Flexible schema, mobile/web, real-time sync" | Firestore |
| "Global relational + horizontal scale + strong consistency" | Cloud Spanner |
| "Traditional relational DB, lift-and-shift" | Cloud SQL |
| "In-memory cache/session store" | Memorystore |

## Analytics / ML
| Keyword | Service |
|---|---|
| "SQL-based ML directly on warehouse data" | BigQuery ML |
| "No ML expertise, tabular/image/text AutoML" | Vertex AI AutoML |
| "Full custom model code, GPUs/TPUs" | Vertex AI Custom Training |
| "Common task: sentiment, vision, translation — don't reinvent" | Pre-trained APIs (Vision/NL/Translation/Speech) |
| "Consistent features training vs serving" | Vertex AI Feature Store |
| "Detect model degrading in production" | Vertex AI Model Monitoring |
| "Lightweight dashboard, free" | Looker Studio |
| "Enterprise governed BI, semantic layer" | Looker |

## Security / Governance
| Keyword | Service |
|---|---|
| "Find/redact/mask PII" | Cloud DLP (Sensitive Data Protection) |
| "Prevent data exfiltration even with misconfigured IAM" | VPC Service Controls |
| "Customer-managed encryption keys" | Cloud KMS (CMEK) |
| "Metadata discovery, lineage, data classification" | Data Catalog / Dataplex |
| "Restrict specific rows/columns in BigQuery" | Row-level security / Policy tags |

## Common Trade-off Questions
- **"Minimize cost, data accessed rarely"** → Coldline/Archive storage class + lifecycle rules.
- **"Minimize latency for global users, relational needed"** → Cloud Spanner (not Cloud SQL).
- **"We already have Spark expertise, want to migrate fast"** → Dataproc, not rewrite in Beam/Dataflow.
- **"Need exactly-once, ordered processing from IoT devices"** → Pub/Sub with ordering keys + Dataflow.
- **"Query data without moving/copying it, data in GCS"** → BigQuery external/federated tables (or BigLake).
- **"Table scanned by date filters constantly, costs too high"** → Add/verify partitioning (and clustering).
- **"On-prem Hadoop migrating with minimal code change"** → Dataproc + GCS connector (HDFS → GCS).

## Pricing Model Quick Reference
- BigQuery: on-demand (per TB scanned) vs flat-rate slots (reserved compute).
- Cloud Storage: pay for storage class + egress + operations; lifecycle rules reduce storage cost.
- Compute (Dataproc/GCE): preemptible/spot = cheap but can be reclaimed; committed use discounts for steady workloads.
- Bigtable: pay per node-hour (provisioned capacity) + storage — scale nodes for throughput, not storage.
