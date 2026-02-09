#!/usr/bin/env bash
set -euo pipefail

# Phase 1 Shadow Training Cycle
# - export fresh datasets from a real OpenClaw session
# - run deterministic replay split + consumer checks
# - run optimization-loop smoke + runtime hook smoke
# - write timestamped artifact bundle + summary

SESSION_JSONL="${1:-$HOME/.openclaw/agents/main/sessions/920609f2-4171-4818-a1dd-af93cb4b8643.jsonl}"
OUT_ROOT="${2:-artifacts/phase1-shadow}"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
CYCLE_DIR="$OUT_ROOT/$TS"

mkdir -p "$CYCLE_DIR"

bash scripts/smoke_end_to_end_lightning.sh "$SESSION_JSONL" "$CYCLE_DIR/end2end" "run_phase1_${TS}" > "$CYCLE_DIR/step_end2end.log" 2>&1
bash scripts/run_real_optimization_loop_smoke.sh "$CYCLE_DIR/end2end/triplets.jsonl" "$CYCLE_DIR/end2end/messages.jsonl" "$CYCLE_DIR/optimization" > "$CYCLE_DIR/step_opt.log" 2>&1

uv run --python 3.13 -- python - <<'PY' "$CYCLE_DIR"
import json,sys,glob,os
c=sys.argv[1]
summary={"ok":True,"cycle_dir":c}

def load(path):
    with open(path,encoding='utf-8') as f:
        return json.load(f)

opt=load(os.path.join(c,'optimization','optimization-report.json'))
rt=load(os.path.join(c,'optimization','runtime-smoke.log.json'))
summary['optimization']={
    'baseline_val_reward': opt.get('baseline_val_reward'),
    'best_val_reward': opt.get('best_val_reward'),
    'uplift_val_abs': opt.get('uplift_val_abs'),
    'uplift_val_pct': opt.get('uplift_val_pct'),
    'best_policy': opt.get('best_policy'),
}
summary['runtime']={
    'ok': rt.get('ok'),
    'rows_used': rt.get('rows_used'),
    'spans_written': rt.get('spans_written'),
}
out=os.path.join(c,'summary.json')
with open(out,'w',encoding='utf-8') as f:
    json.dump(summary,f,ensure_ascii=False,indent=2)
print(json.dumps(summary,ensure_ascii=False))
PY
