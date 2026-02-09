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
  --run-id <run>

uv run --python 3.13 --group dev openclaw-tracebridge stats \
  --events traces/<run>/events.jsonl
```

## Status

- Phase A scaffold is live (`tracebridge.event.v1`, importer, stats)
- Dogfood run validated on real OpenClaw session JSONL
- Repo is private and in active hacking-mode bootstrap
