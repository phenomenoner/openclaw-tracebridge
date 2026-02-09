# Dogfood Report — Agent Lightning Bridge (2026-02-09)

Command:

```bash
bash scripts/smoke_agent_lightning_bridge.sh
```

Source session:
- `~/.openclaw/agents/main/sessions/920609f2-4171-4818-a1dd-af93cb4b8643.jsonl`

Outputs:
- `artifacts/bridge-smoke/events.jsonl`
- `artifacts/bridge-smoke/agent_lightning_messages.jsonl`
- `artifacts/bridge-smoke/agent_lightning_triplets.jsonl`

Observed summaries:

```json
{"ok": true, "run_id": "run_bridge_smoke", "events_written": 5613, "out": "artifacts/bridge-smoke/events.jsonl"}
{"ok": true, "format": "messages", "out": "artifacts/bridge-smoke/agent_lightning_messages.jsonl", "rows_written": 125, "skipped_missing_content": 1, "skipped_unpaired": 5}
{"ok": true, "format": "triplets", "out": "artifacts/bridge-smoke/agent_lightning_triplets.jsonl", "rows_written": 125, "skipped_missing_content": 1, "skipped_unpaired": 5}
{"ok": true, "events": 5613, "token_estimate_total": 223133395, "cost_usd": 70.85764, "kinds": {"agent.input": 131, "agent.output": 201, "cron.fire": 44, "heartbeat": 42, "note": 1, "system.event": 78, "tool.call": 2452, "tool.result": 2664}}
```

Notes:
- End-to-end exporter path is operational on real OpenClaw session data.
- `messages` export currently uses deterministic input/output pairing.
- `triplets` export supports deterministic `heuristic-basic` reward mode for bootstrap experiments.
- Rows are skipped when textual content is missing (expected in mixed historical sessions).
