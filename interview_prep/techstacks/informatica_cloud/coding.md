# Informatica Cloud (IICS) Coding Questions — Round 2 Drills

## Interview Guide
IICS is lower-code than PowerCenter's Expression Language work, so there's less pure "coding" here —
most of it is parameterization/configuration. For the shared expression-language patterns (IIF, DECODE,
Lookup, hash-based SCD2 detection), see
[../informatica_powercenter/coding](../informatica_powercenter/coding.md), which apply nearly
unchanged in IICS's Mapping Designer.

---

### Q1. IICS mapping task parameter file example
```ini
; params.prm - used by an IICS mapping task to parameterize the run
$$SOURCE_SCHEMA=RAW_SALES
$$TARGET_TABLE=proj.curated.orders
$$LOAD_DATE=2026-10-14
$$INCREMENTAL_FLAG=Y
```
**Talk through:** parameterizing the mapping task (rather than hard-coding values in the mapping) is what
lets the same mapping be reused across dev/stage/prod or across similar source tables with a config change
instead of a mapping change — mirrors the "config-driven job" pattern discussed in
[../python/guide](../python/guide.md) Q6.
