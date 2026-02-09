# TraceBridge → Agent Lightning Phased Adoption Plan

_Last updated: 2026-02-09 (UTC)_

## Canonical locations
- Plan doc: `openclaw-tracebridge/docs/PHASED_ADOPTION_PLAN.md`
- Phase-1 artifacts: `openclaw-tracebridge/artifacts/phase1-shadow/<timestamp>/`
- Reaction feedback ledger: `memory/feedback/telegram-reactions.jsonl`
- Reaction mapping: `memory/feedback/reaction-mapping.json`

## Phase 1 — Shadow Training (active now)
Goal: run offline train/eval loop without changing production behavior.

### What runs
1. Import/export/replay/consumer checks from real sessions
2. Optimization-loop smoke (baseline vs optimized)
3. Runtime-hook smoke (Agent Lightning in-memory tracer path)

### Cadence
- Daily shadow cycle cron (isolated)
- Outputs are timestamped artifact bundles

### Success criteria (for 3-day review)
- At least 3 successful shadow cycles
- No runtime-hook failures
- Stable positive uplift (not necessarily large), with no data integrity regressions
- Reaction feedback harvesting running daily and auditable
- Chunked-message label policy documented and applied in training joins

## Phase 2 — Offline robustness
Goal: improve reward quality and behavior diversity.

### Work items
- Add behavior variants (prompt/tool/response policies)
- Introduce richer task-grounded reward signals
- Add ablation report over fixed replay set
- Apply weak-supervision join rules for chunked Telegram messages (last-chunk reaction labels full batch)

Exit criteria:
- Clear winner policy on fixed benchmark
- Reproducible report with manifests

## Phase 3 — Canary (limited online impact)
Goal: verify gains under real workload with strict guardrails.

### Guardrails
- Fail-open fallback to baseline
- Quality/cost/latency gates
- Small traffic slice only

Exit criteria:
- No regressions on safety/quality
- Cost within budget

## Phase 4 — Gradual rollout + continuous loop
Goal: scalable and stable optimization operations.

### Operational mode
- Weekly retrain/eval cadence
- Monthly mapping/reward review
- Ongoing community feedback loop

## Cloud split strategy (cost-aware)
- Local host: production runtime + trace capture + export
- Cloud host: training/eval only (ephemeral GPU windows)
- Promotion to production requires explicit gate pass + rollback path
