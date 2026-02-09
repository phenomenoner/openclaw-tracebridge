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

### Research pass (fail-eager)
- Attempted direct X exploration via `bird`, blocked by missing auth tokens.
- Switched to GitHub/docs/web snippets and captured findings in:
  - `docs/RESEARCH_AGENT_LIGHTNING_USAGE.md`

### Phase B start: deterministic replay tooling
- Added `replay-split` CLI command:
  - deterministic A/B split by hash(key, seed)
  - optional deterministic sampling (`sample-size`, `sample-seed`)
- Added `replay-manifest` CLI command:
  - row count + sha256 for reproducibility checks
- Added replay module and tests.
- Added `docs/REPLAY_CONTRACT_V0.md`.

### Agent Lightning consumer smoke added
- Added `agent-lightning-consumer-smoke` CLI command:
  - validates `messages` and `triplets` dataset shapes
  - strict fail mode for CI/automation
- Added end-to-end smoke script:
  - `scripts/smoke_end_to_end_lightning.sh`
  - import -> export -> replay split -> consumer checks
- Added docs:
  - `docs/AGENT_LIGHTNING_CONSUMER_SMOKE.md`

### End-to-end smoke completed
- Added and ran `scripts/smoke_end_to_end_lightning.sh`.
- Verified full path:
  - import -> export -> replay split -> consumer strict checks.
- Added report: `docs/DOGFOOD_END2END_2026-02-09.md`.

### Close-gap: real optimization loop smoke
- Added `optimization-loop-smoke` CLI command:
  - deterministic train/val split over triplets
  - baseline (`identity`) vs policy-search (`sanitize_errors`, `safe_rewrite`, `short_safe`)
  - measurable validation uplift outputs
- Added `agent-lightning-runtime-smoke` CLI command:
  - optional runtime-side smoke against `agentlightning` + `InMemoryLightningStore`
  - emits synthetic spans and reward annotations
  - strict fail mode supported
- Added one-shot script:
  - `scripts/run_real_optimization_loop_smoke.sh`
- Added docs:
  - `docs/REAL_OPTIMIZATION_LOOP.md`
- Ran close-gap smoke end-to-end:
  - validation uplift observed: `+0.10` reward (`+14.9%`)
  - runtime smoke spans written: `36`
- Added report:
  - `docs/DOGFOOD_REAL_OPT_LOOP_2026-02-09.md`

### Next
- Wire replay outputs into benchmark-style A/B reporting.
- Add richer policy families and task-specific rewards beyond keyword heuristics.

### Upstream linkage addendum (#12660 / #12633)
- Contributed architecture feedback to OpenClaw #12660 (context-provider slot proposal):
  - emphasized fail-open fallback, provider timeout budgets, and shadow-mode rollout before cutover.
  - this directly matches TraceBridge’s replay/split/manifest path for low-risk A/B validation.
- Contributed stability feedback to OpenClaw #12633 (session indexing skip bug):
  - highlighted that cold-start correctness and session-heavy timeout resilience should be treated as separate failure classes.
  - implication for TraceBridge: maintain replay-ready artifacts so upstream fixes can be validated against repeatable slices.
