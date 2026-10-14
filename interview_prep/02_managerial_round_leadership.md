# Round 4: Managerial & Leadership Interview — Guide & Q&A

## Interview Guide
This round is run by the **hiring manager** (or a senior manager from an adjacent team, for cross-calibration),
usually 45-60 minutes, almost entirely behavioral. Unlike R1-R3, there's no "right answer" to look up — the
hiring manager is pattern-matching your stories against the competency rubric in
[04_recruiter_scorecard_and_leveling_rubric.md](04_recruiter_scorecard_and_leveling_rubric.md), specifically:
**ownership, scope, handling ambiguity, conflict/influence, mentorship, and delivering measurable results.**

Most high-bar tech companies use some version of a published leadership-competency framework to structure
these questions (for example, Amazon's publicly documented Leadership Principles — Ownership, Dive Deep,
Deliver Results, Earn Trust, Bias for Action, Think Big, Disagree & Commit, Hire and Develop the Best; or
Google's "Googleyness & Leadership" axis). You don't need to know a specific company's exact list by name —
you need stories that credibly demonstrate the *underlying behaviors*, because every company's framework
maps to roughly the same handful of things: **did you own something hard, did you make a good call with
incomplete information, did you make other people better, and did you deliver a result anyone would care
about.**

### The "Satisfying Answer" Formula (use this for every single behavioral question)
A hiring manager interviews 3-5 candidates a week. The ones who get "Strong Hire" are rarely the ones with
the most impressive project — they're the ones whose answers are **easy to listen to**. Compress every
story into this spoken structure and say it out loud, timed, until it's ~45-60 seconds:

> **"[1 sentence Situation] → [1 sentence: the specific decision/action *I* took] → [1 sentence: the
> quantified Result] → (pause)."**

Then stop talking. Let the interviewer ask "tell me more about X" if they want depth — this is a feature,
not a gap. Rambling through every detail unprompted is the #1 reason technically strong candidates score
lower than expected in this round.

### Story-to-Competency Map
Prepare 6-8 stories and know which competencies each one can answer, so you're not inventing a new story
live for every question:

| Story | Competencies it covers |
|---|---|
| Production incident (month-end Dataproc/Airflow failure) | Ownership, Dive Deep, Deliver Results, handling pressure |
| BigQuery cost optimization | Ownership, Think Big, Business acumen |
| Disagreement on migration approach (PySpark vs. rewrite) | Earn Trust, Disagree & Commit, Influence without authority |
| Mentoring + DAG-authoring guide | Hire & Develop the Best, multiplying others |
| Pushing back on an unsafe deadline | Ownership, Earn Trust, Customer Obsession |
| Informatica → GCP migration | Think Big, Deliver Results, Dive Deep, ambiguity |
| A project that failed / wrong approach | Learn and be curious, self-awareness |
| Prioritizing competing tickets | Bias for Action, judgment under ambiguity |

---

## Q&A (headline version first, expandable detail below each)

**Q1: Tell me about a time you resolved a production incident.**
> **Headline (45 sec):** "A nightly Airflow DAG feeding exec dashboards started failing intermittently at
> month-end. I found the root cause was a Dataproc job timing out under month-end's larger data volume —
> I triggered an immediate rerun with a bigger cluster to hit the SLA, then fixed the autoscaling policy
> permanently so it never recurred. No repeat failures in the following six month-ends."
*If probed further:* explain how you diagnosed it (YARN metrics vs. a code bug), the specific config change,
and that you wrote a short postmortem shared with the team.

**Q2: Tell me about a time you optimized cost on a data platform.**
> **Headline:** "BigQuery costs were growing faster than data volume justified. I found several dashboards
> were doing full-table scans from missing partition filters, added partitioning and clustering to the
> worst offenders, and converted a few repeated aggregations into materialized views. That cut monthly
> BigQuery spend by roughly a third with zero change to dashboard latency."
*If probed further:* mention `INFORMATION_SCHEMA.JOBS`/billing export analysis, `require_partition_filter`,
and the cost-attribution dashboard you built afterward so the issue wouldn't silently recur.

**Q3: Tell me about a disagreement with a teammate or another team about technical direction.**
> **Headline:** "A teammate wanted to hand-rewrite all PowerCenter mappings as plain Python scripts. I
> thought that would create new maintenance debt at our data volumes. Instead of just disagreeing, I
> prototyped the same mapping both ways and showed the performance/maintainability gap, then proposed a
> decision framework — SQL-expressible logic goes to BigQuery, complex procedural logic goes to PySpark.
> The team adopted it, and it made every later migration decision faster."
*If probed further:* emphasize you brought data/a prototype rather than opinion, and that the relationship
stayed collaborative afterward — this is the "Earn Trust"/"Disagree & Commit" signal.

**Q4: Tell me about a time you mentored someone or improved team practices.**
> **Headline:** "New hires were slow to ship their first Airflow DAGs, and a few had idempotency bugs that
> duplicated data on retry. I wrote a short DAG-authoring guide with a reusable template and added a CI
> lint check that caught the common mistakes automatically, then paired directly with two new hires. Time
> to first production DAG dropped, and that class of bug stopped recurring entirely."
*If probed further:* note this scaled beyond 1:1 help — it became a standing team asset, which is the
"multiplying effect" signal that separates Senior from Mid-level.

