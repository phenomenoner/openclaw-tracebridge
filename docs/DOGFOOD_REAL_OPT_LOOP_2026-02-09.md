# Dogfood Report — Real Optimization Loop Smoke (2026-02-09)

Command:

```bash
bash scripts/run_real_optimization_loop_smoke.sh
```

Outputs:
- `artifacts/optimization-loop-smoke/optimization-report.json`
- `artifacts/optimization-loop-smoke/runtime-smoke.log.json`

Observed summaries:

```json
{"ok": true, "rows_total": 129, "rows_train": 105, "rows_val": 24, "baseline_policy": "identity", "best_policy": "sanitize_errors", "baseline_train_reward": 0.711905, "baseline_val_reward": 0.670833, "best_train_reward": 0.789048, "best_val_reward": 0.770833, "uplift_val_abs": 0.1, "uplift_val_pct": 14.9068}
{"ok": true, "installed": true, "reason": null, "rows_total": 129, "rows_used": 12, "spans_written": 36, "rollout_id": "ro-038931a52d74"}
```

Interpretation (preliminary):
- The measurable optimization case is now in place (baseline vs optimized validation reward).
- Runtime-side Agent Lightning hook smoke is operational with in-memory store traces.
- This closes the previously identified MVP gap for a practical optimization-loop demonstration.
