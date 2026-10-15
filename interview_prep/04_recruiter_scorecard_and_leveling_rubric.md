# The Recruiter Scorecard & Leveling Rubric
### "If I were your senior recruiter / bar-raiser, here is literally what I write down."

## 1. How Scoring Actually Works at a High-Bar Tech Company
After every round, the interviewer fills out a written scorecard **before** talking to anyone else about
the candidate (to avoid anchoring bias). It typically has: a few competency ratings, a free-text evidence
section, and one overall recommendation:
- **Strong Hire** — I'd be disappointed if we didn't make an offer; I'll personally vouch for this.
- **Hire** — Solid, meets the bar, comfortable recommending.
- **Lean Hire** — Mostly positive but a real gap; would defer to the rest of the loop.
- **Lean No Hire** — Mostly negative but not disqualifying; would defer to the rest of the loop.
- **No Hire** — Doesn't meet the bar for this level.
- **Strong No Hire** — Active concerns (red flags), would advocate against regardless of other rounds.

A single "Strong No Hire" with concrete evidence can override four "Strong Hire" scores. This is why
**consistency across all five rounds** matters more than being brilliant in one and weak in another.

## 2. The Competency Rubric
Score each dimension 1-4. "3" is the bar for a 6+ YOE Senior Data Engineer offer.

| # | Dimension | 1 — Below Bar | 2 — Developing | 3 — Meets Bar (Senior, 6 YOE) | 4 — Exceeds Bar |
|---|---|---|---|---|---|
| 1 | **Technical depth** (GCP/Spark/SQL/Airflow) | Defines terms but can't explain trade-offs | Explains trade-offs only when prompted | Volunteers trade-offs, cites real scale/numbers unprompted | Teaches the interviewer something; connects multiple services fluently |
| 2 | **Coding proficiency** | Can't complete a medium problem unaided | Completes with heavy hints, messy code | Working, reasonably clean solution in reasonable time, discusses complexity | Also discusses edge cases, tests, and how it changes at distributed scale |
| 3 | **System design judgment** | Jumps to a solution, misses major requirements | Reasonable design but can't defend trade-offs under pushback | Clarifies requirements first, presents 2+ options with trade-offs, defends choice under pushback | Proactively surfaces failure modes, cost, and security interviewer hadn't asked about |
| 4 | **Debugging / operational maturity** | Has no production-incident stories | Has stories but no systemic fix, just "we restarted it" | Clear root cause, immediate fix, and a permanent/systemic fix | Also shows a monitoring/prevention change that helped other teams, not just their own pipeline |
| 5 | **Communication clarity** | Rambles, jargon-heavy, loses the thread | Gets to the point eventually with prompting | Headline-first answers, checks in, adjusts depth to audience | Can explain the same concept simply to a non-technical exec and in depth to a peer |
| 6 | **Ownership & drive for results** | Passive voice, unclear what they personally did | "I" only appears for small tasks | Clearly owned a meaningful piece end-to-end, with quantified outcome | Owned something ambiguous/undefined and created the structure themselves |
| 7 | **Collaboration & influence** | Describes conflict as someone else's fault | Resolved conflict only by escalating to a manager | Resolved disagreement directly, with data/prototype, preserving the relationship | Changed how the team/org works going forward (process, template, standard) |
| 8 | **Mentorship / multiplying effect** | No mentoring examples | Ad hoc help only | Deliberate mentoring/documentation/process that measurably helped others | Built something (framework, training, guild) still used after they left the project |
| 9 | **Business acumen** | Talks only about tech, never impact | Mentions impact vaguely ("it helped the business") | Ties decisions to concrete cost/revenue/SLA/trust outcomes | Proactively made a build-vs-buy or cost call that changed budget/roadmap |
| 10 | **Values / culture alignment** | Badmouths past employer/colleagues, inconsistent story | Neutral but generic answers | Specific, honest, consistent story across rounds | Energizes the interviewer; you want them on your team specifically |

**Overall bar for offer at Senior Data Engineer (6 YOE):** average of 3 across all dimensions, with
**no single dimension below 2**, and **no "Strong No Hire" red flag present** (see below — red flags are a
veto, not just a point deduction).

## 3. Red Flags (Veto Power — Independent of Technical Skill)
These push toward **Strong No Hire** even if the technical rounds were excellent:
- **Badmouthing** a former manager, team, or company — signals how they'll talk about *this* company later.
- **Can't go deep on their own resume bullet.** If their resume says "led migration of 50 ETL pipelines"
  and they can't describe one specific pipeline's actual logic/schema, that's a fabrication flag.
- **No metrics, ever** — every answer is qualitative ("it went well," "it was a big improvement") with no
  numbers even when pushed.
