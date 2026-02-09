# Landscape & Rationale (2026-02-09)

## Short answer
Yes, adjacent projects exist. No, we still need TraceBridge.

## What already exists (adjacent)

### Memory layers
- `mem0ai/mem0` — universal memory layer.
- `NevaMind-AI/memU` — memory engine for OpenClaw-style always-on agents.

### Observability / eval platforms
- `langfuse/langfuse` — observability + evals + datasets.
- `Arize-ai/phoenix` — observability and evaluation tooling.
- `AgentOps-AI/agentops` — agent monitoring and cost tracking.

### Training framework
- `microsoft/agent-lightning` — tracer/store/runner/algorithm loop for training and optimization.

## Why not "just install Agent Lightning"?

Because the scope is different from our immediate need.

We need a **runtime-ops adapter** for OpenClaw now:
- OpenClaw session JSONL/cron/heartbeat aware parsing,
- low-overhead capture with token-efficiency defaults,
- deterministic replay artifacts for A/B on memory/rerank/routing.

Agent Lightning is excellent, but it is primarily a **training orchestration framework**. That is a higher layer than our Phase A immediate goal.

Also, Agent Lightning installation docs currently describe official support as Linux-first (macOS/Windows outside WSL2 not yet supported), while TraceBridge aims for a Python core that remains portable.

## Design implications for TraceBridge

1. Keep **OpenClaw-native ingestion** first.
2. Keep schema OTEL-friendly and replay-friendly.
3. Keep payloads lean by default (`profile=lean`).
4. Add optional `profile=debug` for deep troubleshooting.
5. Preserve a future bridge path to external training/eval stacks, including Agent Lightning.

## License posture

- Agent Lightning is MIT.
- We can reuse ideas and implementation patterns.
- If we copy/adapt source code later, preserve MIT notices and attribution.