**Q5: Tell me about a time you pushed back on a deadline or requirement.**
> **Headline:** "A stakeholder wanted a new BigQuery dashboard live on a timeline that meant skipping
> validation on a migrated pipeline. I proposed shipping it clearly labeled 'beta' with a fast-follow
> validated release instead of either blocking the launch or shipping silently-unvalidated numbers. They
> agreed — and the beta period caught two real data discrepancies before we removed the label."
*If probed further:* explain you framed the risk in business terms ("wrong exec numbers"), not process
purity — this is what makes pushback land well instead of sounding obstructive.

**Q6: Describe the most complex migration or modernization project you've worked on.**
> **Headline:** "I led the migration of [N] PowerCenter mappings to GCP. I triaged them by complexity —
> SQL-expressible logic became BigQuery SQL, complex procedural logic became PySpark on Dataproc — then
> ran old and new pipelines in parallel, reconciling output with automated row-count and checksum diffing
> before cutover. We cut ETL runtime from hours to under an hour and retired a chunk of PowerCenter
> licensing cost."
*If probed further:* the reconciliation/validation approach is usually the most impressive part to a
hiring manager — it shows production-mindedness, not just "I can write a Spark job." See
[techstacks/informatica_cloud/guide.md](techstacks/informatica_cloud/guide.md) Q5-Q10 for the full
technical narrative to pull detail from.

**Q7: Tell me about a time you had to make a decision with incomplete information.**
> **Headline:** "Midway through a migration, we discovered the legacy mapping's business logic wasn't
> fully documented anywhere. Rather than wait on an SME who was unavailable for weeks, I reverse-engineered
> the logic from sample input/output pairs and existing reports, documented my assumptions explicitly, and
> got a lightweight sign-off from the business team before building on top of it. That let us stay on
> schedule without guessing silently."
*If probed further:* the key signal is *documenting assumptions and getting lightweight validation*, not
just barreling ahead on a guess.

**Q8: Tell me about a time you influenced an outcome without having direct authority.**
> **Headline:** "I believed our orchestration layer needed a standard DAG template before we scaled past
> a handful of pipelines, but I didn't own the platform team's roadmap. I built a working prototype on my
> own pipeline, measured the before/after in code review time and bug rate, and presented that data at a
> team sync. The platform team adopted it as the org standard the following quarter."
*If probed further:* emphasize evidence-based influence (prototype + metrics) over asking for authority.

**Q9: Tell me about a time a project failed or didn't go as planned.**
> **Headline:** "Early in a migration, I translated a PowerCenter mapping almost literally into row-by-row
> Python, assuming that would be 'safe.' At real data volume it was far too slow. I redesigned it as a
> distributed PySpark job using broadcast joins, and from then on I always benchmarked a small prototype
> before committing to a translation approach on the rest of the migration."
*If probed further:* be genuinely honest about the miscalculation — hiring managers specifically listen for
real self-awareness here, not a disguised brag ("my biggest weakness is I work too hard").

**Q10: How do you prioritize when multiple pipelines/tickets compete for your time?**
> **Headline:** "I triage by business impact and blast radius — what's broken and who's blocked, versus
> what's merely overdue. An on-call page beats a backlog item even if the backlog item is more important
> long-term, but I communicate that trade-off to stakeholders rather than silently deprioritizing their
> work."
*If probed further:* mention batching small similar tasks (code review, minor fixes) to protect deep-work
time for design/migration work — shows time-management maturity.

**Q11: How do you measure success for a pipeline or project you own?**
> **Headline:** "Beyond 'it runs' — freshness/SLA adherence, data quality (did downstream consumers ever
> catch a number we should have caught first), cost per unit of data processed, and whether stakeholders
> trust the output enough to act on it without double-checking elsewhere."
*If probed further:* give one concrete metric you personally tracked and moved.

**Q12: Tell me about a time you received tough feedback. How did you respond?**
> **Headline:** "A peer told me my PR reviews were too focused on style nitpicks and not enough on design,
> which was slowing the team down without adding real value. I took it seriously, changed my review
> checklist to focus on correctness/design first, and asked that same peer to call it out again if I
> slipped back into it."
*If probed further:* the signal here is *behavior change*, not just "I listened."

**Q13: Where do you see yourself in 3-5 years?**
> **Headline:** "Growing from owning individual pipelines to owning platform-level decisions — the kind of
> build-vs-buy and architecture calls a staff engineer makes — and continuing to grow others along the way,
> which is already something I enjoy doing."
*If probed further:* tie it to something concrete you're already doing in that direction (the mentoring
story, the migration framework you built).

**Q14: Why are you looking to leave your current role?**
> **Headline:** "I want more exposure to early-stage architecture decisions rather than mostly execution,
> and I want to go deeper on streaming/real-time patterns than my current team's needs have required."
*Keep this forward-looking and specific — never negative about the current employer. See*
[03_hr_final_round.md](03_hr_final_round.md) *for the fuller version of this question tailored to the HR
round.*

**Q15: What are you most proud of in your career so far?**
> **Headline:** Pick the story with the widest blast radius of impact — ideally one where something you
> built (a framework, a migration pattern, a mentee's growth) outlived your direct involvement in it. Tie
> it explicitly to the role you're interviewing for.

## Questions to Ask Your Hiring Manager
- "What does success look like for this role at the 6-month and 12-month mark?"
- "How does the team currently split time between new pipeline development and maintaining/operating
  existing ones?"
- "What's the team's current on-call rotation and incident load like?"
- "Where is the team in the Informatica-to-GCP (or equivalent) modernization journey, and what's blocking
  faster progress?"
- "How do you approach performance feedback and growth conversations on this team?"

