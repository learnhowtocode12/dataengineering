---
slug: /
---

# Data Engineer (6+ Years) — Interview Guide Overview
### Written from the seat of a senior technical recruiter / bar-raiser at a high-paying, FAANG-style company

Target profile: Senior Data Engineer, 6+ years experience, stack = GCP (BigQuery, Pub/Sub, Dataflow,
Dataproc, Cloud Run, Cloud Functions, GKE, Cloud Tasks, Cloud Workflows, Cloud Scheduler), PySpark,
Python, SQL, Apache Iceberg, Airflow, Looker, Informatica PowerCenter + Informatica Cloud (IICS/IDMC).

This edition of the guide is written the way a **senior recruiter / hiring committee bar-raiser** actually
thinks: not "did they define the term correctly" but "would I bet my own credibility on recommending this
hire." Every round in a real loop ends with the interviewer typing independent written feedback and a
rating (Strong Hire / Hire / Lean Hire / No Hire / Strong No Hire) before anyone compares notes. This guide
is built around earning that "Strong Hire."

## 1. How This Guide Is Organized
Each technology has a focused guide with conceptual Q&A and, where useful, a separate set of hands-on
drills. The guides are grouped by topic so you can jump directly to the technology you want to practice.

| Technology | Round | Covers |
|---|---|---|
| [Python](techstacks/python/guide.md) | R1/R2 | Core Python: GIL, generators, decorators, config/secrets |
| [PySpark](techstacks/pyspark/guide.md) | R1/R2 | Spark architecture, shuffle, skew, Catalyst/Tungsten, tuning |
| [SQL](techstacks/sql/guide.md) | R1/R2 | Dialect-agnostic SQL fundamentals — joins, ACID, indexes, execution plans |
| [GCP Fundamentals](techstacks/gcp_fundamentals/guide.md) | R2 | GCP service selection (BigQuery vs Bigtable vs Spanner etc.), IAM |
| [BigQuery](techstacks/bigquery/guide.md) | R2 | Architecture, partitioning/clustering, cost, MERGE/SCD, security |
| [Pub/Sub](techstacks/pubsub/guide.md) | R2 | Delivery guarantees, ordering keys, dead-lettering, Pub/Sub vs Kafka/Tasks |
| [Dataflow](techstacks/dataflow/guide.md) | R2 | Apache Beam model, windowing/triggers, templates, autoscaling |
| [Dataproc](techstacks/dataproc/guide.md) | R2 | Cluster management, preemptible VMs, Hadoop/Spark migration |
| [Apache Iceberg](techstacks/apache_iceberg/guide.md) | R2 | Metadata-tree architecture, ACID/time travel, BigLake integration |
| [Airflow / Cloud Composer](techstacks/airflow/guide.md) | R2 | DAG design, idempotency, sensors, Composer architecture |
| [Cloud Workflows](techstacks/cloud_workflows/guide.md) | R2 | Lightweight YAML orchestration, retries, service-to-service auth |
| [Cloud Tasks](techstacks/cloud_tasks/guide.md) | R2 | Rate-controlled task dispatch, vs Pub/Sub |
| [Cloud Scheduler](techstacks/cloud_scheduler/guide.md) | R2 | Cron triggers, relationship to Tasks/Workflows/Composer |
| [Cloud Run](techstacks/cloud_run/guide.md) | R2 | Serverless containers, Jobs, concurrency sizing, cold starts |
| [Cloud Functions](techstacks/cloud_functions/guide.md) | R2 | Event-driven triggers, Eventarc, reliability |
| [GKE](techstacks/gke/guide.md) | R2 | When data workloads need Kubernetes, Workload Identity |
| [Looker](techstacks/looker/guide.md) | R2 | LookML, PDTs, caching, row-level security |
| [Informatica PowerCenter](techstacks/informatica_powercenter/guide.md) | R2 | Legacy ETL: mappings, transformations, tuning, PDO |
| [Informatica Cloud](techstacks/informatica_cloud/guide.md) | R2/R4 | IICS architecture + the full Informatica→GCP migration narrative |
| [01_system_design_scenarios](01_system_design_scenarios.md) | R3 | End-to-end architecture / whiteboard scenarios + grading rubric |
| [02_managerial_round_leadership](02_managerial_round_leadership.md) | R4 | Ownership, leadership, conflict — concise STAR answers |
| [03_hr_final_round](03_hr_final_round.md) | R5 | Culture fit, comp negotiation, logistics, closing questions |
| [04_recruiter_scorecard_and_leveling_rubric](04_recruiter_scorecard_and_leveling_rubric.md) | All | The literal scorecard interviewers fill out, red/green flags, leveling bar |

