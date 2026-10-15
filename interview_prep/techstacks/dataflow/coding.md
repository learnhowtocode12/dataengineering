# Dataflow / Apache Beam Coding Questions — Round 2 Drills

## Interview Guide
Beam questions are graded on whether you understand the **PCollection/PTransform/DoFn** model well enough
to write correct, idempotent, side-output-aware code — not on memorizing every method signature. It's
fine to write Python Beam SDK code slightly loosely (interviewers rarely expect it to compile perfectly
from memory) as long as the structure and reasoning (windowing, triggers, side outputs) are right.

---

### Q1. Classic word count (the "hello world" of Beam — keep it short, move on fast)
```python
import apache_beam as beam

with beam.Pipeline() as p:
    (
        p
        | "Read" >> beam.io.ReadFromText("gs://bucket/input.txt")
        | "Split" >> beam.FlatMap(lambda line: line.split())
        | "PairWithOne" >> beam.Map(lambda word: (word, 1))
        | "GroupAndSum" >> beam.CombinePerKey(sum)
        | "Format" >> beam.Map(lambda kv: f"{kv[0]}: {kv[1]}")
        | "Write" >> beam.io.WriteToText("gs://bucket/output")
    )
```
**Talk through:** `CombinePerKey(sum)` instead of `GroupByKey()` + manual summing — `sum` is associative/
commutative, so Beam can partially combine on the mapper side before the shuffle, just like a Spark
combiner.

---

### Q2. ParDo with a side output for dead-lettering malformed records
```python
import apache_beam as beam
from apache_beam.pvalue import TaggedOutput

class ParseAndValidate(beam.DoFn):
    OUTPUT_TAG_DEAD_LETTER = "dead_letter"

    def process(self, element):
        try:
            record = parse_json(element)
            if "user_id" not in record:
                raise ValueError("missing user_id")
            yield record
        except Exception as e:
            yield TaggedOutput(self.OUTPUT_TAG_DEAD_LETTER, {"raw": element, "error": str(e)})

results = (
    raw_messages
    | "ParseAndValidate" >> beam.ParDo(ParseAndValidate()).with_outputs(
        ParseAndValidate.OUTPUT_TAG_DEAD_LETTER, main="parsed"
    )
)
results.parsed | "WriteGood" >> beam.io.WriteToBigQuery(...)
results.dead_letter | "WriteBad" >> beam.io.WriteToText("gs://bucket/dead-letter/")
```
**Why it matters:** this is the single most-asked Beam coding pattern in interviews because it tests
whether you design for failure by default, not just the happy path.

---

### Q3. Windowed aggregation with early/late triggers
```python
import apache_beam as beam
from apache_beam.transforms import trigger
from apache_beam.transforms.window import FixedWindows

windowed_counts = (
    events
    | "Window" >> beam.WindowInto(
        FixedWindows(60),  # 1-minute windows
        trigger=trigger.AfterWatermark(
            early=trigger.AfterProcessingTime(10),   # speculative results every 10s
            late=trigger.AfterCount(1),               # emit again on any late record
        ),
        accumulation_mode=trigger.AccumulationMode.ACCUMULATING,
        allowed_lateness=3600,  # tolerate up to 1 hour of late data
    )
    | "CountPerKey" >> beam.combiners.Count.PerKey()
)
```
**Talk through:** `ACCUMULATING` mode re-emits the full updated total on every trigger firing (vs.
`DISCARDING`, which emits only the delta since the last firing) — pick based on whether the downstream
sink overwrites or needs to sum deltas itself.

---

### Q4. Pub/Sub to BigQuery streaming pipeline skeleton
```python
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions

options = PipelineOptions(streaming=True)
options.view_as(StandardOptions).runner = "DataflowRunner"

with beam.Pipeline(options=options) as p:
    (
        p
        | "ReadPubSub" >> beam.io.ReadFromPubSub(subscription="projects/proj/subscriptions/events-sub")
        | "Decode" >> beam.Map(lambda b: json.loads(b.decode("utf-8")))
        | "ParseAndValidate" >> beam.ParDo(ParseAndValidate()).with_outputs(
            ParseAndValidate.OUTPUT_TAG_DEAD_LETTER, main="parsed"
          ).parsed
        | "WriteBQ" >> beam.io.WriteToBigQuery(
            table="proj:dataset.events",
            write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
            method=beam.io.WriteToBigQuery.Method.STORAGE_WRITE_API,
          )
    )
```
**Talk through:** explicitly naming `STORAGE_WRITE_API` as the write method — call out that this is the
modern, higher-throughput, lower-cost path versus legacy streaming inserts (ties back to
[../bigquery/guide](../bigquery/guide.md) Q11).

---