- **Blame-shifting** — every failure story is someone else's fault; never their own decision or mistake.
- **Inconsistent story across rounds** — scope, dates, or outcomes of the same project change noticeably
  between the technical round and the managerial round.
- **Overclaiming scope** — describing an obvious team effort ("I built the entire data platform") with no
  acknowledgment of a team, especially when the team size/timeline makes solo ownership implausible.
- **Can't simplify** — asked to explain their own project to a non-technical audience, they just repeat the
  same jargon louder.
- **No questions for the interviewer** at the end of any round — reads as low genuine interest.
- **Dismissive of trade-offs** — insists their chosen tool/approach is correct in all cases with no "it
  depends."

## 4. Green Flags (What Tips Lean Hire → Strong Hire)
- Headline-first answers that respect the interviewer's time (see
  [00_interview_guide_overview](00_interview_guide_overview.md) section 4).
- Unprompted mention of trade-offs, failure modes, cost, or security — shows the candidate thinks in
  systems, not just features.
- Quantified impact in almost every story (%, $, hours saved, scale handled).
- A genuine "here's what I'd do differently" in at least one story — self-awareness reads as maturity, not
  weakness.
- Sharp clarifying questions asked *before* diving into a system design solution.
- Visible enthusiasm about specific technical topics (not generic "I love data") — shows real engagement.
- Balanced "I/we" language: clear about their individual contribution while crediting the team accurately.
- A credible, detailed Informatica → GCP modernization story — for *this specific* stack combination, this
  is a strong differentiator most other candidates won't have.

## 5. Leveling Guide: Mid-Level vs. Senior (6 YOE) vs. Staff
Years of experience is a weak signal by itself — scope and ambiguity handled are the real levers.

| Signal | Mid-Level (IC3-ish) | **Senior (IC4-ish, 6 YOE target)** | Staff (IC5-ish) |
|---|---|---|---|
| **Scope** | Owns a feature/pipeline within clear specs | Owns a full pipeline/service end-to-end; defines the specs | Owns a platform/area spanning multiple teams |
| **Ambiguity** | Needs requirements handed to them | Resolves ambiguous requirements themselves, confirms with stakeholders | Defines the problem before anyone asks for it |
| **Technical decisions** | Follows existing patterns | Chooses and justifies the pattern/tool for new situations | Sets the pattern/standard others follow |
| **Cross-team work** | Works within their team | Coordinates across 1-2 teams for a project | Influences roadmap across many teams without authority |
| **Mentorship** | Helps peers informally | Actively mentors, reviews code/design as a standard practice | Shapes how the org hires/develops engineers |
| **Incidents** | Fixes the immediate issue | Fixes root cause + adds systemic prevention | Changes org-wide practice/tooling to prevent a class of incidents |

If a candidate's stories consistently land in the "Mid-Level" column despite 6 years of tenure, that's a
legitimate basis for a "Lean Hire"/leveling-down conversation, not a disqualifier — some candidates have
deep tool expertise but shallow scope because of how their past org was structured. Probe explicitly:
*"Who decided that approach — you, your lead, or the team together?"*

## 6. Sample Scorecard Template (use this to self-grade mock interviews)
```
Candidate: ____________________        Round: R__  Interviewer role: __________

Technical depth           [1 2 3 4]   Evidence: ________________________________
Coding proficiency        [1 2 3 4]   Evidence: ________________________________
System design judgment    [1 2 3 4]   Evidence: ________________________________
Debugging / ops maturity  [1 2 3 4]   Evidence: ________________________________
Communication clarity     [1 2 3 4]   Evidence: ________________________________
Ownership & drive         [1 2 3 4]   Evidence: ________________________________
Collaboration/influence   [1 2 3 4]   Evidence: ________________________________
Mentorship                [1 2 3 4]   Evidence: ________________________________
Business acumen           [1 2 3 4]   Evidence: ________________________________
Values/culture            [1 2 3 4]   Evidence: ________________________________

Red flags observed (if any): ________________________________________________
Green flags observed:        ________________________________________________

Overall recommendation: [ ] Strong Hire [ ] Hire [ ] Lean Hire [ ] Lean No Hire
                         [ ] No Hire    [ ] Strong No Hire
One sentence summary: _________________________________________________________
```

## 7. How to Use This File to Prepare
1. After each mock interview answer, fill in the scorecard yourself (or have a friend do it) — be honest.
2. Any dimension scoring 1-2 is your study priority, not the topic you already feel confident about.
3. Specifically audit your stories for the red flags in Section 3 — these are the easiest, cheapest fixes
   and the highest-leverage ones, since a single red flag can outweigh strong technical performance.
4. Re-read Section 5 and make sure at least 2-3 of your stories clearly land in the "Senior" column, with
   an explicit "I decided/I proposed" moment, not just "I implemented what was asked."