Technologies that are naturally comparative (Dataflow vs Dataproc, Cloud Run vs Functions vs GKE, Airflow
vs the lightweight GCP-native trio, PowerCenter vs IICS) each have a focused guide with cross-references
to the alternatives. This keeps the "when do I use this vs the other option" framing close to each topic.

## 2. What I Actually Expect From a 6+ Year Data Engineer
Years of experience on a resume mean nothing by themselves — I'm listening for **scope, ownership, and
judgment**, not tool trivia. At the 6 YOE / Senior IC bar, a candidate should show all of these, unprompted,
across the loop:

| Dimension | What "meets bar" sounds like |
|---|---|
| **Trade-off reasoning** | "I chose Dataflow over Dataproc because X, even though Y would've been cheaper, because Z constraint mattered more" — never a one-sided answer. |
| **Production rigor** | Unprompted mention of idempotency, retries, dead-letter handling, monitoring/alerting, backfills — because something *has* broken on them before. |
| **Scale fluency** | Concrete numbers: data volume, cluster size, query cost, SLA — not "it was big data." |
| **Migration/legacy judgment** | Given Informatica + GCP both on the resume, a credible modernization narrative (triage, reconciliation, cutover risk) is a major differentiator — most candidates only have one side of this. |
| **Ownership language** | "I decided / I drove / I proposed" balanced with fair team credit — not passive voice ("it was decided") and not erasing the team either. |
| **Communication under pressure** | Can explain a complex pipeline to me (a non-engineer) in plain language in under 90 seconds. This is the single most common reason strong engineers get a "Lean Hire" instead of "Strong Hire." |
| **Business tie-back** | Connects technical decisions to cost, revenue, SLA, or stakeholder trust — not technology for its own sake. |

See [04_recruiter_scorecard_and_leveling_rubric](04_recruiter_scorecard_and_leveling_rubric.md) for the
full scoring rubric, calibration bar, and the exact red/green flags that move a scorecard rating up or down.

## 3. The Interview Loop: Round 1 → Round 5
Exact structure varies by company, but the competencies tested are consistent across every high-bar tech
employer. Treat this as the representative loop this guide is built around:

| Round | Name | Format | Duration | Who Interviews You | Primary Files |
|---|---|---|---|---|---|
| **R1** | Technical Screen | Live coding: Python + SQL, 1 conceptual GCP question | 45-60 min | Senior IC (peer-level) | [python](techstacks/python/guide.md), [sql](techstacks/sql/guide.md), their `coding` files |
| **R2** | Technical Deep Dive | PySpark/Dataflow/Dataproc/Airflow/Pub-Sub/Iceberg/GCP architecture + live debugging + light coding | 60 min | Senior IC / Tech Lead | The 18 technology guides listed above |
| **R3** | System Design | Whiteboard/doc: design a pipeline end-to-end, defend trade-offs under pushback | 60 min | Staff Engineer / Tech Lead | [01_system_design_scenarios](01_system_design_scenarios.md) |
| **R4** | Managerial / Leadership | Behavioral — ownership, conflict, ambiguity, mentorship, delivering results | 45-60 min | Hiring Manager | [02_managerial_round_leadership](02_managerial_round_leadership.md) |
| **R5** | HR / Recruiter Final | Culture fit, motivation, comp negotiation, logistics | 30 min | Recruiter | [03_hr_final_round](03_hr_final_round.md) |

After R1-R4, every interviewer privately submits a written scorecard (rating + evidence) before any
debrief discussion happens — this is why consistency across rounds matters more than nailing one round and
stumbling in another. A "Strong Hire" in system design cannot save a "No Hire" in the managerial round.

## 4. The Golden Rule for Every Answer: Lead, Then Expand
The single biggest, most fixable gap I see in otherwise-strong engineers is **rambling**. A 4-minute answer
to a question that needed 45 seconds reads as unclear thinking, not thoroughness. Use this structure for
*every* answer, technical or behavioral:

