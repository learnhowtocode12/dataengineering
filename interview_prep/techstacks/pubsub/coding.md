# Pub/Sub Coding Questions — Round 2 Drills

## Interview Guide
These exercises test correct use of the Pub/Sub client libraries: proper ack/nack handling, flow control,
ordering keys, and idempotent consumption — not just "can you call `publish()`." Narrate delivery
guarantees as you code (at-least-once, per-key ordering) since that's what's really being evaluated.

---

### Q1. Publish a message with an ordering key
```python
from google.cloud import pubsub_v1

publisher = pubsub_v1.PublisherClient(
    publisher_options=pubsub_v1.types.PublisherOptions(enable_message_ordering=True)
)
topic_path = publisher.topic_path("my-project", "orders")

future = publisher.publish(
    topic_path,
    data=b'{"order_id": "123", "status": "created"}',
    ordering_key="order-123",  # all events for this order_id stay in publish order
)
future.result()
```
**Talk through:** without `ordering_key`, Pub/Sub makes no ordering promise at all; setting it buffers/
retries per-key on the publisher side so messages for the *same* key arrive in order, while messages for
different keys can still interleave arbitrarily — call this out explicitly, it's the most commonly
misunderstood part of Pub/Sub.

---

### Q2. Idempotent pull subscriber
```python
from google.cloud import pubsub_v1, firestore

subscriber = pubsub_v1.SubscriberClient()
db = firestore.Client()
subscription_path = subscriber.subscription_path("my-project", "orders-sub")

def callback(message: pubsub_v1.subscriber.message.Message) -> None:
    msg_id = message.message_id
    doc_ref = db.collection("processed_messages").document(msg_id)
    if doc_ref.get().exists:
        message.ack()  # already handled - just ack and move on, don't reprocess
        return
    try:
        process(message.data)
        doc_ref.set({"processed_at": firestore.SERVER_TIMESTAMP})
        message.ack()
    except TransientError:
        message.nack()  # triggers redelivery
    except PermanentError:
        log_to_dead_letter(message.data)
        message.ack()  # don't retry something that can never succeed

streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
```
**Talk through:** the Firestore "processed markers" check is what actually makes this safe under
at-least-once redelivery; acking a permanently-failing message (after logging it) prevents an infinite
nack/redeliver loop — contrast with relying solely on a dead-letter-topic policy at the subscription level.

---

### Q3. Flow control to avoid overwhelming a slow consumer
```python
from google.cloud import pubsub_v1

flow_control = pubsub_v1.types.FlowControl(
    max_messages=100,        # at most 100 unacked messages outstanding at once
    max_bytes=10 * 1024 * 1024,
)
streaming_pull_future = subscriber.subscribe(
    subscription_path, callback=callback, flow_control=flow_control
)
```
**Follow-up:** "What happens to messages beyond the flow-control limit?" → they simply aren't pulled yet;
they stay safely in the subscription's backlog (durable, within retention) until the client has capacity —
this is the client *choosing* to slow down, not data loss.

---

### Q4. Synchronous vs. batched async publish — latency/throughput trade-off
```python
# Synchronous (simple, but blocks on each publish - low throughput)
future = publisher.publish(topic_path, data=payload)
future.result()  # blocks until server ack

# Batched async (high throughput - the client library batches under the hood)
batch_settings = pubsub_v1.types.BatchSettings(
    max_messages=500, max_bytes=1024 * 1024, max_latency=0.05,
)
publisher = pubsub_v1.PublisherClient(batch_settings=batch_settings)
futures = [publisher.publish(topic_path, data=p) for p in payloads]
for f in futures:
    f.result()  # resolve at the end, not after each individual publish
```
**Talk through:** calling `.result()` immediately after every single `publish()` serializes network
round-trips and kills throughput; batch settings let the client coalesce many small messages into fewer
network requests — this is the #1 performance mistake candidates make when asked to "publish 10,000
messages."

---

### Q5. Configure a dead-letter policy on a subscription (infra-as-code, gcloud)
```bash
gcloud pubsub subscriptions create orders-sub \
  --topic=orders \
  --dead-letter-topic=orders-dead-letter \
  --max-delivery-attempts=5 \
  --ack-deadline=30
```
**Follow-up:** "What IAM is required for this to actually work?" → the Pub/Sub service agent needs
`roles/pubsub.publisher` on the dead-letter topic and `roles/pubsub.subscriber` on the main subscription —
a commonly forgotten step that silently breaks dead-lettering if missed.

---

### Q6. Seek a subscription back to a snapshot (replay after a bad deploy)
```python
from google.cloud import pubsub_v1

subscriber = pubsub_v1.SubscriberClient()
snapshot_path = subscriber.snapshot_path("my-project", "pre-deploy-snapshot")
subscriber.seek(request={
    "subscription": subscription_path,
    "snapshot": snapshot_path,
})
```
**Talk through:** take the snapshot *before* rolling out a risky consumer change; if the new code turns out
to be broken, seeking back to the snapshot redelivers everything published since that point, giving you a
clean replay instead of a manual data-recovery effort.

---

### Q7. Exactly-once delivery subscription (infra config + consumer note)
```bash
gcloud pubsub subscriptions create orders-sub-eos \
  --topic=orders \
  --enable-exactly-once-delivery
```
```python
def callback(message):
    ack_result_future = message.ack_with_response()
    try:
        ack_result_future.result(timeout=20)  # confirms the ack was durably recorded
    except pubsub_v1.subscriber.exceptions.AcknowledgeError as e:
        logging.warning(f"Ack failed, message may be redelivered: {e}")
```
**Talk through:** exactly-once delivery guarantees a message is acked exactly once *to this subscription*
within its tracking window — you still must check the ack actually succeeded (`ack_with_response`) rather
than fire-and-forget acking, and your processing logic should still be written idempotently as defense in
depth for anything outside that guarantee's scope (e.g., cross-subscription replays via seek).

---

### Q8. Push subscription handler (Flask/Cloud Run) with correct status-code semantics
```python
from flask import Flask, request
import base64, json

app = Flask(__name__)

@app.route("/push-handler", methods=["POST"])
def push_handler():
    envelope = request.get_json()
    if not envelope or "message" not in envelope:
        return "Bad Request", 400  # malformed envelope - Pub/Sub will retry per its policy

    data = json.loads(base64.b64decode(envelope["message"]["data"]))
    try:
        process(data)
    except TransientError:
        return "retry", 500  # non-2xx => nacked => redelivered
    return "", 204  # 2xx => acked
```
**Why it's asked:** identical reasoning applies to a push subscription hosted on Cloud Run or Cloud
Functions instead of this example's handler — interviewers like to see you recognize it's the same
ack/nack-via-HTTP-status pattern regardless of which compute service hosts it (see
[../cloud_run/coding](../cloud_run/coding.md) Q3).
