#!/usr/bin/env bash
set -euo pipefail

# Close-the-gap smoke:
# 1) run measurable optimization loop on triplets
# 2) run optional Agent Lightning runtime hook smoke

TRIPLETS="${1:-artifacts/end2end-smoke/triplets.jsonl}"
MESSAGES="${2:-artifacts/end2end-smoke/messages.jsonl}"
OUT_DIR="${3:-artifacts/optimization-loop-smoke}"

mkdir -p "$OUT_DIR"

uv run --python 3.13 --group dev openclaw-tracebridge optimization-loop-smoke \
  --triplets "$TRIPLETS" \
  --val-ratio 0.2 \
  --seed 42 \
  --out "$OUT_DIR/optimization-report.json" | tee "$OUT_DIR/optimization.log.json"

# Runtime hook requires agentlightning package. We run with --with to keep core deps lean.
uv run --python 3.13 --group dev --with agentlightning openclaw-tracebridge agent-lightning-runtime-smoke \
  --input "$MESSAGES" \
  --max-rows 12 \
  --strict | tee "$OUT_DIR/runtime-smoke.log.json"

echo "Optimization loop smoke complete: $OUT_DIR"
