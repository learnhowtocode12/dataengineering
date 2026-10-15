# Python Coding Questions — Round 1 / Round 2 Drills

## Interview Guide
This is typically a **live-coding, shared-editor** exercise (CoderPad/HackerRank-style, or screen-share in
VS Code) — talk out loud, ask clarifying questions about input assumptions (nulls? duplicates? sort order?
scale?), state the time/space complexity of your approach before and after coding, and write runnable code
rather than pseudocode when possible. For a 6 YOE data engineer, problems lean "data munging" rather than
pure algorithmic trivia — but a clean, correct, idiomatic solution matters more than cleverness.

---

### Q1. Flatten a nested JSON object (common for API ingestion before loading to BigQuery)
**Problem:** Given an arbitrarily nested dict, return a single-level dict with underscore-joined keys.
```python
def flatten(d: dict, parent_key: str = "", sep: str = "_") -> dict:
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten(v, new_key, sep))
        else:
            items[new_key] = v
    return items

# flatten({"a": 1, "b": {"c": 2, "d": {"e": 3}}}) -> {"a": 1, "b_c": 2, "b_d_e": 3}
```
**Complexity:** O(n) where n = total number of leaf+branch keys. **Follow-up:** "What if a value is a
list of dicts?" — discuss keeping it as a repeated field for BigQuery vs. exploding into multiple rows
(a join/cross-product decision, not a pure coding one).

---

### Q2. Deduplicate records, keeping the latest by timestamp
**Problem:** Given `records = [{"id": 1, "ts": 100, "val": "a"}, {"id": 1, "ts": 200, "val": "b"}, ...]`,
return one record per `id`, the one with the max `ts`.
```python
def dedupe_latest(records: list[dict]) -> list[dict]:
    latest: dict[int, dict] = {}
    for r in records:
        existing = latest.get(r["id"])
        if existing is None or r["ts"] > existing["ts"]:
            latest[r["id"]] = r
    return list(latest.values())
```
**Complexity:** O(n) time, O(k) space for k unique ids. **Follow-up:** "How would this change if the input
were too large for memory?" → sort by `(id, ts)` externally / process in a stream keeping only the current
best per key, or push the dedupe down into a SQL `ROW_NUMBER()` query instead.

---

### Q3. Group and aggregate without pandas
**Problem:** Given `sales = [{"category": "A", "revenue": 10}, {"category": "B", "revenue": 5}, ...]`,
return total revenue per category, sorted descending.
```python
from collections import defaultdict

def revenue_by_category(sales: list[dict]) -> list[tuple[str, float]]:
    totals: dict[str, float] = defaultdict(float)
    for s in sales:
        totals[s["category"]] += s["revenue"]
    return sorted(totals.items(), key=lambda kv: kv[1], reverse=True)
```
**Follow-up:** "Top 3 per category instead of totals" — bridges naturally into the PySpark/SQL window
function version (see [../pyspark/coding](../pyspark/coding.md) Q3 and
[../bigquery/coding](../bigquery/coding.md)).

---

### Q4. Generator to read a huge file in fixed-size batches
**Problem:** Write a generator that yields lists of `batch_size` lines at a time from a large file, without
loading the whole file into memory.
```python
def batched_lines(path: str, batch_size: int = 1000):
    with open(path) as f:
        batch = []
        for line in f:
            batch.append(line.rstrip("\n"))
            if len(batch) == batch_size:
                yield batch
                batch = []
        if batch:
            yield batch
```
**Why it matters:** this is the pattern behind processing multi-GB GCS files in a Cloud Function/Cloud Run
job without OOMing. **Follow-up:** "How would you parallelize this?" → split by byte offset ranges, or
hand off to Dataflow/Spark for true distributed processing instead of single-process batching.

---

### Q5. Retry-with-backoff decorator
**Problem:** Write a decorator that retries a function on exception, with exponential backoff, up to
`max_attempts`.
```python
import time
import functools
import random

def retry(max_attempts=3, base_delay=1.0):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    if attempt == max_attempts:
                        raise
                    delay = base_delay * (2 ** (attempt - 1)) + random.uniform(0, 0.5)
                    time.sleep(delay)
        return wrapper
    return decorator

@retry(max_attempts=3, base_delay=0.5)
def call_flaky_api():
    ...
```
**Follow-up:** "What exceptions should you NOT retry?" → non-transient errors (4xx auth/validation
errors) — only retry transient/5xx/timeout-type failures; discuss jitter to avoid thundering-herd retries.

---

