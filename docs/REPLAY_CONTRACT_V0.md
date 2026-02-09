# Replay Contract v0

## Goal
Provide deterministic A/B splits over exported JSONL datasets so replay/evaluation runs are reproducible.

## Scope
CLI commands:
- `replay-split`
- `replay-manifest`

## `replay-split`

Input:
- JSONL records (typically `agent_lightning_messages.jsonl` or `agent_lightning_triplets.jsonl`)

Output:
- `out-a` JSONL
- `out-b` JSONL

Determinism rules:
- Split assignment uses SHA-256 hash of `split:{seed}:{key}`.
- `key` defaults to `id` field; falls back to `event_id`, `sequence_id`, then index.
- Same input + seed + key-field + ratio => identical split.

Optional deterministic sampling:
- `--sample-size N`
- `--sample-seed S`
- Sampling ranks rows using `sample:{sample_seed}:{key}` before split.

## `replay-manifest`

Input:
- JSONL dataset path

Output JSON:
- `schema: tracebridge.replay.manifest.v0`
- `rows`
- `sha256`
- `generated_at`

Purpose:
- pin replay inputs to immutable content checksum
- simplify CI/regression checks

## Non-goals
- No semantic equivalence checks across different schemas.
- No task-specific scoring in v0.

## Acceptance
- Re-running `replay-split` with same parameters yields byte-identical outputs.
- `replay-manifest` produces stable row-count and SHA for unchanged inputs.
