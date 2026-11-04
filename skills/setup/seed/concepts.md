# JTBD Concepts and Writing Rules

Reference for anyone adding to the knowledge base. The model follows the Outcome-Driven Innovation approach (Tony Ulwick) for statements and scoring, and Dan Olsen's importance and satisfaction map for prioritization.

## Glossary

| Term | Definition | Example |
|---|---|---|
| Job performer | The person who executes the job. Defined by the job, not by a job title. One performer can cover several roles. | UX researcher (could be: UX researcher, product designer, PM doing discovery) |
| Main job | The functional goal the performer is trying to achieve, stable over time and independent of any solution. | Turn customer conversations into product decisions |
| Job step | A chronological stage of the main job. Most main jobs have 5 to 12 steps. | Synthesize findings across interviews |
| Sub-job | A more specific job nested under a step, when a step is still too broad. | Tag quotes by theme |
| Emotional job | How the performer wants to feel while doing the job. | Feel confident my conclusions are grounded in data |
| Social job | How the performer wants to be perceived by others. | Be seen as the voice of the customer by the team |
| Related job | A job the performer does before, after or alongside the main job. | Recruit interview participants |
| Desired outcome | A metric the performer uses to judge how well a job or step gets done. | Minimize the time it takes to find every quote on a topic |
| Alternative | Anything the performer uses today to get the job done: competitor, workaround, manual work, doing nothing. | Spreadsheet plus manual tagging |
| Aspiration | The longer-term change the performer hopes for, in first person. | I want my research to shape strategy, not just validate features |

## Writing statements

### Job statement

**Verb + object + contextual clarifier.** Present tense, starts with an action verb, no solution, no adjective about quality.

- Good: *Prepare a synthesis of interview findings for the product team*
- Bad: *Use a tool to tag transcripts quickly* (names a solution and a quality)

Use "Why?" to move up to a main job and "How?" to move down to steps and sub-jobs.

### Desired outcome statement

**Direction + metric + object of control + contextual clarifier.**

- Direction: Minimize or Increase (prefer Minimize, it makes satisfaction easier to rate)
- Metric: time, likelihood, effort, number, cost, risk
- Good: *Minimize the likelihood of missing a recurring pain point across interviews*
- Bad: *Faster synthesis* (no object, no context)

An outcome must be measurable, stable over time and solution-free. Typically 5 to 10 outcomes per job step.

### Emotional and social jobs

Start with "Feel...", "Avoid feeling...", "Be perceived as...", "Avoid being perceived as...".

## Status lifecycle

| Status | Meaning | Rule |
|---|---|---|
| Hypothesis | Assumed by the team | Default for anything new without evidence |
| Supported | Seen in real data | At least 1 linked Evidence entry from a real source |
| Validated | Confirmed | Evidence from 3+ participants or a survey |
| Deprecated | No longer relevant | Kept for history, never deleted |

## Forces of progress

Why performers switch from an alternative to a new way of getting the job done, or stay put (Bob Moesta and Chris Spiek, Switch interview). Record them on each Alternative, from the performer's point of view.

| Force | Effect | Question to ask | Example |
|---|---|---|---|
| Push | Toward change | What in the current situation frustrates them enough to look elsewhere? | Re-tagging every past study by hand after each new one |
| Pull | Toward change | What attracts them to a new way of doing the job? | Finding every quote on a topic in a single search |
| Anxiety | Against change | What worries them about the new way? | Losing the nuance of their own coding scheme |
| Habit | Against change | What keeps them where they are? | The whole team knows the spreadsheet and years of studies live in it |

- A switch happens when Push + Pull outweigh Anxiety + Habit. A strong Habit explains why "Do nothing" is so often the real competitor.
- Write each force as a short sentence in the performer's terms. Push and Habit describe the current situation, never a feature of your product.
- Tag Evidence with the force a quote illustrates. A force without evidence is a hypothesis like any other entry.
- "Where it falls short" lists functional gaps per job; Push is the broader frustration that triggers the search. "Why they hire it" is the value the alternative delivers; Habit is what makes leaving it costly.

## Opportunity scoring

Importance and Satisfaction are averages on a **1 to 7 scale**, collected with the survey of method 8 "Find and rank opportunities with an importance and satisfaction survey" (`jtbd-base:method` skill).

- **Opportunity score** (Ulwick): importance + max(importance minus satisfaction, 0). Range 1 to 13. Use it to rank; treat the top of the list as the priority, not an absolute threshold.
- **Quadrant** (Olsen): importance 4 or more and satisfaction below 4 means Opportunity; importance 4 or more and satisfaction 4 or more means Competitive market; importance below 4 means Not worth going after.
- **Satisfaction delta**: satisfaction post-launch minus baseline satisfaction, used by the method "Measure satisfaction changes post-launch".

At least 20 to 30 responses are needed for low-fidelity results.
