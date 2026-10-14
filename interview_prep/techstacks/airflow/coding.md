# Airflow DAG Coding Questions — Round 2 Drills

## Interview Guide
These are "write/fix a DAG" exercises rather than algorithmic coding — graded on idempotency, correct use
of dependencies/sensors, and whether you reach for modern TaskFlow API patterns instead of 2017-era
boilerplate. Narrate *why* a task is structured a certain way (idempotency, retries, resource isolation),
not just the syntax.

---

### Q1. GCS sensor → BigQuery load → data quality check → Slack alert on failure
```python
from airflow import DAG
from airflow.providers.google.cloud.sensors.gcs import GCSObjectExistenceSensor
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryCheckOperator
from airflow.providers.slack.notifications.slack import send_slack_notification
from datetime import datetime, timedelta

default_args = {"retries": 3, "retry_delay": timedelta(minutes=5)}

with DAG(
    dag_id="daily_orders_load",
    schedule="0 6 * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    default_args=default_args,
    on_failure_callback=send_slack_notification(
        slack_conn_id="slack_alerts", text="daily_orders_load FAILED: {{ ti.task_id }}"
    ),
) as dag:

    wait_for_file = GCSObjectExistenceSensor(
        task_id="wait_for_file",
        bucket="raw-landing",
        object="orders/{{ ds }}/orders.csv",
        mode="reschedule",   # free the worker slot while waiting
        timeout=60 * 60,
    )

    load_to_bq = GCSToBigQueryOperator(
        task_id="load_to_bq",
        bucket="raw-landing",
        source_objects=["orders/{{ ds }}/orders.csv"],
        destination_project_dataset_table="proj.staging.orders_{{ ds_nodash }}",
        write_disposition="WRITE_TRUNCATE",  # idempotent: safe to re-run for the same ds
        schema_update_options=["ALLOW_FIELD_ADDITION"],
    )

    check_row_count = BigQueryCheckOperator(
        task_id="check_row_count",
        sql="SELECT COUNT(*) > 0 FROM `proj.staging.orders_{{ ds_nodash }}`",
        use_legacy_sql=False,
    )

    wait_for_file >> load_to_bq >> check_row_count
```
**Talk through:** `mode="reschedule"` instead of default poke mode so the sensor doesn't hog a worker slot
for up to an hour; `WRITE_TRUNCATE` to a date-suffixed/partitioned table makes the load idempotent on
retry/backfill; the failure callback fires DAG-wide, not per task.

---

### Q2. DAG factory to avoid copy-pasting near-identical DAGs
```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

TABLE_CONFIGS = [
    {"name": "orders", "schedule": "0 6 * * *"},
    {"name": "customers", "schedule": "0 7 * * *"},
    {"name": "products", "schedule": "0 7 * * *"},
]

def build_dag(table_name: str, schedule: str) -> DAG:
    with DAG(
        dag_id=f"load_{table_name}",
        schedule=schedule,
        start_date=datetime(2026, 1, 1),
        catchup=False,
        tags=["ingestion", table_name],
    ) as dag:
        PythonOperator(
            task_id="load",
            python_callable=load_table,
            op_kwargs={"table_name": table_name},
        )
    return dag

for cfg in TABLE_CONFIGS:
    globals()[f"load_{cfg['name']}"] = build_dag(cfg["name"], cfg["schedule"])
```
**Follow-up:** "What's the risk of a DAG factory?" → DAG parsing time grows with the number of generated
DAGs/config entries; if the config list grows into the hundreds, move it to a database-backed config and
page/lazy-load rather than parsing everything on every scheduler loop.

---

### Q3. TaskFlow API (`@task`) version of a simple ETL chain
```python
from airflow.decorators import dag, task
from datetime import datetime

@dag(schedule="@daily", start_date=datetime(2026, 1, 1), catchup=False)
def taskflow_etl():
    @task
    def extract() -> list[dict]:
        return [{"id": 1, "val": "a"}, {"id": 2, "val": "b"}]

    @task
    def transform(records: list[dict]) -> list[dict]:
        return [{**r, "val": r["val"].upper()} for r in records]

    @task
    def load(records: list[dict]) -> None:
        print(f"Loading {len(records)} records")

    load(transform(extract()))

taskflow_etl()
```
**Talk through:** TaskFlow passes data between tasks via XCom automatically based on return values/
arguments — cleaner than manual `xcom_push`/`xcom_pull`, but call out the XCom size limit (small metadata
only, never pass full datasets through it — pass a GCS path/table reference instead).

---

### Q4. Branching based on a condition
```python
from airflow.decorators import task

@task.branch
def choose_path(ds=None) -> str:
    is_month_end = is_last_day_of_month(ds)
    return "run_month_end_job" if is_month_end else "run_daily_job"
```
**Follow-up:** "What happens to the task that isn't chosen?" → it's marked `skipped`, and downstream tasks
need `trigger_rule="none_failed_min_one_success"` (or similar) if they should run regardless of which
branch executed.

