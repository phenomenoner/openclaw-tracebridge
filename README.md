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
  --profile lean

uv run --python 3.13 --group dev openclaw-tracebridge stats \
  --events traces/<run>/events.jsonl
```

## Docs

- Phase A spec: `docs/PHASE_A_V0_SPEC.md`
- Devlog: `docs/DEVLOG.md`
- Dogfood report: `docs/DOGFOOD_2026-02-09.md`
- Landscape + rationale: `docs/LANDSCAPE_AND_RATIONALE.md`

## Status

- Phase A scaffold is live (`tracebridge.event.v1`, importer, stats)
- Phase A.1 live: better kind split (`cron.fire`, `system.event`, `tool.call`)
- `profile=lean|debug` import mode is available (`lean` default)
- Dogfood run validated on real OpenClaw session JSONL
- Repo is private and in active hacking-mode bootstrap
