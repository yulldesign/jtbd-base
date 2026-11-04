# JTBD knowledge base schema

Canonical model used by every skill, for both backends. Change it here first, then in the backend (Notion databases or local templates), then in `reference/rules.md` if property names change.

## Entities

| Entity | ID prefix | Purpose |
|---|---|---|
| Job Performer | JP | Who executes the job |
| Job | JOB | Main job, job step, sub-job, emotional, social or related job |
| Outcome | OUT | Desired outcome measuring a job or step |
| Alternative | ALT | How the job gets done today |
| Evidence | EV | Quote, survey, observation backing any entry |

Shared options:

- Status: Hypothesis, Supported, Validated, Deprecated
- Job Type: Main job, Job step, Sub-job, Emotional job, Social job, Related job
- Outcome Direction: Minimize, Increase. Metric: Time, Likelihood, Effort, Number, Cost, Risk
- Alternative Type: Competitor, Adjacent tool, Generic AI, Workaround, Manual work, Outsourcing, Do nothing
- Evidence Type: Interview, Verbatim, Survey, Observation, Analytics, Desk research, Support ticket
- Force (forces of progress, on Alternatives and Evidence): Push, Pull, Anxiety, Habit

## Notion backend

Create in this order (relations need the target data source ID). Replace `<PERFORMERS_DS>` etc. with the `collection://` IDs returned by each creation, without the `collection://` prefix. Add the first project name as the Project option (e.g. `'Acme':purple`); more options can be added later. Unique ID prefixes need at least 2 characters.

1. **Job Performers**

```sql
CREATE TABLE ("Name" TITLE, "ID" UNIQUE_ID PREFIX 'JP', "Project" SELECT('<PROJECT>':purple), "Could be" RICH_TEXT, "Aspirations" RICH_TEXT, "Context" RICH_TEXT, "Status" SELECT('Hypothesis':yellow, 'Supported':blue, 'Validated':green, 'Deprecated':gray))
```

2. **Jobs**, then add the self-relation with a second call

```sql
CREATE TABLE ("Statement" TITLE, "ID" UNIQUE_ID PREFIX 'JOB', "Project" SELECT('<PROJECT>':purple), "Type" SELECT('Main job':purple, 'Job step':blue, 'Sub-job':default, 'Emotional job':pink, 'Social job':orange, 'Related job':gray), "Performer" RELATION('<PERFORMERS_DS>', DUAL 'Jobs'), "Step order" NUMBER, "Status" SELECT('Hypothesis':yellow, 'Supported':blue, 'Validated':green, 'Deprecated':gray), "Importance" NUMBER, "Satisfaction" NUMBER, "Opportunity" FORMULA('if(empty(prop("Importance")) or empty(prop("Satisfaction")), toNumber(""), round((prop("Importance") + max(prop("Importance") - prop("Satisfaction"), 0)) * 10) / 10)'), "Quadrant" FORMULA('if(empty(prop("Importance")) or empty(prop("Satisfaction")), "", if(prop("Importance") < 4, "Not worth going after", if(prop("Satisfaction") < 4, "Opportunity", "Competitive market")))'), "Notes" RICH_TEXT)
```

```sql
ADD COLUMN "Parent job" RELATION('<JOBS_DS>', DUAL 'Child jobs' 'child_jobs')
```

3. **Outcomes**

```sql
CREATE TABLE ("Statement" TITLE, "ID" UNIQUE_ID PREFIX 'OUT', "Project" SELECT('<PROJECT>':purple), "Job" RELATION('<JOBS_DS>', DUAL 'Outcomes'), "Direction" SELECT('Minimize':blue, 'Increase':green), "Metric" SELECT('Time':default, 'Likelihood':default, 'Effort':default, 'Number':default, 'Cost':default, 'Risk':default), "Status" SELECT('Hypothesis':yellow, 'Supported':blue, 'Validated':green, 'Deprecated':gray), "Importance" NUMBER, "Satisfaction" NUMBER, "Satisfaction post-launch" NUMBER, "Opportunity" FORMULA('if(empty(prop("Importance")) or empty(prop("Satisfaction")), toNumber(""), round((prop("Importance") + max(prop("Importance") - prop("Satisfaction"), 0)) * 10) / 10)'), "Quadrant" FORMULA('if(empty(prop("Importance")) or empty(prop("Satisfaction")), "", if(prop("Importance") < 4, "Not worth going after", if(prop("Satisfaction") < 4, "Opportunity", "Competitive market")))'), "Satisfaction delta" FORMULA('if(empty(prop("Satisfaction")) or empty(prop("Satisfaction post-launch")), toNumber(""), round((prop("Satisfaction post-launch") - prop("Satisfaction")) * 10) / 10)'), "Notes" RICH_TEXT)
```

4. **Alternatives**

```sql
CREATE TABLE ("Name" TITLE, "ID" UNIQUE_ID PREFIX 'ALT', "Project" SELECT('<PROJECT>':purple), "Type" SELECT('Competitor':red, 'Adjacent tool':orange, 'Generic AI':purple, 'Workaround':yellow, 'Manual work':brown, 'Outsourcing':blue, 'Do nothing':gray), "Jobs" RELATION('<JOBS_DS>', DUAL 'Alternatives'), "Why they hire it" RICH_TEXT, "Where it falls short" RICH_TEXT, "Push" RICH_TEXT, "Pull" RICH_TEXT, "Anxiety" RICH_TEXT, "Habit" RICH_TEXT, "Status" SELECT('Hypothesis':yellow, 'Supported':blue, 'Validated':green, 'Deprecated':gray), "URL" URL)
```

