#!/usr/bin/env bash
set -euo pipefail

# Smoke workflow:
# 1) import an OpenClaw session with profile=bridge
# 2) export Agent Lightning messages/triplets datasets
# 3) print summaries

SESSION_JSONL="${1:-$HOME/.openclaw/agents/main/sessions/920609f2-4171-4818-a1dd-af93cb4b8643.jsonl}"
OUT_DIR="${2:-artifacts/bridge-smoke}"
RUN_ID="${3:-run_bridge_smoke}"

mkdir -p "$OUT_DIR"

uv run --python 3.13 --group dev openclaw-tracebridge import-openclaw-session \
  --session-jsonl "$SESSION_JSONL" \
  --out "$OUT_DIR/events.jsonl" \
  --run-id "$RUN_ID" \
  --profile bridge | tee "$OUT_DIR/import.json"

uv run --python 3.13 --group dev openclaw-tracebridge export-agent-lightning \
  --events "$OUT_DIR/events.jsonl" \
  --out "$OUT_DIR/agent_lightning_messages.jsonl" \
  --format messages | tee "$OUT_DIR/export-messages.json"

uv run --python 3.13 --group dev openclaw-tracebridge export-agent-lightning \
  --events "$OUT_DIR/events.jsonl" \
  --out "$OUT_DIR/agent_lightning_triplets.jsonl" \
  --format triplets \
  --reward-mode heuristic-basic | tee "$OUT_DIR/export-triplets.json"

uv run --python 3.13 --group dev openclaw-tracebridge stats \
  --events "$OUT_DIR/events.jsonl" | tee "$OUT_DIR/stats.json"

echo "Smoke complete: $OUT_DIR"