1. **Headline (1-2 sentences)** — the direct answer/conclusion first. ("I'd use a broadcast join here
   because the dimension table is small enough to fit in memory on every executor.")
2. **One concrete example or mechanism (2-4 sentences)** — how/why, grounded in something real you did.
3. **Stop. Check in.** — "Happy to go deeper on [X] if useful" or let the interviewer ask a follow-up.

For behavioral questions specifically, compress STAR into **~45-60 seconds**: one sentence of Situation,
one of your specific Action, one of the quantified Result. Expand only if asked. See
[02_managerial_round_leadership](02_managerial_round_leadership.md) for this pattern applied to a full
story bank.

## 5. Red Flags vs. Green Flags (Quick Reference)
Full detail with example phrases is in
[04_recruiter_scorecard_and_leveling_rubric](04_recruiter_scorecard_and_leveling_rubric.md). Quick
version:

| Green flags (push toward Strong Hire) | Red flags (push toward No Hire) |
|---|---|
| Structured, concise answers; stops and checks in | Rambling 3-5 minute answers to simple questions |
| "I decided / I drove," with fair team credit | Either hogging all credit or hiding behind "we" entirely |
| Quantifies impact (%, $, time saved, scale) | No metrics anywhere, ever |
| Volunteers trade-offs and failure modes unprompted | Only states the happy path; has to be dragged into trade-offs |
| Admits mistakes with a genuine lesson learned | Claims to have never made a significant mistake |
| Asks sharp clarifying questions before designing | Jumps straight into a solution with no clarifying questions |
| Consistent narrative across rounds | Story details shift/contradict between rounds |
| Neutral-to-constructive about past employers | Badmouths former manager/company/colleagues |

## 6. Preparation Checklist
- [ ] Be ready to draw 2-3 architecture diagrams from memory (batch ELT, streaming pipeline, CDC pipeline).
- [ ] Practice writing a PySpark job and a Beam/Dataflow pipeline from scratch without IDE autocomplete —
      see the [PySpark hands-on guide](techstacks/pyspark/coding.md) and
      [Dataflow hands-on guide](techstacks/dataflow/coding.md).
- [ ] Review BigQuery partitioning/clustering, slot/on-demand pricing, `EXPLAIN`/execution plan reading —
      see the [BigQuery guide](techstacks/bigquery/guide.md).
- [ ] Review core SQL fundamentals (joins, ACID, isolation levels, indexes, execution plans) — see
      the [SQL guide](techstacks/sql/guide.md) — these get asked even in warehouse-heavy loops.
- [ ] Be able to state Pub/Sub's delivery/ordering guarantees precisely (at-least-once, per-key ordering
      only) and explain Iceberg's snapshot/metadata model — see
      the [Pub/Sub guide](techstacks/pubsub/guide.md) and
      [Apache Iceberg guide](techstacks/apache_iceberg/guide.md).
- [ ] Rehearse 5-6 STAR stories at the 45-60 second "headline" length from
      [02_managerial_round_leadership](02_managerial_round_leadership.md) — a production incident, a
      cost win, a conflict, a mentorship story, a time you pushed back, and the Informatica→GCP migration
      (see the [Informatica Cloud guide](techstacks/informatica_cloud/guide.md) Q5-Q10).
- [ ] Prepare the 90-second "walk me through your background" answer for R5 — see
      [03_hr_final_round](03_hr_final_round.md).
- [ ] Have 3-5 thoughtful questions ready for each round (different questions for the IC rounds, the
      hiring manager, and the recruiter — see each round's file for tailored suggestions).
- [ ] Do one full mock loop (R1-R5 back to back) with a friend using the
      [04_recruiter_scorecard_and_leveling_rubric](04_recruiter_scorecard_and_leveling_rubric.md)
      scorecard template to self-grade honestly.

## 7. Quick Positioning Statement (practice saying this in under 60 seconds)
"I'm a data engineer with 6+ years building batch and streaming pipelines primarily on GCP. I design and
operate ELT/ETL workflows using BigQuery, Dataflow (Apache Beam), and Dataproc (PySpark) for large-scale
processing, orchestrated with Airflow/Cloud Composer and lighter-weight GCP-native orchestration (Cloud
Workflows, Cloud Tasks, Cloud Scheduler) for event-driven and scheduled jobs. I've built serverless
services on Cloud Run and Cloud Functions, and deployed containerized processing on GKE when workloads
needed more control. I also have hands-on experience modernizing legacy Informatica PowerCenter mappings
to Informatica Cloud (IICS) and ultimately to cloud-native GCP pipelines, and I build/maintain Looker
dashboards and LookML models so the pipelines I build are consumable by business stakeholders."
