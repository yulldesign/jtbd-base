---
order: 6
title: Analyze research through the JTBD lens
phase: Analyze
roles: [User Research]
status: Stable
inputs: Interview transcripts or research notes
outputs: Evidence entries, new or updated jobs and outcomes
---

# 6. Analyze research through the JTBD lens

## What it gives you

Reading research as jobs gets past surface feedback to what people "hire" a product to do. It shows what really drives their behavior, which problems they are trying to solve, and which needs remain unmet, and it points product work toward value that matters.

## Steps

1. Read the transcript and spot what the participant is trying to achieve.
2. Capture one insight per sticky note on a board.
3. Cluster notes that talk about the same thing (affinity mapping).
4. In each cluster, pick the note that best expresses the participant's main job.
5. Order the other notes of the cluster in time: they become the job steps. Attach any outcomes you found to the job they measure.
6. Order the clusters in time relative to each other.
7. Review everything and rewrite each job and outcome in the standard grammar.

## Running it with Claude

This method is automated by the `jtbd-base:ingest` skill: the `jtbd-base:analyst` agent reads each transcript, pulls verbatims, proposes jobs, steps, outcomes and forces, and matches them to existing entries. Nothing is written until you approve; the verbatims become Evidence entries linked to what they support.
