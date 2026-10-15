# Cloud Tasks — Interview Guide & Q&A
> **Round mapping:** R2 (technical deep dive). See also [../pubsub/guide](../pubsub/guide.md) (the
> messaging alternative — expect a comparison question) and
> [../cloud_workflows/guide](../cloud_workflows/guide.md) Q3 for a design scenario using Cloud Tasks
> alongside Workflows and Scheduler.

## Interview Guide
Cloud Tasks questions check whether you understand it as a **rate-controlled, per-task dispatch queue**,
distinct from Pub/Sub's fan-out messaging model — this distinction is one of the most commonly tested
"compare these two GCP services" questions in this stack.

---

## Q&A

**Q1: What is Cloud Tasks and how does it differ from Pub/Sub?**

**Answer:** Cloud Tasks is a managed **push-based task queue** designed for asynchronous execution of individual
units of work with fine-grained control: per-queue rate limiting, max concurrent dispatches, scheduled/
delayed execution per task, automatic retries with configurable backoff, and guaranteed (at most one
in-flight, in order within some constraints) delivery to a specific HTTP target (Cloud Run/Functions/App
Engine/any HTTP endpoint). Pub/Sub is a **pub-sub messaging** system for fan-out to multiple independent
subscribers, higher throughput, and decoupled producers/consumers, but with less built-in per-task
scheduling/rate-limiting control. Rule of thumb: use Cloud Tasks when you need to control the *rate* and
*timing* of calls to a specific downstream service (e.g., "call this API at most 5/sec, retry failures
individually"); use Pub/Sub for event broadcasting/decoupled architectures with potentially many consumer
types.

**Q2: Give a data-engineering use case for Cloud Tasks.**

**Answer:** Fan-out per-file processing: a Cloud Function triggered by a GCS upload enumerates thousands of
individual records/sub-files and enqueues one Cloud Task per item targeting a Cloud Run processing
endpoint, with the queue's rate-limiting protecting a downstream rate-limited third-party API, and
built-in per-task retry/backoff handling transient failures without custom retry code in your service.
