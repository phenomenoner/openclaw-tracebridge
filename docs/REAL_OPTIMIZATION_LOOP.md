# Real Optimization Loop (Smoke v0)

## What this closes
This adds the missing two pieces from bridge-only readiness:
1. **runtime-side Agent Lightning hook smoke**
2. **measurable baseline-vs-optimized metric case**

## Commands

### A) Measurable optimization case

```bash
uv run --python 3.13 --group dev openclaw-tracebridge optimization-loop-smoke \
  --triplets artifacts/end2end-smoke/triplets.jsonl \
  --val-ratio 0.2 --seed 42 \
  --out artifacts/optimization-loop-smoke/optimization-report.json
```

Output includes:
- train/val row counts
- baseline policy reward (identity)
- selected best policy reward
- validation uplift (absolute + percent)

### B) Runtime-side hook smoke

```bash
uv run --python 3.13 --group dev --with agentlightning openclaw-tracebridge agent-lightning-runtime-smoke \
  --input artifacts/end2end-smoke/messages.jsonl \
  --max-rows 12 \
  --strict
```

This writes synthetic spans + rewards to `InMemoryLightningStore` via Agent Lightning tracer APIs.

### C) One-shot close-gap runner

```bash
bash scripts/run_real_optimization_loop_smoke.sh
```

## Notes
- Runtime smoke intentionally uses `--with agentlightning` so core TraceBridge remains lean.
- Optimization loop is a practical bootstrap benchmark, not a full RL benchmark.
- This gives an immediate measurable loop while preserving a clean path to APO/VERL workflows later.
