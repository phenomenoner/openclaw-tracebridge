# OpenClaw TraceBridge

OpenClaw TraceBridge is a **Python-first, low-overhead trace adapter** project for OpenClaw.

## Mission

1. **Phase A (now):** ship a plug-and-play adapter layer that normalizes OpenClaw runtime events into a stable JSONL schema.
2. **Phase B (next):** add a replayable trace bus for deterministic A/B evaluation.

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
```

## Docs

- Phase A spec: `docs/PHASE_A_V0_SPEC.md`
- Devlog: `docs/DEVLOG.md`
- Dogfood report: `docs/DOGFOOD_2026-02-09.md`
- Landscape + rationale: `docs/LANDSCAPE_AND_RATIONALE.md`
- Agent Lightning bridge spec: `docs/AGENT_LIGHTNING_BRIDGE_SPEC.md`
- Agent Lightning bridge dogfood: `docs/DOGFOOD_AGENT_LIGHTNING_BRIDGE_2026-02-09.md`
- Agent Lightning usage research snapshot: `docs/RESEARCH_AGENT_LIGHTNING_USAGE.md`
- Replay contract v0: `docs/REPLAY_CONTRACT_V0.md`

## Status

- Phase A scaffold is live (`tracebridge.event.v1`, importer, stats)
- Phase A.1 live: better kind split (`cron.fire`, `system.event`, `tool.call`)
- Import profiles: `lean|bridge|debug` (`lean` default)
- Phase A.2 pivot started: Agent Lightning bridge exporter (`messages|triplets`)
- Phase B started: deterministic replay tooling (`replay-split`, `replay-manifest`)
- Dogfood run validated on real OpenClaw session JSONL
- Repo is private and in active hacking-mode bootstrap
