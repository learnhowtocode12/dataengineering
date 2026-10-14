# GKE Coding Questions — Round 2 Drills

## Interview Guide
Graded on correct Kubernetes resource definitions for data/ETL workloads and Workload Identity wiring —
see [../cloud_run/coding.md](../cloud_run/coding.md) for the equivalent, simpler serverless-container
patterns.

---

### Q1. Kubernetes Deployment + CronJob YAML for a containerized ETL task
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: nightly-etl
spec:
  schedule: "0 2 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          serviceAccountName: etl-ksa   # bound via Workload Identity to a GCP service account
          containers:
            - name: etl
              image: gcr.io/my-project/nightly-etl:1.2.0
              resources:
                requests: { cpu: "1", memory: "2Gi" }
                limits:   { cpu: "2", memory: "4Gi" }
          restartPolicy: OnFailure
```
**Follow-up:** "Why a CronJob here instead of Cloud Scheduler + Cloud Run?" → you'd pick GKE if this job
needs to live alongside other GKE workloads, needs a specific node pool (e.g., high-memory or GPU), or the
org has standardized tooling/monitoring around GKE already — otherwise Cloud Run Jobs is simpler and has
less infrastructure to maintain. See [../cloud_run/coding.md](../cloud_run/coding.md) Q2 for the Cloud Run
Job equivalent.

---

### Q2. Workload Identity binding (KSA to GSA)
```bash
gcloud iam service-accounts add-iam-policy-binding \
  etl-pipeline@my-project.iam.gserviceaccount.com \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:my-project.svc.id.goog[data-pipelines/etl-ksa]"

kubectl annotate serviceaccount etl-ksa \
  --namespace data-pipelines \
  iam.gke.io/gcp-service-account=etl-pipeline@my-project.iam.gserviceaccount.com
```
**Talk through:** this is the two-step binding (IAM policy binding + KSA annotation) that makes
`serviceAccountName: etl-ksa` in Q1's CronJob able to call BigQuery/GCS APIs using the GSA's permissions
without any key file — see [../gke/guide.md](../gke/guide.md) Q3 for why this matters (avoids long-lived
keys).
