# OpenClaw TraceBridge

OpenClaw TraceBridge is a Python-first bridge that turns OpenClaw runtime traces into reproducible datasets for offline evaluation and training-oriented workflows.

## Why this project exists

Most agent-training stacks are strong on algorithms, but weak on **runtime-native data plumbing**.
TraceBridge focuses on that missing layer:

1. Normalize OpenClaw session traces (`tracebridge.event.v1`)
2. Export training-friendly formats (`messages` / `triplets`)
3. Support deterministic replay/eval (`replay-split`, `replay-manifest`)

## Current status (preliminary)

- ✅ Import profiles: `lean`, `bridge`, `debug`
- ✅ Agent-Lightning-oriented export: `messages`, `triplets`
- ✅ Consumer smoke checks
- ✅ Deterministic replay split + manifest
- ✅ Runtime hook smoke (in-memory tracer/store path)
- ✅ Phase-1 shadow cycle automation (offline)

This is still **preliminary**. We are validating workflow reliability first, then effectiveness claims.

## Quickstart

```bash
uv run --python 3.13 --group dev openclaw-tracebridge --help

# 1) import a session
uv run --python 3.13 --group dev openclaw-tracebridge import-openclaw-session \
  --session-jsonl ~/.openclaw/agents/main/sessions/<session>.jsonl \
  --out traces/<run>/events.jsonl \
  --run-id <run> \
  --profile bridge

# 2) export messages dataset
uv run --python 3.13 --group dev openclaw-tracebridge export-agent-lightning \
  --events traces/<run>/events.jsonl \
  --out traces/<run>/messages.jsonl \
  --format messages

# 3) deterministic replay split
uv run --python 3.13 --group dev openclaw-tracebridge replay-split \
  --input traces/<run>/messages.jsonl \
  --out-a traces/<run>/train.jsonl \
  --out-b traces/<run>/val.jsonl \
  --seed 42 --split-ratio 0.9
```

## Reproducible smoke paths

```bash
# end-to-end bridge smoke
bash scripts/smoke_end_to_end_lightning.sh

# optimization-loop shadow smoke
bash scripts/run_real_optimization_loop_smoke.sh

# phase-1 shadow cycle
bash scripts/run_phase1_shadow_cycle.sh
```

## Docs

- `docs/INDEX.md` — entry point
- `docs/PHASE_A_V0_SPEC.md`
- `docs/AGENT_LIGHTNING_BRIDGE_SPEC.md`
- `docs/REPLAY_CONTRACT_V0.md`
- `docs/AGENT_LIGHTNING_CONSUMER_SMOKE.md`
- `docs/REAL_OPTIMIZATION_LOOP.md`
- `docs/PHASED_ADOPTION_PLAN.md`
- `docs/PUBLIC_CHECKLIST_2026-02-09.md`

Dogfood reports are under `docs/DOGFOOD_*.md`.

## Design principles

- Keep production runtime changes minimal
- Keep defaults token-lean
- Keep eval/training reproducible and auditable
- Prefer fail-open safety for production paths

## License

MIT
