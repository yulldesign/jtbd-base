---
order: 8
title: Find and rank opportunities with an importance and satisfaction survey
phase: Prioritize
roles: [Product, Strategy]
status: Stable
inputs: Jobs or outcomes to rate
outputs: Importance and satisfaction averages, opportunity scores, an opportunity map
---

# 8. Find and rank opportunities with an importance and satisfaction survey

## What it gives you

A roadmap built on what matters most to users and is served worst today, which is where demand is urgent for customers and prospects and where product opportunities sit.

## Steps

1. Decide what to rate: your users' jobs, or their desired outcomes.
2. First table: "How important are the following statements for you?", each statement rated from 1 to 7.
3. Second table: "How satisfied are you with your ability to get this done today?", the same statements in the same order, rated from 1 to 7.
4. Send it as widely as you can. Aim for at least 20 to 30 answers for a first, low-fidelity read.
5. Place each statement on a map by its average importance and average satisfaction.

| | Low satisfaction | High satisfaction |
|---|---|---|
| **High importance** | Opportunity | Competitive market |
| **Low importance** | Not worth going after | Not worth going after |

The map comes from Dan Olsen (*The Lean Product Playbook*). The ranking uses Tony Ulwick's opportunity score: importance + max(importance minus satisfaction, 0).

## Running it with Claude

Claude builds the survey from the selected statements, loads the results into Importance and Satisfaction, and returns the ranked opportunities with their quadrant.
