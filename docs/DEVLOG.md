# Devlog

## 2026-02-09

### Bootstrap
- Created private repo `phenomenoner/openclaw-tracebridge`.
- Added Python 3.13 + uv-first project skeleton.
- Added initial docs (`README`, `PHASE_A_V0_SPEC.md`).

### Phase A MVP implemented
- Added `tracebridge.event.v1` schema (`TraceEvent`) and run metadata (`RunMeta`).
- Added JSONL writer/reader helpers.
- Added `openclaw-tracebridge` CLI:
  - `run-init`
  - `import-openclaw-session`
  - `stats`
- Added OpenClaw session importer adapter with lean payload defaults.

### Reliability fixes
- Added package build config (`hatchling`) so CLI script resolves correctly under `uv run`.
- Added `.gitignore` and removed accidental `__pycache__` artifacts.
- Added overwrite-by-default import behavior (`--append` opt-in).

### Validation
- Tests: `3 passed`
- Lint: `ruff check .` passed
- Dogfood import on real OpenClaw session JSONL completed successfully.

### Phase A.1 completed
- Improved event-kind split in importer:
  - `tool.call` (including assistant-side toolCall payload)
  - `tool.result`
  - `cron.fire`
  - `system.event`
- Added importer profile flag:
  - `--profile lean` (default)
  - `--profile bridge` (adds `content`, no raw payload)
  - `--profile debug` (adds `content` and raw row)
- Added tests for kind split and debug profile.

### Research insight captured
- Added `docs/LANDSCAPE_AND_RATIONALE.md`:
  - what adjacent projects exist,
  - why TraceBridge is still needed,
  - why not just install Agent Lightning for this phase.

### Phase A.2 pivot started (Agent Lightning bridge)
- Added run-level capability flags in `RunMeta`.
- Added `export-agent-lightning` CLI subcommand.
- Added exporter module for:
  - `messages` dataset (`tracebridge.agent_lightning.messages.v0`)
  - `triplets` dataset (`tracebridge.agent_lightning.triplet.v0`)
- Added deterministic pairing logic (`agent.input` -> `agent.output`) with skip accounting.
- Added optional `--reward-mode heuristic-basic` for bootstrap reward experiments.
- Added `docs/AGENT_LIGHTNING_BRIDGE_SPEC.md`.

### Bridge dogfood completed
- Added `scripts/smoke_agent_lightning_bridge.sh`.
- Ran end-to-end bridge smoke on a real OpenClaw session.
- Produced:
  - `messages` export rows
  - `triplets` export rows
  - skip-accounting counters for missing/unpaired events
- Added report: `docs/DOGFOOD_AGENT_LIGHTNING_BRIDGE_2026-02-09.md`.

### Next
- Phase B: replay contract and deterministic A/B harness.
- Add first Agent Lightning consumer smoke (minimal trainer-side ingestion check).
