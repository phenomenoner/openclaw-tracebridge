# OpenClaw TraceBridge

OpenClaw TraceBridge is a **Python-first, low-overhead trace adapter** project for OpenClaw.

## Mission

1. **Phase A (now):** ship a plug-and-play adapter layer that normalizes OpenClaw runtime events into a stable JSONL schema.
2. **Phase B (active):** add a replayable trace bus for deterministic A/B evaluation.
3. **Phase C (starting):** bridge traces into Agent Lightning-compatible optimization loops.

## Principles

- Token-efficient by default (lean event payloads)
- Cross-platform Python core (Linux first, macOS/Windows friendly)
- Upstream-friendly design (easy to PR into OpenClaw ecosystem)
- MIT-compatible development and redistribution posture

## Quickstart

```bash
uv run --python 3.13 --group dev openclaw-tracebridge --help
```

Import one OpenClaw session into normalized events:

```bash
uv run --python 3.13 --group dev openclaw-tracebridge import-openclaw-session \
  --session-jsonl ~/.openclaw/agents/main/sessions/<session>.jsonl \
  --out traces/<run>/events.jsonl \
  --run-id <run> \
  --profile bridge

uv run --python 3.13 --group dev openclaw-tracebridge stats \
  --events traces/<run>/events.jsonl

# export for Agent Lightning-oriented pipelines
uv run --python 3.13 --group dev openclaw-tracebridge export-agent-lightning \
  --events traces/<run>/events.jsonl \
  --out traces/<run>/agent_lightning_messages.jsonl \
  --format messages

# optional smoke script
bash scripts/smoke_agent_lightning_bridge.sh

# deterministic replay split
uv run --python 3.13 --group dev openclaw-tracebridge replay-split \
  --input traces/<run>/agent_lightning_messages.jsonl \
  --out-a traces/<run>/replay_a.jsonl \
  --out-b traces/<run>/replay_b.jsonl \
  --seed 42 --split-ratio 0.5

# trainer-side shape smoke check (strict exits non-zero on bad rows)
uv run --python 3.13 --group dev openclaw-tracebridge agent-lightning-consumer-smoke \
  --input traces/<run>/agent_lightning_messages.jsonl \
  --format messages \
  --strict

# full end-to-end smoke
bash scripts/smoke_end_to_end_lightning.sh

# measurable optimization-loop smoke (baseline vs optimized)
uv run --python 3.13 --group dev openclaw-tracebridge optimization-loop-smoke \
  --triplets artifacts/end2end-smoke/triplets.jsonl \
  --out artifacts/optimization-loop-smoke/optimization-report.json

# runtime-side hook smoke via Agent Lightning in-memory store
uv run --python 3.13 --group dev --with agentlightning openclaw-tracebridge agent-lightning-runtime-smoke \
  --input artifacts/end2end-smoke/messages.jsonl \
  --strict

# close-gap one-shot script
bash scripts/run_real_optimization_loop_smoke.sh
```

## Docs

- Docs index: `docs/INDEX.md`
- Phase A spec: `docs/PHASE_A_V0_SPEC.md`
- Devlog: `docs/DEVLOG.md`
- Dogfood report: `docs/DOGFOOD_2026-02-09.md`
- Landscape + rationale: `docs/LANDSCAPE_AND_RATIONALE.md`
- Agent Lightning bridge spec: `docs/AGENT_LIGHTNING_BRIDGE_SPEC.md`
- Agent Lightning bridge dogfood: `docs/DOGFOOD_AGENT_LIGHTNING_BRIDGE_2026-02-09.md`
- End-to-end dogfood: `docs/DOGFOOD_END2END_2026-02-09.md`
- Real optimization-loop dogfood: `docs/DOGFOOD_REAL_OPT_LOOP_2026-02-09.md`
- Agent Lightning usage research snapshot: `docs/RESEARCH_AGENT_LIGHTNING_USAGE.md`
- Replay contract v0: `docs/REPLAY_CONTRACT_V0.md`
- Consumer smoke spec: `docs/AGENT_LIGHTNING_CONSUMER_SMOKE.md`
- Real optimization loop smoke: `docs/REAL_OPTIMIZATION_LOOP.md`

## Status

- Phase A scaffold is live (`tracebridge.event.v1`, importer, stats)
- Phase A.1 live: better kind split (`cron.fire`, `system.event`, `tool.call`)
- Import profiles: `lean|bridge|debug` (`lean` default)
- Phase A.2 pivot started: Agent Lightning bridge exporter (`messages|triplets`)
- Phase B started: deterministic replay tooling (`replay-split`, `replay-manifest`)
- Runtime-side Agent Lightning hook smoke added (`agent-lightning-runtime-smoke`)
- Measurable optimization loop smoke added (`optimization-loop-smoke`)
- Close-gap dogfood produced baseline-vs-optimized uplift on validation set (+0.10 reward, +14.9%)
- End-to-end and close-gap dogfood runs validated on real OpenClaw session JSONL
- Repo is private and in active hacking-mode bootstrap
