---
slug: /
---

# Google Cloud Professional Data Engineer (PDE) — Exam Overview & Study Plan

<div class="pde-flow" role="img" aria-label="PDE scenario-solving flow: identify requirements, choose an architecture, then validate operations and trade-offs">
  <div class="pde-flow__node"><strong>Read the scenario</strong><small>Find the business goal and constraints</small></div>
  <span class="pde-flow__arrow" aria-hidden="true">&rarr;</span>
  <div class="pde-flow__node"><strong>Choose the pattern</strong><small>Match data shape, scale, and latency</small></div>
  <span class="pde-flow__arrow" aria-hidden="true">&rarr;</span>
  <div class="pde-flow__node"><strong>Check trade-offs</strong><small>Reliability, security, cost, and operations</small></div>
</div>

## 1. Exam Basics
- **Length**: 2 hours
- **Format**: 50–60 multiple choice / multiple select questions
- **Delivery**: Online proctored or onsite at test center
- **Cost**: $200 USD
- **Validity**: 2 years (recertification required)
- **Passing score**: Not publicly disclosed (pass/fail only, scaled scoring)
- **Prerequisite**: None official, but Google recommends 3+ years industry experience, 1+ year on GCP

## 2. Exam Domains (weight is approximate, based on official guide)
| Domain | Focus |
|---|---|
| 1. Designing data processing systems | Architecture selection, system design for reliability/scalability/flexibility |
| 2. Ingesting and processing the data | Pipelines, batch vs streaming, transformation |
| 3. Storing the data | Choosing storage systems, schema design, data modeling |
| 4. Preparing and using data for analysis | BI tools, feature engineering, ML prep |
| 5. Maintaining and automating data workloads | Orchestration, CI/CD, monitoring, cost optimization |
| 6. Analyzing data and enabling machine learning | AutoML, Vertex AI, BigQuery ML |
| 7. Ensuring solution quality | Security, reliability, compliance, testing |

**Study emphasis (qualitative; confirm exact percentages in the current official exam guide):**

| Emphasis | Domains | Why |
|---|---|---|
| High | 1, 2, 3 | Service selection (Pub/Sub, Dataflow, Dataproc, BigQuery, Bigtable, Spanner) drives most scenario questions |
| Medium | 5, 7 | Orchestration, IAM, encryption, DLP, monitoring, cost |
| Lower but easy points | 4, 6 | BigQuery ML, Vertex AI, Looker and BI tools |

## 3. Core Mindset for Questions
- Questions are **scenario-based**: pick the service/pattern that is *most appropriate*, not just "works."
- Prefer **managed/serverless** services over self-managed (e.g., Dataflow over self-hosted Spark, BigQuery over self-managed Hadoop) unless requirements say otherwise (e.g., existing Hadoop/Spark skills → Dataproc).
- Always weigh: **cost, latency, scalability, operational overhead, team skill set, existing tooling (lift-and-shift vs re-architect)**.
- Watch for keywords:
  - "minimize operational overhead" → serverless (BigQuery, Dataflow, Pub/Sub, Firestore)
  - "existing Hadoop/Spark jobs" → Dataproc
  - "real-time / streaming / low latency" → Pub/Sub + Dataflow + Bigtable/BigQuery streaming inserts
  - "petabyte-scale analytics / SQL" → BigQuery
  - "low-latency NoSQL at massive scale (time-series, IoT)" → Bigtable
  - "mobile/web app flexible NoSQL" → Firestore
  - "strong consistency, relational, global" → Cloud Spanner
  - "cheap, infrequent access archival" → Cloud Storage (Coldline/Archive)
  - "orchestration of multi-step pipelines" → Cloud Composer (Airflow)

## 4. Study Plan (4–6 weeks suggested)
1. **Week 1–2**: Core storage & compute services (Cloud Storage, BigQuery, Bigtable, Spanner, Dataproc, Dataflow, Pub/Sub). Hands-on labs for each.
2. **Week 3**: Data modeling, pipeline design patterns, orchestration (Composer), streaming vs batch.
3. **Week 4**: ML services (Vertex AI, BigQuery ML, AutoML), data governance (Data Catalog, DLP), IAM/security.
4. **Week 5**: Practice exams, review weak areas, re-do hands-on qwiklabs.
5. **Week 6**: Final review of cheat sheets, case studies (official Google case studies: Flowlogistic, MJTelco, TerramEarth — these recur in real exam scenarios).

## 5. Official Case Studies (memorize key requirements!)
Google publishes 3 case studies that often appear as the basis for several exam questions:
- **Flowlogistic**: Logistics company moving from on-prem Hadoop/Kafka to GCP; needs real-time tracking, legacy SQL/NoSQL migration.
- **MJTelco**: Telecom startup; needs scalable analytics pipeline for network telemetry, cost-sensitive, future ML plans.
- **TerramEarth**: Manufacturer with IoT sensors on vehicles; intermittent connectivity, needs edge processing + central analytics + predictive maintenance ML.

Read the official PDF case studies before the exam — questions assume familiarity with these scenarios.

## 6. Recommended Resources
- Official Google Cloud exam guide (console.cloud.google.com/certification)
- Qwiklabs / Google Cloud Skills Boost "Data Engineer" learning path
- "Google Cloud Certified Professional Data Engineer" official practice exam (free, on Google's site)
- Hands-on: build at least one end-to-end pipeline (Pub/Sub → Dataflow → BigQuery, plus a Dataproc Spark job, plus a Vertex AI model).

## 7. Files in this folder
- [Ingesting and Processing Data](02_ingestion_and_processing.md) — pipelines, Pub/Sub, Dataflow, Dataproc, batch vs streaming
- [Storage Services](03_storage_services.md) — Cloud Storage, BigQuery, Bigtable, Spanner, Firestore, SQL/Memorystore
- [Analytics and Machine Learning](04_analytics_and_ml.md) — BigQuery ML, Vertex AI, AutoML, analysis/BI tools
- [Orchestration, Reliability, Security & Compliance](05_orchestration_reliability_security.md) — Composer, monitoring, IAM, DLP, compliance
- [Service Decision Cheat Sheet](06_service_cheat_sheet.md) — quick decision matrix for "which GCP service do I pick"
- [Practice Questions](07_practice_questions.md) — practice Q&A with explanations