---

### Q5. Fix the bug: this DAG duplicates data on retry
**Given (buggy):**
```python
@task
def load_partition(ds=None):
    df = read_source(ds)
    df.to_gbq("proj.dataset.table", if_exists="append")  # BUG
```
**The bug:** `if_exists="append"` means any retry (automatic retry, manual clear-and-rerun, or backfill)
inserts the same day's data again, duplicating rows — this task is not idempotent.
**The fix:**
```python
@task
def load_partition(ds=None):
    df = read_source(ds)
    client.query(f"DELETE FROM `proj.dataset.table` WHERE partition_date = '{ds}'").result()
    df.to_gbq("proj.dataset.table", if_exists="append")
```
Or better, load to a staging table and `MERGE` into the target keyed on business key + date — explain both
options and when you'd pick delete-then-insert (simple, whole-partition overwrite) vs. `MERGE` (need to
preserve unrelated existing rows / handle partial updates).

---

### Q6. Data-aware scheduling with Datasets
```python
from airflow.datasets import Dataset
from airflow.decorators import dag, task
from datetime import datetime

orders_dataset = Dataset("gs://curated-bucket/orders/")

@dag(schedule="@daily", start_date=datetime(2026, 1, 1), catchup=False)
def produce_orders():
    @task(outlets=[orders_dataset])
    def write_orders():
        ...
    write_orders()

@dag(schedule=[orders_dataset], start_date=datetime(2026, 1, 1), catchup=False)
def consume_orders():
    @task
    def build_report():
        ...
    build_report()
```
**Talk through:** `consume_orders` triggers automatically whenever `produce_orders` updates the dataset,
instead of being scheduled on a separate time-based guess of when the upstream usually finishes — removes
a whole class of "ran too early, upstream wasn't done yet" bugs.

---

### Q7. Dynamic task mapping to process N files in parallel
```python
from airflow.decorators import dag, task
from datetime import datetime

@dag(schedule="@daily", start_date=datetime(2026, 1, 1), catchup=False)
def process_files():
    @task
    def list_files(ds=None) -> list[str]:
        return list_gcs_files(prefix=f"raw/{ds}/")

    @task
    def process_one(file_path: str) -> None:
        transform_and_load(file_path)

    process_one.expand(file_path=list_files())

process_files()
```
**Talk through:** `expand()` creates one mapped task instance per file at runtime (not known until the DAG
runs) — each gets independent retry/logging, which is strictly better than a manual Python `for` loop
inside a single task that would fail/retry as one unit.

---

### Q8. Unit test a DAG (import + structure test)
```python
import pytest
from airflow.models import DagBag

@pytest.fixture(scope="session")
def dagbag():
    return DagBag(dag_folder="dags/", include_examples=False)

def test_no_import_errors(dagbag):
    assert len(dagbag.import_errors) == 0, dagbag.import_errors

def test_daily_orders_load_task_count(dagbag):
    dag = dagbag.get_dag("daily_orders_load")
    assert dag is not None
    assert len(dag.tasks) == 3

def test_all_dags_have_retries(dagbag):
    for dag_id, dag in dagbag.dags.items():
        for task in dag.tasks:
            assert task.retries >= 1, f"{dag_id}.{task.task_id} has no retries configured"
```
**Why it matters:** this is the kind of CI gate a senior engineer adds so a broken DAG or a missing-retries
policy mistake is caught in a PR, not in production at 2am.

---

### Q9. Cross-DAG dependency with `ExternalTaskSensor`
```python
from airflow.sensors.external_task import ExternalTaskSensor

wait_for_upstream = ExternalTaskSensor(
    task_id="wait_for_upstream_etl",
    external_dag_id="upstream_etl",
    external_task_id="final_task",
    execution_date_fn=lambda dt: dt,  # adjust if schedules differ
    mode="reschedule",
    timeout=3600,
)
```
**Follow-up:** "When would you use `TriggerDagRunOperator` instead?" → when the upstream DAG should
actively kick off the downstream one (push model) rather than the downstream DAG waiting/polling for it
(pull model) — push is preferable when upstream reliably knows the moment it's ready.

---

### Q10. KubernetesPodOperator for a dependency-heavy task
```python
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator

run_custom_job = KubernetesPodOperator(
    task_id="run_custom_job",
    name="custom-etl-job",
    namespace="data-pipelines",
    image="gcr.io/my-project/custom-etl:1.4.0",
    cmds=["python", "run_job.py"],
    arguments=["--date", "{{ ds }}"],
    get_logs=True,
    is_delete_operator_pod=True,
)
```
**Follow-up:** "Why not just a `PythonOperator`?" → the job needs dependencies that conflict with (or are
far heavier than) the Airflow worker image, or you want the exact same container image used in another
deployment context (e.g., the same image used for a Cloud Run job) for consistency.
