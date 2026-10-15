# PDE Mock Question Bank — Index

A bank of 550 scenario-style mock questions for the Google Cloud Professional Data Engineer exam, organized by domain. Every question includes the correct answer plus a **specific explanation of why each wrong option is wrong** — not just why the right one is right.

## How to use
- Work through one file per study session; don't just read answers, attempt each question first.
- Pay attention to the "why others are wrong" lines — the exam is designed so 2–3 options are *plausible*, and the differentiator is almost always a stated constraint (cost, latency, existing skills, compliance, operational overhead).
- Revisit missed questions after finishing a file; patterns repeat across the real exam.

## Files & Coverage
| File | Topic | Question range | Count |
|---|---|---|---|
| [Ingesting and Processing (Q1–Q100)](09_mock_ingestion_processing.md) | Pub/Sub, Dataflow, Dataproc, Data Fusion, Composer, transfer services | Q1–Q100 | 100 |
| [Storage (Q101–Q200)](10_mock_storage.md) | Cloud Storage, Bigtable, Spanner, Firestore, Cloud SQL, Memorystore | Q101–Q200 | 100 |
| [BigQuery Deep Dive (Q201–Q275)](11_mock_bigquery_deep_dive.md) | Partitioning, clustering, views, cost, schema design, pricing | Q201–Q275 | 75 |
| [Analytics and ML (Q276–Q350)](12_mock_analytics_ml.md) | BigQuery ML, Vertex AI, AutoML, pre-trained APIs, BI tools | Q276–Q350 | 75 |
| [Security and Compliance (Q351–Q425)](13_mock_security_compliance.md) | IAM, service accounts, DLP, VPC-SC, encryption, compliance | Q351–Q425 | 75 |
| [Reliability, Operations, and Cost (Q426–Q500)](14_mock_reliability_ops_cost.md) | Monitoring, RPO/RTO, idempotency, cost optimization, CI/CD, orchestration | Q426–Q500 | 75 |
| [Case Study Scenarios (Q501–Q550)](15_mock_case_studies_scenarios.md) | Flowlogistic / MJTelco / TerramEarth-style end-to-end scenarios | Q501–Q550 | 50 |

**Total: 550 questions**

## Answer format used throughout
```
**Qn.** <scenario>
A) ...
B) ...
C) ...
D) ...

**Correct answer: X**
**Why X is correct:** <reasoning tied to the stated constraints>
**Why the others are wrong:**
- A) <specific flaw>
- B) <specific flaw>
- C) <specific flaw>
```
