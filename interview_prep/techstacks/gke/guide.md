# GKE (Google Kubernetes Engine) — Interview Guide & Q&A
> **Round mapping:** R2 (technical deep dive). Hands-on drills: [coding.md](coding.md). See also
> [../cloud_run/guide.md](../cloud_run/guide.md) and [../cloud_functions/guide.md](../cloud_functions/guide.md)
> — expect a three-way comparison question across all three compute options.

## Interview Guide
For a data engineer (not a pure platform/SRE role), GKE questions check whether you know *when data
workloads actually need Kubernetes* instead of serverless, and whether you understand GKE-specific
security patterns (Workload Identity) that come up whenever a pipeline runs inside a pod.

---

## Q&A

**Q1: What is GKE, and when do data workloads actually need it instead of Cloud Run/Cloud Functions?**
A: GKE gives full Kubernetes control — best when you need long-running stateful workloads, fine-grained
resource/node control, custom networking, multiple tightly-coupled services needing a service mesh, GPU
scheduling, or you're already standardized on Kubernetes org-wide and want consistency/portability across
clouds. For a data engineer specifically: running a containerized ETL microservice that needs a specific
node pool (high-memory, GPU), or hosting Cloud Composer itself (Composer runs on GKE under the hood).

**Q2: Explain how you'd deploy a containerized PySpark-adjacent or custom Python ETL microservice to
GKE, and why GKE over Cloud Run in that case.**
A: Build a Docker image with the app + dependencies, deploy via a `Deployment` (for always-on services) or
`CronJob`/`Job` (for scheduled/batch tasks) with resource requests/limits, HPA (Horizontal Pod Autoscaler)
for load-based scaling, and secrets via mounted `Secret` objects synced from Secret Manager (e.g., via
External Secrets Operator) or Workload Identity for GCP API auth from pods without key files (see Q3).
Choose GKE over [Cloud Run](../cloud_run/guide.md) when you need: custom node pools (e.g., GPU nodes,
high-memory nodes), persistent volumes/stateful sets, more complex networking (VPC-native pods, service
mesh for many microservices talking to each other), fine-grained autoscaling/bin-packing control, or very
long-running/always-on workloads where Kubernetes' scheduling efficiency beats per-request serverless
billing at scale.

**Q3: What is Workload Identity on GKE and why does it matter for data pipelines running in pods?**
A: Workload Identity lets a Kubernetes service account impersonate a GCP IAM service account without
mounting a downloaded JSON key into the pod — the pod authenticates to GCP APIs (BigQuery, GCS, etc.)
using short-lived, automatically rotated credentials bound to its KSA-to-GSA mapping. This avoids the
security risk of long-lived service account keys sitting in container images/config, which is a common
audit finding; it's the GKE equivalent of Cloud Run/Functions' attached service account model. See
[../gcp_fundamentals/guide.md](../gcp_fundamentals/guide.md) Q2 for the broader IAM best-practices context.

**Q4: How do you handle secrets and configuration on GKE?**
A: GKE typically needs either the Secret Manager CSI driver or an operator (External Secrets Operator) to
sync Secret Manager values into native Kubernetes `Secret` objects consumed by pods, since Kubernetes
doesn't natively know about GCP Secret Manager — unlike Cloud Run/Functions, which can mount Secret
Manager values directly with no extra sync mechanism.
