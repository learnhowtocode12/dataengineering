# Dataproc Coding / Operational Drills — Round 2

## Interview Guide
Dataproc "coding" questions are mostly about cluster/job operational commands and Airflow operator
config, since the transformation logic itself is just PySpark (see
[../pyspark/coding.md](../pyspark/coding.md)). Expect `gcloud` CLI snippets and Airflow operator config.

---

### Q1. Create an ephemeral cluster with autoscaling and preemptible secondary workers
```bash
gcloud dataproc clusters create nightly-etl-cluster \
  --region=us-central1 \
  --master-machine-type=n2-standard-4 \
  --worker-machine-type=n2-standard-4 \
  --num-workers=2 \
  --num-secondary-workers=4 \
  --secondary-worker-type=spot \
  --autoscaling-policy=nightly-etl-policy \
  --initialization-actions=gs://my-bucket/init-actions/install-libs.sh
```
**Talk through:** primary workers stay on standard VMs (stability for HDFS/shuffle-critical roles),
secondary workers use Spot for cost — matches the preemptible-risk discussion in
[guide.md](guide.md) Q3.

---

### Q2. Submit a PySpark job to an existing cluster
```bash
gcloud dataproc jobs submit pyspark gs://my-bucket/jobs/transform.py \
  --cluster=nightly-etl-cluster \
  --region=us-central1 \
  --py-files=gs://my-bucket/jobs/deps.zip \
  -- --run-date=2026-10-14 --source-table=proj.raw.orders
```

---

### Q3. Airflow operators: create cluster -> submit job -> delete cluster (always, even on failure)
```python
from airflow.providers.google.cloud.operators.dataproc import (
    DataprocCreateClusterOperator, DataprocSubmitJobOperator, DataprocDeleteClusterOperator,
)

CLUSTER_CONFIG = {
    "master_config": {"num_instances": 1, "machine_type_uri": "n2-standard-4"},
    "worker_config": {"num_instances": 2, "machine_type_uri": "n2-standard-4"},
    "secondary_worker_config": {
        "num_instances": 4,
        "machine_type_uri": "n2-standard-4",
        "is_preemptible": True,
    },
}

create_cluster = DataprocCreateClusterOperator(
    task_id="create_cluster", cluster_name="etl-{{ ds_nodash }}",
    cluster_config=CLUSTER_CONFIG, region="us-central1",
)
submit_job = DataprocSubmitJobOperator(
    task_id="submit_job", region="us-central1",
    job={
        "placement": {"cluster_name": "etl-{{ ds_nodash }}"},
        "pyspark_job": {"main_python_file_uri": "gs://my-bucket/jobs/transform.py"},
    },
)
delete_cluster = DataprocDeleteClusterOperator(
    task_id="delete_cluster", cluster_name="etl-{{ ds_nodash }}", region="us-central1",
    trigger_rule="all_done",   # delete even if the job failed - never leak a cluster
)
create_cluster >> submit_job >> delete_cluster
```
**Talk through:** `trigger_rule="all_done"` is the detail interviewers listen for — forgetting it means a
failed job leaves an idle (billed) cluster running indefinitely.

---

### Q4. Define an autoscaling policy (YAML)
```yaml
workerConfig:
  minInstances: 2
  maxInstances: 10
secondaryWorkerConfig:
  minInstances: 0
  maxInstances: 20
basicAlgorithm:
  cooldownPeriod: 4m
  yarnConfig:
    scaleUpFactor: 0.8
    scaleDownFactor: 1.0
    gracefulDecommissionTimeout: 1h
```
**Follow-up:** "Why `gracefulDecommissionTimeout`?" → gives running tasks time to finish on a worker before
it's removed during scale-down, avoiding wasted recompute of in-flight shuffle data.
