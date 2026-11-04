# JTBD Base

A Jobs To Be Done knowledge base for Claude Code. It stores who you serve (job performers), the jobs they are trying to get done, the outcomes they judge success by, the alternatives they use today with the forces that keep them there, and the evidence behind every statement. It also ships 15 JTBD methods that Claude can explain or run on your data: screeners, interview guides, competition maps, opportunity surveys, How Might We questions, design briefs, post-launch measurement.

What makes it different from a method skill: the base grows with your research. Every entry starts as a **Hypothesis**, becomes **Supported** once real evidence is linked and **Validated** with 3+ participants or a survey. Claude enforces the statement grammar, deduplicates, and never invents evidence.

The base lives in **Notion** (shareable) or in a **local Markdown vault** (private, Obsidian friendly). Everything works the same with both.

## Install

In Claude Code:

```
/plugin marketplace add yulldesign/jtbd-base
/plugin install jtbd-base@jtbd-base
```

Requirements:
- Notion backend: the Notion MCP server connected to Claude Code.
- Local backend: Python 3.8+ (standard library only).

## Quick start

1. Create or open the folder where your JTBD work will live (your project). Open Claude Code there.
2. Run `/jtbd-base:setup`. It asks a few questions (Notion or local, project name, where to create it, empty or with starter hypotheses), builds the base and writes `jtbd.config.yaml` in your project.
3. Start working:
   - "Show me the job map of the UX researcher"
   - "Add an outcome: researchers waste time re-tagging old studies"
   - "Prepare the interview guide for the PM performer"
   - "Process the interview in inbox/"
   - "Audit the base"

## Commands

Plain sentences work: Claude picks the right skill from its description. Commands force a skill; add your request after the name.

| Command | What it does | Example |
|---|---|---|
| `/jtbd-base:setup` | Create the base, add a project, switch backend, upgrade the schema | `/jtbd-base:setup add project Atlas` |
| `/jtbd-base:capture` | Add, edit, link or deprecate entries | `/jtbd-base:capture outcome: researchers waste time re-tagging old studies` |
| `/jtbd-base:query` | Read-only questions, maps, rankings, gaps, forces | `/jtbd-base:query top 10 underserved outcomes for Acme` |
| `/jtbd-base:method` | Explain, recommend or run one of the 15 methods | `/jtbd-base:method 5 interview guide for the PM performer` |
| `/jtbd-base:ingest` | Turn files in `inbox/` into JTBD proposals | `/jtbd-base:ingest interview-03.md` |

Two agents run in their own context so heavy reading does not clutter your session. Skills call them for you, or ask by name (`@agent-jtbd-base:auditor`, or "run the auditor on Acme"):

| Agent | Role |
|---|---|
| `jtbd-base:analyst` | Reads one transcript, maps it through the JTBD lens, returns matches and new proposals (jobs, steps, outcomes, forces) with anonymized quotes. Read-only. |
| `jtbd-base:auditor` | Checks grammar, duplicates, hierarchy, outcome coverage, forces, status versus evidence, privacy. Returns a prioritized fix list. Read-only. |

Nothing is written to the base without your confirmation, and nothing is ever deleted (entries are set to Deprecated).

## Your project folder

The plugin holds no data. Everything personal lives in the project where you run Claude Code:

```
your-project/
├── jtbd.config.yaml   Backend, projects, Notion IDs (created by setup, keep it out of git)
├── inbox/             Transcripts, notes, survey CSVs to process (stay local)
├── outputs/           Generated deliverables
└── jtbd-base/         Local backend only: one Markdown file per entry
```

If the project is a git repository, add `jtbd.config.yaml`, `inbox/`, `outputs/` and `jtbd-base/` to its `.gitignore` unless you mean to share them.

## Data model

```
Job Performer ── Main job ──┬── Job steps (ordered) ── Desired outcomes
                            ├── Emotional job / Social job
                            └── Alternatives (real competition, forces of progress)
Evidence links to any of them
```