### Q5. Side input: broadcasting a small lookup table to every worker
```python
import apache_beam as beam

lookup_dict_view = (
    pipeline
    | "ReadLookup" >> beam.io.ReadFromText("gs://bucket/country_codes.csv")
    | "ParseLookup" >> beam.Map(parse_lookup_row)
    | "ToDict" >> beam.combiners.ToDict()
)

def enrich(element, lookup):
    element["country_name"] = lookup.get(element["country_code"], "UNKNOWN")
    return element

enriched = main_pcollection | "Enrich" >> beam.Map(
    enrich, lookup=beam.pvalue.AsSingleton(lookup_dict_view)
)
```
**Talk through:** this is Beam's equivalent of a Spark broadcast join — the lookup is materialized once
and made available to every worker instead of requiring a shuffle-based join against the main, much larger
PCollection.

---

### Q6. Custom CombineFn for a running average
```python
import apache_beam as beam

class AverageFn(beam.CombineFn):
    def create_accumulator(self):
        return (0.0, 0)  # (sum, count)

    def add_input(self, accumulator, input):
        total, count = accumulator
        return total + input, count + 1

    def merge_accumulators(self, accumulators):
        totals, counts = zip(*accumulators)
        return sum(totals), sum(counts)

    def extract_output(self, accumulator):
        total, count = accumulator
        return total / count if count else float("nan")

averages = values | beam.CombineGlobally(AverageFn())
```
**Talk through:** `merge_accumulators` is what makes this parallelizable — partial accumulators computed
on different workers/bundles can be merged without re-reading the raw data, which is the whole point of
the Combiner pattern over a naive `GroupByKey` + Python-side average.

---

### Q7. Testing a Beam pipeline with `TestPipeline` and `assert_that`
```python
import unittest
import apache_beam as beam
from apache_beam.testing.test_pipeline import TestPipeline
from apache_beam.testing.util import assert_that, equal_to

class WordCountTest(unittest.TestCase):
    def test_word_count(self):
        with TestPipeline() as p:
            input_data = p | beam.Create(["hello world", "hello beam"])
            output = (
                input_data
                | beam.FlatMap(str.split)
                | beam.Map(lambda w: (w, 1))
                | beam.CombinePerKey(sum)
            )
            assert_that(output, equal_to([("hello", 2), ("world", 1), ("beam", 1)]))
```
**Why it matters:** runs on `DirectRunner` locally with no GCP cost — the standard way Beam pipelines are
unit-tested in CI before ever touching `DataflowRunner`.

---

### Q8. Stateful DoFn: deduplicate events by key within a time window
```python
import apache_beam as beam
from apache_beam.transforms.userstate import BagStateSpec
from apache_beam.coders import StrUtf8Coder

class DedupeByKey(beam.DoFn):
    SEEN = BagStateSpec("seen", StrUtf8Coder())

    def process(self, element, seen=beam.DoFn.StateParam(SEEN)):
        key, event_id = element
        already_seen = list(seen.read())
        if event_id in already_seen:
            return  # drop duplicate
        seen.add(event_id)
        yield element
```
**Talk through:** state is scoped per key (and per window, if windowed) and persisted by the runner across
bundles — call out that unbounded state growth is a real risk here, so pair this with a window/TTL
strategy rather than keeping state forever.

---

### Q9. Debug exercise: pipeline produces different output on retries
**Prompt:** "This `DoFn` calls `random.random()` to sample 10% of records for a QA table. QA sees
inconsistent counts between runs on identical input — why, and how do you fix it?"
**Answer:** Beam bundles can be **retried** on worker failure, and a non-deterministic `DoFn` (using
unseeded randomness, wall-clock time, or external mutable state) produces different output on each retry
of the same bundle, breaking Beam's exactly-once processing guarantees which assume deterministic
re-execution. **Fix:** derive the random decision deterministically from the record itself, e.g.
`hashlib.md5(event_id.encode()).hexdigest()` mapped into a `[0, 1)` range, so re-processing the same
record always yields the same sampling decision.

---

### Q10. Flex template skeleton (conceptual, not full code)
```dockerfile
# Dockerfile
FROM gcr.io/dataflow-templates-base/python3-template-launcher-base
COPY requirements.txt pipeline.py /template/
RUN pip install -r /template/requirements.txt
ENV FLEX_TEMPLATE_PYTHON_PY_FILE=/template/pipeline.py
```
```json
// metadata.json
{
  "name": "My Flex Template",
  "parameters": [
    {"name": "input_subscription", "label": "Pub/Sub subscription", "paramType": "TEXT"},
    {"name": "output_table", "label": "BigQuery table", "paramType": "TEXT"}
  ]
}
```
**Talk through:** the pipeline reads parameters at runtime (not baked in at build time like a classic
template), which is why Flex templates support dynamic pipeline construction — e.g., choosing a different
transform graph based on a parameter — that classic templates can't.
