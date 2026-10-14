# Cloud Pub/Sub & Messaging — Interview Guide & Q&A
> **Round mapping:** R2 (technical deep dive) — almost always discussed as part of a streaming-ingestion
> system design question too (R3). Hands-on drills:
> [coding.md](coding.md).

## Interview Guide
Pub/Sub is the messaging backbone behind almost every GCP streaming story — it's the thing sitting in
front of Dataflow, triggering Cloud Functions/Run, and decoupling microservices. At 6+ years, interviewers
expect you to know its **delivery guarantees precisely** (not just "it's reliable"), how ordering actually
works (it's per-key, not global), how to handle duplicates/poison messages, and how to reason about it
versus Kafka and versus Cloud Tasks — three tools candidates commonly blur together.

---

## Q&A

**Q1: Explain the core Pub/Sub model: topic, subscription, publisher, subscriber.**
A: Publishers send messages to a **topic**, which is just a named resource with no knowledge of
consumers. A **subscription** is an independent, durable queue attached to a topic — every subscription
gets its own copy of every message published after it was created (fan-out), so multiple independent
consumers can each process the full stream without interfering with each other. **Subscribers** pull (or
receive pushed) messages from a subscription and must **ack** each one; unacked messages are redelivered
after the ack deadline expires.

**Q2: What delivery guarantee does Pub/Sub actually provide, and how do you handle duplicates?**
A: At-least-once delivery by default — a message can be redelivered (e.g., if an ack arrives late, or
after a subscriber crash before acking), so consumers must be **idempotent**. Standard approaches: track a
processed-message-ID set in a fast store (Firestore/Redis/Memorystore) and skip reprocessing, or design
the downstream write itself to be idempotent (a `MERGE` keyed on a business key rather than blind insert).
Pub/Sub also offers an **exactly-once delivery** feature on subscriptions — within a 10-minute window it
guarantees a message is acked exactly once across retries *to that subscription*, which removes most
duplicate-delivery cases but doesn't replace idempotent downstream design as a safety net for retries
outside that window or for replays.

**Q3: Push vs. pull subscriptions — when do you use each?**
A: **Pull** subscriptions have the subscriber actively call the API to fetch messages — gives the consumer
full control over concurrency/flow control and is the natural fit for Dataflow, custom workers, or
anything that needs to batch/throttle its own processing rate. **Push** subscriptions have Pub/Sub call an
HTTPS endpoint (e.g., Cloud Run/Cloud Functions) for each message — simpler (no polling loop to write) and
a natural fit for lightweight serverless handlers, but you give up fine-grained control over concurrency to
Pub/Sub's own push behavior and must handle auth (OIDC token) and ack/nack purely via HTTP status codes
(2xx acks, 5xx/timeout nacks and triggers redelivery).

**Q4: How does message ordering work in Pub/Sub?**
A: Pub/Sub does **not** guarantee global ordering across a topic. If you need ordering, you publish with
an **ordering key** — messages sharing the same key are delivered to subscribers in the order they were
published, but ordering is only guaranteed *within* a key, not across keys, and only when the publisher
also enables message ordering client-side (which buffers/retries per-key to preserve order even across
transient publish failures). This is a common trick question: "does Pub/Sub guarantee ordering?" → "only
per ordering key, and only if you opt in — never globally."

**Q5: How do you handle a "poison message" that a subscriber can never successfully process?**
A: Configure a **dead-letter topic** on the subscription with a `max_delivery_attempts` threshold — after
that many failed delivery attempts (nack or ack-deadline-exceeded), Pub/Sub automatically forwards the
message to the dead-letter topic instead of retrying forever, and you handle it out-of-band (alerting,
manual inspection, reprocessing after a fix) instead of letting it block/slow the main subscription
indefinitely.

**Q6: How do you handle a slow consumer / backpressure in Pub/Sub?**
A: On the pull/client side, **flow control** settings (`max_outstanding_messages`, `max_outstanding_bytes`)
cap how much unacked work a client pulls at once, preventing it from overwhelming itself; Pub/Sub's own
backlog just grows (durably, up to the retention period) if the subscriber falls behind, which is the
desired behavior — the queue absorbs bursts rather than dropping data. For Dataflow specifically, this
surfaces as **subscription backlog/age** metrics that drive Dataflow's autoscaling (more workers spun up
as backlog grows).

**Q7: What are Pub/Sub schemas, and why use them?**
A: You can attach an Avro or Protocol Buffer schema to a topic so Pub/Sub validates (and optionally
rejects) messages that don't conform at publish time — this enforces a producer/consumer contract at the
messaging layer itself, catching a breaking schema change from a producer team before it silently breaks
every downstream consumer, instead of discovering it as a parsing failure deep in a Dataflow pipeline.

