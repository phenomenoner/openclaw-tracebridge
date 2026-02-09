# Agent Lightning Consumer Smoke (v0)

## Purpose
Provide a fast, deterministic check that exported datasets are consumable by trainer-side pipelines.

This is intentionally lightweight and dependency-free (no GPU stack required).

## Command

```bash
uv run --python 3.13 --group dev openclaw-tracebridge agent-lightning-consumer-smoke \
  --input <dataset.jsonl> \
  --format messages|triplets \
  --strict
```

## Validation rules

### `messages`
- `schema == tracebridge.agent_lightning.messages.v0`
- `messages` array has at least two entries
- first role is `user`, second role is `assistant`
- both contents are non-empty strings

### `triplets`
- `schema == tracebridge.agent_lightning.triplet.v0`
- `state_text` non-empty string
- `action_text` non-empty string
- `reward` is null or numeric

## Output
JSON summary includes:
- `rows_total`, `rows_ok`, `rows_bad`
- sample ids
- average text lengths (format-specific)

With `--strict`, command exits non-zero when:
- any bad rows exist, or
- dataset is empty.

## Positioning
This command is a bridge readiness check, not model training.
It is designed to fail fast before running expensive RL/APO/SFT loops.
