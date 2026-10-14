# Dataproc — Interview Guide & Q&A
> **Round mapping:** R2 (technical deep dive). Hands-on drills: [coding.md](coding.md) (Dataproc
> cluster/job operational commands — for the actual PySpark transformation code that runs on Dataproc,
> see [../pyspark/coding.md](../pyspark/coding.md)). See also
> [../dataflow/guide.md](../dataflow/guide.md) (the alternative compute engine) and
> [../apache_iceberg/guide.md](../apache_iceberg/guide.md) (table format for Dataproc/Spark lake storage).

## Interview Guide
Dataproc is the other half of GCP's "which compute engine for this job" decision point. Expect questions
on cluster management (ephemeral vs long-running), PySpark job submission, autoscaling policies, cost
optimization (preemptible/spot VMs), and migration patterns from on-prem Hadoop/Spark.

---

## Q&A

**Q1: Dataflow vs Dataproc — how do you decide which to use?**
A: Dataproc is managed Hadoop/Spark/Hive/Flink clusters — best when: you have existing Spark/Hadoop jobs
to lift-and-shift, need Spark-specific libraries (MLlib, GraphX) or Spark SQL/Hive compatibility, want
more granular cluster/tuning control, or run mixed workloads (Spark + Hive + Presto) on shared
infrastructure. Cost-wise, ephemeral Dataproc clusters with preemptible/spot workers can be cheaper for
scheduled batch jobs than Dataflow's per-job autoscaling. See [../dataflow/guide.md](../dataflow/guide.md)
Q1 for the mirror-image framing of this same decision.

**Q2: Explain Dataproc cluster types: ephemeral vs long-running, and autoscaling policies.**
A: **Ephemeral clusters** are created per-job (or per-workflow) and torn down after completion — preferred
for scheduled batch ETL since you only pay for the job duration and avoid idle cluster cost/drift; typically
orchestrated via Airflow/Composer (`DataprocCreateClusterOperator` → submit job → `DataprocDeleteCluster`).
**Long-running clusters** stay up for interactive/ad hoc workloads (notebooks, Hive/Presto serving) —
costlier if underutilized, so autoscaling policies (min/max worker nodes, scale-up/down thresholds based
on YARN pending memory) and idle-cluster-deletion timeouts are used to control cost.

**Q3: How do you use preemptible/Spot VMs with Dataproc, and what's the risk?**
A: Secondary workers can be preemptible/Spot VMs, which are significantly cheaper but can be reclaimed by
Google at any time (preemptible: 24h max, can be revoked earlier; Spot: no max duration but also
revocable). Spark handles worker loss by recomputing lost partitions (lineage) and re-launching tasks, so
it tolerates preemption for data processing — but you should keep primary/non-preemptible workers (and
HDFS/datanode roles) on standard VMs, size the preemptible fraction conservatively (e.g., 50% of workers)
for cost without excessive job retries/stalls, and avoid preemptible for jobs sensitive to tail latency/
strict SLAs.

**Q4: How do you submit and parameterize PySpark jobs on Dataproc from Airflow?**
A: Use `DataprocSubmitJobOperator` (or `DataprocSubmitPySparkJobOperator` legacy) specifying the cluster
name/region, main Python file (often staged on GCS), `--py-files` for dependency zips/wheels, and job
arguments. Common pattern: ephemeral cluster created via `DataprocCreateClusterOperator` with a cluster
config templated (machine types, autoscaling policy, initialization actions for extra libraries), job
submitted, then `DataprocDeleteClusterOperator` in a `trigger_rule=ALL_DONE` to ensure cleanup even on
job failure. See [../airflow/guide.md](../airflow/guide.md) for the Airflow-side DAG design.

**Q5: What are Dataproc initialization actions and when do you need them?**
A: Shell scripts run on every node at cluster creation to install extra packages/libraries not in the base
image (e.g., custom Python packages, JDBC drivers, monitoring agents, internal CA certs). Stored in GCS and
referenced in cluster creation config. Alternative/complement: custom Dataproc images (pre-baked) for
faster cluster startup when init actions are heavy/slow, trading image maintenance overhead for startup
speed.

**Q6: How do you migrate an on-prem Hadoop/Spark workload to GCP — Dataproc lift-and-shift vs
re-architecture to BigQuery/Dataflow?**
A: Lift-and-shift to Dataproc first (fastest path, minimal code change — point Spark jobs at GCS instead
of HDFS via the GCS connector, migrate Hive metastore to Dataproc Metastore or an external Hive metastore,
migrate Oozie/Airflow DAGs to Cloud Composer) to de-risk the migration and stop paying for on-prem
hardware quickly. Then selectively re-architect: SQL-heavy ETL/reporting workloads often move to BigQuery
(lower ops burden, better cost/performance for analytical SQL); true streaming or complex custom
transformation logic may move to Dataflow/Beam for the serverless/unified batch-streaming benefits. Decide
case-by-case based on job complexity, team Spark skill investment, and cost.

**Q7: How do you optimize a Dataproc PySpark job's cost and runtime together?**
A: Use ephemeral clusters sized to the job (not a shared oversized cluster), autoscaling with sensible
bounds, preemptible/Spot secondary workers for the bulk of compute, GCS instead of local HDFS for
input/output (enables true cluster ephemerality), tune `spark.sql.shuffle.partitions`/executor sizing
(see [../pyspark/guide.md](../pyspark/guide.md) Q10), enable Dataproc's Enhanced Flexibility Mode for
graceful handling of preemptible worker loss during shuffle-heavy jobs, and compare against a
Dataflow/BigQuery rewrite for jobs that are mostly SQL-shaped (often cheaper/faster there).

**Q8: What monitoring/alerting do you set up for Dataproc pipelines?**
A: YARN application status/failures, cluster CPU/memory utilization, job duration trend (catch
regressions), and Cloud Logging for driver/executor stderr/stdout; alert on job failure exit codes and on
cluster creation failures/timeouts. Integrate with Cloud Composer's SLA/callback alerting for end-to-end
pipeline freshness where Dataproc jobs are orchestrated from Airflow.
