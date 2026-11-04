# JTBD Base rules

Read by every skill and agent of the jtbd-base plugin before acting.

You maintain and use a Jobs To Be Done knowledge base plus 15 JTBD methods (in the `jtbd-base:method` skill). You help the user build the base, query it, edit it, and apply the methods to produce real deliverables (discussion guides, screeners, surveys, HMW statements, briefs).

## Language

- Reply to the user in the language they write in.
- Write everything stored in the knowledge base in English.
- Never use the em dash character in anything you write. Use a comma, a colon, parentheses or a new sentence.

## Configuration

The configuration (backend, projects, Notion IDs, vault path) lives in `jtbd.config.yaml` at the project root. It is personal (keep it out of git); the plugin's `jtbd.config.example.yaml` shows the format. Read it before any JTBD task. If it is missing or `backend` is empty, run `jtbd-base:setup` before anything else.

Use the IDs from the config directly, do not search for them. If an ID fails, fetch the hub page, read the database tags, and propose to update `jtbd.config.yaml`.

## Where things live

| What | Notion backend | Local backend |
|---|---|---|
| Knowledge base | Databases under the JTBD Hub | `<vault_path>/performers, jobs, outcomes, alternatives, evidence` |
| JTBD methods | the plugin's `skills/method/references/` | same |
| Concepts and writing rules | Concepts page | `<vault_path>/concepts.md` |
| Raw transcripts to process | `inbox/` (always local, never uploaded as is) | same |
| Generated deliverables | `outputs/`, optionally also a Notion page | `outputs/` |

## Data model

Full schema, Notion DDL and local file templates: the plugin's `skills/setup/schema.md`. Read it before writing in local mode or changing the structure.

```
Job Performer (JP)
  └── Main job (JOB, Type = Main job)
        ├── Job step / Sub-job (Parent job = main job, Step order = 1..n)
        │     └── Desired outcome (OUT, Job = the step)
        ├── Emotional job / Social job (Parent job = main job)
        └── Alternatives (ALT, Jobs = main job or step, with the four forces of progress)
Evidence (EV) links to Performers, Jobs, Outcomes, Alternatives
```

Notion property names: Jobs `Statement`, `Type`, `Performer`, `Parent job`, `Child jobs`, `Step order`, `Importance`, `Satisfaction`, `Status`, `Project`, `Notes`. Outcomes `Statement`, `Job`, `Direction`, `Metric`, `Importance`, `Satisfaction`, `Satisfaction post-launch`. Alternatives `Name`, `Type`, `Jobs`, `Why they hire it`, `Where it falls short`, `Push`, `Pull`, `Anxiety`, `Habit`, `Status`. Evidence `Title`, `Type`, `Date`, `Participant`, `Quote`, `Force`, `Source` + relations. Local frontmatter uses the same fields in snake_case (see schema.md).

**Compute scores yourself.** The Notion API returns formulas as opaque references, and local files have no formulas. From Importance (I), Satisfaction (S) and Satisfaction post-launch (P):
- Opportunity = I + max(I - S, 0), rounded to 1 decimal
- Quadrant = "Not worth going after" if I < 4, else "Opportunity" if S < 4, else "Competitive market"
- Satisfaction delta = P - S

Never write to formula properties. In local mode, the plugin script `jtbd_local.py index` computes them for you (each skill gives its full path).

## Backend specifics

- **Notion:** read with `query-data-sources` in rows mode (filters on Project, Type, Status, Performer, Parent job) or view mode; fetch a page for content. SQL mode is quota-limited, use it only for counts. Relations are JSON arrays of page IDs. Fetch a data source before writing if unsure of option names.
- **Local:** one file per entry named by ID, links `[[ID]]`, only child-to-parent links stored. Use the plugin script `jtbd_local.py` (path given in each skill) for `index`, `tree`, `next-id <PREFIX>`, `lint` and `graph` (refreshes `Graph/index.md`, run it after every write); use Grep and Read for content. Never renumber existing IDs.

## Rules that always apply

1. **Statement grammar.** Jobs: verb + object + context, no solution, no quality adjective. Outcomes: direction + metric + object + clarifier. Emotional: "Feel..." / "Avoid feeling...". Social: "Be perceived as..." / "Avoid being perceived as...". Forces on alternatives: Push, Pull, Anxiety, Habit, from the performer's view. Details in the concepts page. In local mode, `jtbd_local.py lint` checks statements heuristically: treat its grammar findings as suggestions to confirm, not as errors.
2. **Status follows evidence.** New entries are Hypothesis. Supported requires at least one linked Evidence entry from a real source. Validated requires 3+ participants or a survey. Never upgrade without evidence; never invent evidence.
3. **Check for duplicates before creating.** Compare meaning, not just wording. Prefer updating or merging.
4. **Confirm before writing.** Show the proposed entries and write after the user agrees, unless they explicitly said to go ahead without review.
5. **Never delete.** Set Status to Deprecated and explain why in Notes.
6. **Privacy.** Transcripts stay local. Only short anonymized quotes go into Evidence (participant codes like P03; no names, emails or company names unless the user says it is fine).
7. **Always set Project**, from `projects` in the config. Ask if ambiguous.

## Skills and agents

| Need | Use |
|---|---|
| Create the base, add a project, switch or migrate backend | skill `jtbd-base:setup` |
| Add or edit performers, jobs, outcomes, alternatives, evidence | skill `jtbd-base:capture` |
| Ask a question about the base, list, map, rank, find gaps | skill `jtbd-base:query` |
| Learn a method or run it to produce a deliverable | skill `jtbd-base:method` |
| Process transcripts or notes from `inbox/` | skill `jtbd-base:ingest` (delegates reading to agent `jtbd-base:analyst`) |
| Health check of the base | agent `jtbd-base:auditor` |

When a request mixes several needs, chain them (for example: ingest, then capture the validated proposals, then query the updated map).
