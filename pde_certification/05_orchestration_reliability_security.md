# Orchestration, Reliability, Security & Compliance

## 1. Orchestration
- **Cloud Composer (Airflow)**: multi-service DAGs, scheduling, retries, dependency management, SLA monitoring. Use for complex cross-service workflows (e.g., Dataproc job → BigQuery load → notify → trigger ML pipeline).
- **Workflows**: lightweight serverless orchestration for simpler HTTP/API-based service chaining (less overhead than Composer for simple cases).
- **Cloud Scheduler**: cron-like triggering of jobs/Pub/Sub messages/HTTP endpoints.

## 2. Monitoring & Logging
- **Cloud Monitoring**: metrics, dashboards, alerting policies (uptime checks, custom metrics via OpenTelemetry).
- **Cloud Logging**: centralized log storage/search; export logs to BigQuery/GCS/Pub/Sub via **log sinks** for long-term retention or further processing.
- **Error Reporting**: aggregates and surfaces application errors automatically.
- **Data Catalog / Dataplex**: metadata discovery, data lineage, data classification — governance across BigQuery, GCS, Pub/Sub.
- Key exam pattern: "need to retain audit logs for 7 years" → export logs to a sink (GCS Archive/Coldline) or BigQuery with appropriate retention policy.

## 3. IAM & Access Control
- Principle of **least privilege**: grant minimal roles needed, prefer predefined roles over Owner/Editor, use custom roles when predefined roles are too broad.
- **IAM hierarchy**: Organization → Folder → Project → Resource (policies inherit downward).
- **Service accounts**: used by applications/VMs/pipelines to authenticate; avoid embedding keys — prefer **Workload Identity Federation** or attached service accounts over downloaded JSON keys.
- **BigQuery-specific access control**:
  - Dataset-level IAM roles.
  - **Authorized views**: share query results without granting access to underlying tables.
  - **Row-level security**: restrict rows a user can see via row access policies.
  - **Column-level security (policy tags / Data Catalog taxonomies)**: restrict sensitive columns (PII) per user/group.
- **VPC Service Controls**: create a security perimeter around GCP resources (e.g., BigQuery, GCS) to prevent data exfiltration even if IAM is misconfigured.

## 4. Data Protection & Compliance
- **Cloud DLP (Sensitive Data Protection)**: discover, classify, and redact/mask/tokenize PII (e.g., credit card numbers, SSNs) in data at rest or in pipelines.
- **Encryption**:
  - At rest: encrypted by default (Google-managed keys); option for **Customer-Managed Encryption Keys (CMEK)** via Cloud KMS, or **Customer-Supplied Encryption Keys (CSEK)** for full control.
  - In transit: TLS by default between Google services.
- **Data residency / sovereignty**: choose specific regions for storage/processing to meet regulatory requirements (e.g., GDPR → EU regions only).
- **Compliance frameworks**: GCP is compliant with HIPAA, PCI-DSS, GDPR, SOC 2, etc. — know that using compliant services correctly (e.g., signing a BAA for HIPAA) is still the customer's responsibility (**shared responsibility model**).

## 5. Reliability & Disaster Recovery
- **RPO (Recovery Point Objective)**: max acceptable data loss (time between backups).
- **RTO (Recovery Time Objective)**: max acceptable downtime to restore service.
- Design for RPO/RTO requirements by choosing:
  - Multi-region storage/BigQuery datasets for low RPO.
  - Automated backups (Cloud SQL automated backups + point-in-time recovery; Spanner backups).
  - Cross-region replication (Bigtable replication, GCS dual/multi-region).
- **Idempotent pipelines**: design Dataflow/pipeline jobs so re-running them (after failure/retry) doesn't duplicate or corrupt data (e.g., use upserts, dedupe by message ID).
- **Dead-letter queues**: isolate bad/unprocessable records instead of failing the whole pipeline.
- **Backpressure handling**: Dataflow autoscaling + Pub/Sub buffering absorb traffic spikes without data loss.

## 6. Cost Optimization (recurring exam theme)
- BigQuery: partition + cluster tables, avoid `SELECT *`, use materialized views, set `maximum bytes billed` on queries, use flat-rate pricing for predictable heavy usage.
- Compute: use preemptible/spot VMs for fault-tolerant batch jobs (Dataproc), autoscaling to avoid over-provisioning.
- Storage: lifecycle policies to move cold data to Nearline/Coldline/Archive automatically.
- Use **committed use discounts** / **flat-rate slots** for steady-state predictable workloads; on-demand for spiky/unpredictable workloads.

## 7. Testing & Quality
- Validate schema and data quality early in the pipeline (schema validation via Pub/Sub schemas, Dataflow data validation transforms).
- Use **staging environments** / separate projects for dev-test-prod to avoid impacting production data.
- Version control pipeline code (Beam/Dataflow, Airflow DAGs) and use CI/CD (Cloud Build) to test and deploy changes safely.
