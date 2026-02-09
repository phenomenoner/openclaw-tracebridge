# Dogfood Report — End-to-End Bridge Smoke (2026-02-09)

Command:

```bash
bash scripts/smoke_end_to_end_lightning.sh
```

Pipeline:
1. import OpenClaw session (`profile=bridge`)
2. export Agent Lightning datasets (`messages`, `triplets`)
3. deterministic replay split (`train`/`val`)
4. consumer-side strict shape checks

Key outputs:
- `artifacts/end2end-smoke/events.jsonl`
- `artifacts/end2end-smoke/messages.jsonl`
- `artifacts/end2end-smoke/triplets.jsonl`
- `artifacts/end2end-smoke/train_messages.jsonl`
- `artifacts/end2end-smoke/val_messages.jsonl`
- `artifacts/end2end-smoke/messages.manifest.json`

Observed summaries:

```json
{"ok": true, "run_id": "run_end2end_smoke", "events_written": 5726, "out": "artifacts/end2end-smoke/events.jsonl"}
{"ok": true, "format": "messages", "out": "artifacts/end2end-smoke/messages.jsonl", "rows_written": 129, "skipped_missing_content": 1, "skipped_unpaired": 5}
{"ok": true, "format": "triplets", "out": "artifacts/end2end-smoke/triplets.jsonl", "rows_written": 129, "skipped_missing_content": 1, "skipped_unpaired": 5}
{"ok": true, "input_rows": 129, "sampled_rows": 129, "out_a_rows": 119, "out_b_rows": 10, "out_a": "artifacts/end2end-smoke/train_messages.jsonl", "out_b": "artifacts/end2end-smoke/val_messages.jsonl"}
{"ok": true, "out": "artifacts/end2end-smoke/messages.manifest.json", "rows": 129}
{"ok": true, "format": "messages", "rows_total": 119, "rows_ok": 119, "rows_bad": 0}
{"ok": true, "format": "messages", "rows_total": 10, "rows_ok": 10, "rows_bad": 0}
{"ok": true, "format": "triplets", "rows_total": 129, "rows_ok": 129, "rows_bad": 0}
```

Conclusion:
- End-to-end bridge pipeline is operational and reproducible.
- Exported datasets pass strict consumer shape checks.
- We are ready for the next step: optional runtime-side Agent Lightning algorithm hook smoke.