5. **Evidence**

```sql
CREATE TABLE ("Title" TITLE, "ID" UNIQUE_ID PREFIX 'EV', "Project" SELECT('<PROJECT>':purple), "Type" SELECT('Interview':blue, 'Verbatim':green, 'Survey':purple, 'Observation':orange, 'Analytics':yellow, 'Desk research':gray, 'Support ticket':red), "Date" DATE, "Participant" RICH_TEXT, "Quote" RICH_TEXT, "Force" SELECT('Push':red, 'Pull':green, 'Anxiety':orange, 'Habit':gray), "Source" URL, "Performers" RELATION('<PERFORMERS_DS>', DUAL 'Evidence'), "Jobs" RELATION('<JOBS_DS>', DUAL 'Evidence'), "Outcomes" RELATION('<OUTCOMES_DS>', DUAL 'Evidence'), "Alternatives" RELATION('<ALTERNATIVES_DS>', DUAL 'Evidence'))
```

Views (create-view): Jobs board "Job map" `GROUP BY "Type"; SORT BY "Step order" ASC`; Outcomes table "Opportunity ranking" `SORT BY "Opportunity" DESC`.

### Upgrading an existing base

Bases created before a schema change lack the new properties. Apply the statements below to the matching data source (one `ADD COLUMN` per call if the tool rejects several), skipping properties that already exist.

- Forces of progress (2026-11):
  - Alternatives: `ADD COLUMN "Push" RICH_TEXT`, `ADD COLUMN "Pull" RICH_TEXT`, `ADD COLUMN "Anxiety" RICH_TEXT`, `ADD COLUMN "Habit" RICH_TEXT`
  - Evidence: `ADD COLUMN "Force" SELECT('Push':red, 'Pull':green, 'Anxiety':orange, 'Habit':gray)`

API notes: formula values are not returned by the Notion API (opaque references), so skills recompute scores. Relations are written as JSON arrays of page IDs.

## Local backend

Markdown files with YAML frontmatter in the vault folder set in `jtbd.config.yaml` (default `jtbd-base/`). Obsidian compatible. One file per entry, **file name = ID** (`JOB-012.md`) so links never break when a statement is reworded. Links use `[[ID]]`. The statement goes in `aliases` so Obsidian shows it in link suggestions.

```
jtbd-base/
├── performers/   JP-001.md
├── jobs/         JOB-001.md
├── outcomes/     OUT-001.md
├── alternatives/ ALT-001.md
├── evidence/     EV-001.md
├── Graph/        index.md (generated, links every entry)
└── concepts.md
```

Only the child-to-parent direction is stored (a step stores its `parent`, an outcome its `job`). Reverse links (children, outcomes of a job, evidence of an entry) are derived by search or by the plugin script `scripts/jtbd_local.py`. IDs: next number = highest existing + 1, 3 digits (`the plugin script `scripts/jtbd_local.py` next-id JOB`).

`Graph/index.md` is generated by `scripts/jtbd_local.py graph`: one note linking every entry, grouped by project, performer, job, step and outcome, so the Obsidian graph view shows the whole base. Never edit it by hand, it is overwritten on each run.

Frontmatter values: plain scalars, quoted strings, or inline lists `["[[JOB-001]]", "[[JOB-004]]"]`. Leave unknown numbers empty.

### Performer `performers/JP-001.md`

```markdown
---
id: JP-001
name: "UX researcher"
project: Acme
status: Hypothesis
could_be: "UX researcher, research ops"
aliases: ["UX researcher"]
---
# UX researcher

## Aspirations
...

## Context
...
```

### Job `jobs/JOB-001.md`

```markdown
---
id: JOB-001
statement: "Turn customer interviews into insights the product team can act on"
type: Main job
project: Acme
status: Hypothesis
performer: "[[JP-001]]"
parent: ""
step_order:
importance:
satisfaction:
aliases: ["Turn customer interviews into insights the product team can act on"]
---
# Turn customer interviews into insights the product team can act on

## Notes
```

### Outcome `outcomes/OUT-001.md`

```markdown
---
id: OUT-001
statement: "Minimize the time it takes to code a one-hour interview"
project: Acme
status: Hypothesis
job: "[[JOB-004]]"
direction: Minimize
metric: Time
importance:
satisfaction:
satisfaction_post:
aliases: ["Minimize the time it takes to code a one-hour interview"]
---
# Minimize the time it takes to code a one-hour interview
```

### Alternative `alternatives/ALT-001.md`

```markdown
---
id: ALT-001
name: "Spreadsheet with manual tagging"
project: Acme
status: Hypothesis
type: Workaround
jobs: ["[[JOB-001]]"]
url: ""
aliases: ["Spreadsheet with manual tagging"]
---
# Spreadsheet with manual tagging

## Why they hire it

## Where it falls short

## Push

## Pull

## Anxiety

## Habit
```

Forces are body sections (free text, one short sentence or a few bullets each). Leave a section empty rather than guessing.

### Evidence `evidence/EV-001.md`

```markdown
---
id: EV-001
title: "P03 on re-tagging after each study"
project: Acme
type: Interview
date: 2026-11-01
participant: P03
force:                     # Push | Pull | Anxiety | Habit, when the quote illustrates one
source: "inbox/interview-p03.md"
performers: ["[[JP-001]]"]
jobs: ["[[JOB-004]]"]
outcomes: ["[[OUT-002]]"]
alternatives: []
---
> Verbatim quote, anonymized.
```