- **Status:** Hypothesis (default), Supported (1+ real evidence), Validated (3+ participants or a survey), Deprecated.
- **Scores:** importance and satisfaction on a 1 to 7 scale. Opportunity = I + max(I - S, 0). Quadrant follows Dan Olsen's map.
- **Forces of progress** on each alternative: Push, Pull, Anxiety, Habit. Evidence can be tagged with the force it illustrates.
- Statement grammar and definitions: `skills/setup/seed/concepts.md`, installed as a page in your base.

## Notion or local?

| | Notion | Local |
|---|---|---|
| Sharing and collaboration | Share the hub page | Through git or file sync |
| Privacy | Data hosted by Notion | Everything stays on your machine |
| Offline | No | Yes |
| Browsing | Notion views (job map, opportunity ranking) | Obsidian, any editor, `jtbd_local.py tree` |

You can switch at any time: "Migrate the base to local" (or to Notion). Setup copies everything and keeps the old data until you confirm.

## Working locally

Each entry is a Markdown file named by its ID (`JOB-012.md`) with YAML frontmatter, links are `[[ID]]`: open `jtbd-base/` in Obsidian to navigate, and `Graph/index.md` for the graph view. The helper script, used by the skills, also runs on its own from your project folder:

```bash
S=~/.claude/plugins/cache/jtbd-base/jtbd-base/<version>/scripts/jtbd_local.py   # or your clone
python3 $S index --project Acme       # all entries with computed scores
python3 $S tree --project Acme        # performer, jobs, steps, outcomes
python3 $S next-id OUT                # next free ID
python3 $S lint                       # broken links, status without evidence, statement grammar, missing forces
python3 $S lint --no-grammar          # structure only
python3 $S graph                      # rewrite Graph/index.md, the hub note for the Obsidian graph
```

Add `--root <project folder>` to run it from anywhere.

## Notion IDs

All Notion references live in `jtbd.config.yaml`; skills never hard-code IDs. To point to another hub, ask "Point the base to this hub: <Notion URL>". To start a new base elsewhere, run `/jtbd-base:setup` again.

## Customizing

Fork the repo, edit, then load your fork (see Development).

- **Methods:** one file per method in `skills/method/references/`, plus the index table in `skills/method/SKILL.md`. Methods 9, 10, 13 and 15 are drafts whose steps still need validating in practice.
- **Data model:** `skills/setup/schema.md` (Notion DDL and local templates), then `reference/rules.md`. Existing bases pick up new properties with `/jtbd-base:setup upgrade`.
- **Rules** (status thresholds, scale, language, writing rules): `reference/rules.md` and `skills/setup/seed/concepts.md`.
- **Language:** stored content is English, replies follow your language (`reference/rules.md`).

## Development

```bash
git clone https://github.com/<github-user>/jtbd-base
cd ~/my-jtbd-project
claude --plugin-dir ~/path/to/jtbd-base     # load the local copy for this session
```

`/reload-plugins` applies edits without restarting. `claude plugin validate ~/path/to/jtbd-base` checks the manifest.

Repository layout:

```
jtbd-base/
├── .claude-plugin/
│   ├── plugin.json         Plugin manifest
│   └── marketplace.json    Lets users install from this repo
├── reference/rules.md      Data model, scoring and rules every skill reads first
├── skills/
│   ├── setup/              schema.md, seed/concepts.md
│   ├── capture/
│   ├── query/
│   ├── method/references/  The 15 methods
│   └── ingest/
├── agents/                 analyst.md, auditor.md
├── scripts/jtbd_local.py   Local backend helper
└── jtbd.config.example.yaml
```

## Privacy

Transcripts stay in `inbox/` on your machine. Only short anonymized quotes (participant codes like P03) go into the base. The auditor and the lint flag quotes that look like they contain personal data. Full details in the [Privacy Policy](PRIVACY.md).

## Credits

- Outcome-Driven Innovation and the opportunity score: Tony Ulwick.
- Forces of progress and the Switch interview: Bob Moesta and Chris Spiek.
- Importance and satisfaction map: Dan Olsen, *The Lean Product Playbook*.

## License

MIT, see [LICENSE](LICENSE).
