#!/usr/bin/env bash
set -euo pipefail

# End-to-end smoke:
# 1) import OpenClaw session as bridge profile
# 2) export Agent Lightning messages + triplets
# 3) deterministic replay split for train/val
# 4) trainer-side dataset smoke validation

SESSION_JSONL="${1:-$HOME/.openclaw/agents/main/sessions/920609f2-4171-4818-a1dd-af93cb4b8643.jsonl}"
OUT_DIR="${2:-artifacts/end2end-smoke}"
RUN_ID="${3:-run_end2end_smoke}"

mkdir -p "$OUT_DIR"

uv run --python 3.13 --group dev openclaw-tracebridge import-openclaw-session \
  --session-jsonl "$SESSION_JSONL" \
  --out "$OUT_DIR/events.jsonl" \
  --run-id "$RUN_ID" \
  --profile bridge | tee "$OUT_DIR/step1-import.json"

uv run --python 3.13 --group dev openclaw-tracebridge export-agent-lightning \
  --events "$OUT_DIR/events.jsonl" \
  --out "$OUT_DIR/messages.jsonl" \
  --format messages | tee "$OUT_DIR/step2-export-messages.json"

uv run --python 3.13 --group dev openclaw-tracebridge export-agent-lightning \
  --events "$OUT_DIR/events.jsonl" \
  --out "$OUT_DIR/triplets.jsonl" \
  --format triplets \
  --reward-mode heuristic-basic | tee "$OUT_DIR/step2-export-triplets.json"

uv run --python 3.13 --group dev openclaw-tracebridge replay-split \
  --input "$OUT_DIR/messages.jsonl" \
  --out-a "$OUT_DIR/train_messages.jsonl" \
  --out-b "$OUT_DIR/val_messages.jsonl" \
  --split-ratio 0.9 --seed 42 | tee "$OUT_DIR/step3-replay-split.json"

uv run --python 3.13 --group dev openclaw-tracebridge replay-manifest \
  --input "$OUT_DIR/messages.jsonl" \
  --out "$OUT_DIR/messages.manifest.json" | tee "$OUT_DIR/step3-replay-manifest.json"

uv run --python 3.13 --group dev openclaw-tracebridge agent-lightning-consumer-smoke \
  --input "$OUT_DIR/train_messages.jsonl" \
  --format messages --strict | tee "$OUT_DIR/step4-consumer-train.json"

uv run --python 3.13 --group dev openclaw-tracebridge agent-lightning-consumer-smoke \
  --input "$OUT_DIR/val_messages.jsonl" \
  --format messages --strict | tee "$OUT_DIR/step4-consumer-val.json"

uv run --python 3.13 --group dev openclaw-tracebridge agent-lightning-consumer-smoke \
  --input "$OUT_DIR/triplets.jsonl" \
  --format triplets --strict | tee "$OUT_DIR/step4-consumer-triplets.json"

echo "End-to-end smoke complete: $OUT_DIR"
