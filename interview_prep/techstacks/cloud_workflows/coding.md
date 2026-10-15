# Cloud Workflows Coding Questions — Round 2 Drills

## Interview Guide
Graded on correct YAML step structure: conditionals, OIDC auth to downstream services, and
retry/error-handling blocks.

---

### Q1. Cloud Workflows YAML calling two Cloud Run services conditionally
```yaml
main:
  steps:
    - check_file:
        call: http.get
        args:
          url: https://file-checker-abc.a.run.app/check
        result: check_result
    - decide:
        switch:
          - condition: ${check_result.body.valid}
            next: process_file
          - condition: true
            next: alert_invalid
    - process_file:
        call: http.post
        args:
          url: https://processor-xyz.a.run.app/process
          auth: {type: OIDC}
        next: end
    - alert_invalid:
        call: http.post
        args:
          url: https://alert-service-def.a.run.app/notify
        next: end
```
**Talk through:** `auth: {type: OIDC}` is how Workflows authenticates to a Cloud Run service securely
(service-to-service identity token) instead of an API key — reuse this point from
[../cloud_workflows/guide](../cloud_workflows/guide.md) Q4.

---

### Q2. Retry policy and error handling block
```yaml
main:
  steps:
    - call_flaky_api:
        try:
          call: http.get
          args:
            url: https://flaky-service.a.run.app/data
          result: api_result
        retry:
          predicate: ${http.default_retry_predicate}
          max_retries: 3
          backoff:
            initial_delay: 1
            max_delay: 10
            multiplier: 2
        except:
          as: e
          steps:
            - log_error:
                call: sys.log
                args:
                  text: ${"API call failed: " + e.message}
            - route_to_dead_letter:
                call: http.post
                args:
                  url: https://dead-letter-handler.a.run.app/notify
                  body: {error: ${e.message}}
```
**Talk through:** the `try`/`retry`/`except` structure mirrors the dead-letter pattern used throughout this
stack (Beam side outputs, Pub/Sub dead-letter topics) — route permanently-failing steps somewhere
observable instead of letting the whole workflow execution fail silently.
