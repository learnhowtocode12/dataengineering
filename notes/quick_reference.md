# Quick Reference

## Pick the service
| Requirement | Service |
|---|---|
| Decouple producers and consumers, global, serverless | Pub/Sub |
| Serverless batch and streaming pipelines (Beam) | Dataflow |
| Existing Hadoop or Spark jobs | Dataproc |
| Petabyte-scale SQL analytics | BigQuery |
| Low-latency wide-column NoSQL, time series, IoT | Bigtable |
| Global relational with strong consistency | Spanner |
| Document store for mobile and web apps | Firestore |
| Cheap archival object storage | Cloud Storage (Coldline, Archive) |
| Multi-step pipeline orchestration | Cloud Composer (Airflow) |

## Data structure complexity (average case)
| Structure | Access | Search | Insert | Delete |
|---|---|---|---|---|
| Array / list | O(1) | O(n) | O(n) | O(n) |
| Hash table | n/a | O(1) | O(1) | O(1) |
| Linked list | O(n) | O(n) | O(1) at known node | O(1) at known node |
| BST (balanced / AVL) | O(log n) | O(log n) | O(log n) | O(log n) |
| Heap | O(1) peek | O(n) | O(log n) | O(log n) |