### Q6. Merge overlapping intervals (maps to session-window logic)
**Problem:** Given a list of `(start, end)` time ranges, merge all overlapping/adjacent ranges.
```python
def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not intervals:
        return []
    intervals = sorted(intervals)
    merged = [intervals[0]]
    for start, end in intervals[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end:
            merged[-1] = (last_start, max(last_end, end))
        else:
            merged.append((start, end))
    return merged
```
**Complexity:** O(n log n) for the sort. **Follow-up:** directly connects to sessionization (Q14 in
[../pyspark/guide](../pyspark/guide.md)) — "how would this generalize to per-user session gaps at
scale?" → window functions in Spark/SQL instead of a single-threaded merge.

---

### Q7. Top-K elements (e.g., top 5 products by revenue) without full sort
**Problem:** Given a large list of `(product_id, revenue)`, return the top K by revenue efficiently.
```python
import heapq

def top_k(items: list[tuple[str, float]], k: int) -> list[tuple[str, float]]:
    return heapq.nlargest(k, items, key=lambda x: x[1])
```
**Complexity:** O(n log k) vs. O(n log n) for a full sort — explain why this matters when `n` is huge and
`k` is small. **Follow-up:** "How would you do this if the data didn't fit in memory?" → maintain a
min-heap of size k while streaming, or push the top-N down to BigQuery/Spark.

---

### Q8. Simple token-bucket rate limiter
**Problem:** Implement a rate limiter allowing at most `rate` calls per `per_seconds` window (ties to the
Cloud Tasks rate-limiting concept in [../cloud_tasks/guide](../cloud_tasks/guide.md)).
```python
import time

class TokenBucket:
    def __init__(self, rate: int, per_seconds: float):
        self.capacity = rate
        self.tokens = rate
        self.refill_rate = rate / per_seconds
        self.last_check = time.monotonic()

    def allow(self) -> bool:
        now = time.monotonic()
        elapsed = now - self.last_check
        self.last_check = now
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False
```
**Follow-up:** "How would this work across multiple processes/instances?" → needs a shared store (Redis/
Memorystore) instead of in-process state — good segue into distributed-systems thinking.

---

### Q9. Detect schema drift between two records
**Problem:** Given an old and a new record (dicts), return which keys were added, removed, and which had a
type change.
```python
def diff_schema(old: dict, new: dict) -> dict:
    old_keys, new_keys = set(old), set(new)
    added = new_keys - old_keys
    removed = old_keys - new_keys
    type_changed = {
        k for k in old_keys & new_keys
        if type(old[k]) is not type(new[k])
    }
    return {"added": added, "removed": removed, "type_changed": type_changed}
```
**Why it matters:** directly maps to the schema-evolution discussion in
[../bigquery/guide](../bigquery/guide.md) Q12 — a nice way to connect a coding answer to a real pipeline
concern.

---

### Q10. LRU cache (common for "cache expensive lookups" scenarios)
**Problem:** Implement an LRU cache with `get`/`put` in O(1).
```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache: OrderedDict = OrderedDict()

    def get(self, key):
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key, value) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
```
**Follow-up:** mention `functools.lru_cache` exists for the common case — but be ready to implement it by
hand, since that's exactly what's being tested. "How would you make this thread-safe?" → wrap mutating
calls with a lock.

---

### Q11. Parse and validate malformed log lines
**Problem:** Given raw log lines like `"2024-01-01T10:00:00Z|user123|LOGIN|200"`, parse into structured
records, skipping/collecting malformed lines separately (dead-letter pattern).
```python
from dataclasses import dataclass

@dataclass
class LogEvent:
    timestamp: str
    user_id: str
    event_type: str
    status_code: int

def parse_logs(lines: list[str]) -> tuple[list[LogEvent], list[str]]:
    good, bad = [], []
    for line in lines:
        parts = line.strip().split("|")
        if len(parts) != 4:
            bad.append(line)
            continue
        ts, user_id, event_type, status = parts
        try:
            good.append(LogEvent(ts, user_id, event_type, int(status)))
        except ValueError:
            bad.append(line)
    return good, bad
```
**Why it matters:** mirrors the Beam dead-letter `ParDo` pattern (see
[../dataflow/coding](../dataflow/coding.md) Q2) — good to explicitly say
"this is the same pattern I'd use with a `TaggedOutput` in a Beam `DoFn`."

---

### Q12. Two-pointer / sliding window: longest run without exceeding a threshold
**Problem:** Given a list of daily data volumes, find the longest contiguous run of days whose total stays
under a storage budget `limit`.
```python
def longest_run_under_budget(volumes: list[int], limit: int) -> int:
    left = 0
    total = 0
    best = 0
    for right, v in enumerate(volumes):
        total += v
        while total > limit:
            total -= volumes[left]
            left += 1
        best = max(best, right - left + 1)
    return best
```
**Complexity:** O(n) sliding window vs. a naive O(n²) — explicitly call out why the window approach works
(monotonic prefix sums as the window only grows and shrinks from aligned ends).
