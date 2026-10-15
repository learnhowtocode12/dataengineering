# Python — Interview Guide & Q&A
> **Round mapping:** R1 (coding screen) & R2 (deep dive). Hands-on drills:
> [coding](coding.md). Related: [../pyspark/guide](../pyspark/guide.md) (PySpark builds directly on
> these Python fundamentals).

## Interview Guide
At 6+ years, interviewers expect fluency in:
- **Python internals**: GIL, memory model, generators, decorators, context managers, mutable default
  argument pitfalls, `*args/**kwargs`, typing, packaging.
- **Production coding**: writing idiomatic, testable ETL code (not just notebooks) — modular
  transformations, unit tests with `pytest`, logging, config-driven jobs.
- **Live coding**: expect a coding round with a data-munging task (e.g., "given this list/dict, compute X")
  done in plain Python, sometimes on a shared editor/replit without full IDE support.

Common format: 45-60 min round, 1-2 conceptual questions + 1 live coding problem (e.g., dedupe records,
flatten nested data, config-driven job design).

---

## Q&A

**Q1: What is the GIL and how does it affect Python data pipelines?**

**Answer:** The Global Interpreter Lock allows only one thread to execute Python bytecode at a time in CPython,
so pure Python multithreading doesn't give CPU parallelism (it still helps for I/O-bound work). This is
why CPU-bound Python work uses multiprocessing or hands off computation to native/JVM code — see
[../pyspark/guide](../pyspark/guide.md) Q1 for how PySpark specifically sidesteps this by running the
actual data processing in the JVM.

**Q2: Explain generators vs lists, and when you'd use a generator in a data pipeline.**

**Answer:** A list materializes all elements in memory; a generator produces values lazily, one at a time, via
`yield`, so memory stays O(1) relative to input size. In data engineering, generators are used when
streaming large files line-by-line (e.g., reading a multi-GB file from GCS and yielding parsed rows),
building ETL pipelines that chain transformations without materializing intermediate collections, or
implementing custom iterators for pagination against an API.

**Q3: Mutable default arguments — what's the bug?**
```python
def add_item(item, bucket=[]):
    bucket.append(item)
    return bucket
```

**Answer:** The default list is created once at function definition time and shared across all calls that don't
pass `bucket` explicitly, so state leaks between calls. Fix: use `None` as default and create the list
inside the function body (`bucket = bucket if bucket is not None else []`).

**Q4: Explain decorators and give a data-engineering use case.**

**Answer:** A decorator wraps a function to add behavior without modifying its code — implemented as a higher-order
function (or class with `__call__`) that takes a function and returns a new function. Common ETL use
cases: `@retry` (retry transient GCS/BigQuery API failures with backoff), `@timing`/`@log_execution`
(instrument pipeline step duration for monitoring), `@deprecated`, caching (`functools.lru_cache`) for
expensive lookups (e.g., reference data).

**Q5: Context managers — why use `with open(...)` and how do you write a custom one?**

**Answer:** Context managers guarantee cleanup (closing files/connections) even if an exception occurs, via
`__enter__`/`__exit__` or `contextlib.contextmanager`. Example: a custom context manager to manage a
BigQuery client session, a temp GCS staging path that gets cleaned up after the block, or wrapping a
Spark session so `spark.stop()` always runs.

**Q6: `*args` vs `**kwargs`, and real usage in pipeline configs.**

**Answer:** `*args` collects extra positional arguments as a tuple; `**kwargs` collects extra keyword arguments as
a dict. Used heavily in config-driven ETL frameworks where a generic `run_job(**config)` function accepts
a variable set of job parameters (source table, target table, partition column, filters) loaded from
YAML/JSON, or when wrapping library functions (e.g., a retry decorator needs to forward arbitrary
args/kwargs to the wrapped function).

**Q7: How do you handle structured configuration and secrets in a Python ETL codebase?**

**Answer:** Use layered config: defaults in code/YAML, environment-specific overrides (dev/stage/prod), environment
variables for anything environment-dependent, and Secret Manager (GCP Secret Manager) for credentials —
never hard-code or commit secrets. Libraries like `pydantic`/`pydantic-settings` or `dataclasses` give
typed, validated config objects instead of raw dicts.

**Q8: Explain Python's memory management / garbage collection briefly, and why it matters for large
in-memory transforms.**

**Answer:** CPython uses reference counting plus a generational garbage collector for cyclic references. For large
pandas/Python transforms, you need to be conscious of object copies (e.g., chained `.filter().assign()`
calls creating intermediate DataFrames), explicitly `del` large objects or use `gc.collect()` in
long-running batch jobs, and prefer in-place/vectorized operations or chunked processing to avoid memory
spikes that trigger OOM kills in Cloud Run/Cloud Functions/Dataproc workers.

**Q9: Write a function to flatten a nested JSON/dict (common in ingestion from APIs into BigQuery).**
```python
def flatten(d, parent_key="", sep="_"):
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten(v, new_key, sep))
        elif isinstance(v, list):
            items[new_key] = v  # keep as repeated field for BigQuery, or json.dumps it
        else:
            items[new_key] = v
    return items
```
Discuss: BigQuery natively supports nested/repeated (RECORD) fields, so sometimes you *don't* flatten and
instead load JSON directly with an explicit schema — flattening is a design choice based on query patterns.
See [../bigquery/guide](../bigquery/guide.md) Q4 for the BigQuery-side half of this decision.

**Q10: How do you unit test a Python ETL transformation function?**

**Answer:** Keep transformation logic as pure functions decoupled from I/O (no Spark session/BigQuery client inside
the function — pass DataFrames/dicts in, get results out). Use `pytest` with fixtures for sample
input/expected-output pairs, `pytest.mark.parametrize` for edge cases (nulls, empty input, duplicate keys),
and mock external clients (`unittest.mock`, `pytest-mock`) for anything hitting GCS/BigQuery/APIs.