**Q8: Pub/Sub vs. Kafka — how do you frame the comparison?**
A: Pub/Sub is fully managed/serverless (no brokers/partitions to size or rebalance, scales automatically,
pay-per-use) with ordering-key-based ordering and a simpler mental model; Kafka (self-managed or via
Confluent/managed offerings) gives you explicit partitions, consumer groups, longer configurable retention
by default, and a broader ecosystem (Kafka Streams, Connect) but with real operational overhead (or
third-party managed cost) to size/tune. Pick Pub/Sub by default on GCP for lower operational burden; pick
Kafka when you have existing Kafka investment/skills, need features Pub/Sub lacks, or are deliberately
multi-cloud/portable. (Also worth knowing: Google's own **Pub/Sub Lite** offering has been deprecated in
favor of pushing Kafka-compatible workloads toward managed Kafka options — mention this only if asked, to
show you're current.)

**Q9: Pub/Sub vs. Cloud Tasks — when do you pick each?** *(cross-reference)*
A: See [../cloud_tasks/guide.md](../cloud_tasks/guide.md) Q1 for the full comparison — short
version: Pub/Sub is for **fan-out event broadcasting** to decoupled, possibly-many consumers; Cloud Tasks
is for **controlling the rate/timing of calls to one specific downstream service** with built-in per-task
scheduling and retry/backoff.

**Q10: How do you replay or backfill historical messages?**
A: **Seek** a subscription to a past timestamp (within the retention window) to redeliver everything
published since then, or create a **snapshot** at a known-good point before a risky deploy so you can seek
back to it if the new consumer code turns out to be broken. For true long-term replay beyond retention,
you need the data landed somewhere durable already (GCS/BigQuery) and a separate batch reprocessing job —
Pub/Sub itself is not a long-term archival store (retention defaults to 7 days, configurable up to 31).

**Q11: Can Pub/Sub write directly to BigQuery without Dataflow?**
A: Yes — **BigQuery subscriptions** let a subscription write matching-schema messages directly into a
BigQuery table without a Dataflow job in between, for the simple case where no transformation/windowing is
needed before landing. Use this for straightforward "land raw events into a table" cases; reach for
Dataflow when you need parsing/validation/windowed aggregation/dead-lettering logic in between.

**Q12: How do you secure Pub/Sub topics/subscriptions?**
A: IAM roles at the topic level (`roles/pubsub.publisher`) and subscription level
(`roles/pubsub.subscriber`) scoped to specific service accounts rather than broad project-level grants;
CMEK (customer-managed encryption keys) if compliance requires control over the encryption key; and for
push subscriptions, requiring OIDC authentication so only an authorized service account can trigger the
push endpoint (same pattern as securing Cloud Workflows → Cloud Run calls).

**Q13: What metrics do you monitor/alert on for a production Pub/Sub-based pipeline?**
A: **Oldest unacked message age** and **num undelivered messages** (subscription backlog) are the primary
health signals — a growing backlog means consumers can't keep up. Also: publish/pull request error rates,
and (if using ordering keys) rare but important per-key delivery-paused states if an ordering key's message
fails repeatedly (Pub/Sub pauses delivery for that specific key until resolved, to preserve order — this
is a subtle failure mode worth knowing about explicitly).

**Q14: Design scenario — ingest high-throughput IoT sensor data (millions of devices) reliably.**
A: Devices publish to a Pub/Sub topic (possibly through a lightweight gateway/Cloud IoT-successor service
for device auth); a Dataflow streaming pipeline subscribes, applies windowed aggregation and dead-letters
malformed payloads, writes aggregates to BigQuery and/or Bigtable (if per-device time-series lookups need
low-latency point reads); a second subscription on the same topic feeds a real-time alerting path (e.g., a
Cloud Function checking threshold breaches) — this fan-out-to-two-subscriptions pattern (one topic, two
independent subscriptions for two different consumption needs) is the key design point to call out
unprompted.

**Q15: What's the difference between the ack deadline and message retention, and why do both matter?**
A: **Ack deadline** (default 10s, extendable up to 600s, or indefinitely via streaming pull lease
management) is how long a subscriber has to ack a single delivered message before Pub/Sub assumes failure
and redelivers it — tune this to comfortably exceed your typical processing time per message to avoid
spurious redeliveries. **Message retention** (default 7 days) is how long an unacked (or, if configured,
even acked) message stays available in the subscription at all — this is what makes seek/replay possible,
and is a separate dial from the ack deadline entirely; conflating the two is a common mistake.
