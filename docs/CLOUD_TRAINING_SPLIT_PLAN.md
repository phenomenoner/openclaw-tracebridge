# Cloud-Assisted Training Split Plan (Cost-Aware)

## Motivation
Local GPU/RAM upgrades can be expensive. We can split data and training across hosts.

## Recommended split
- Host A (local OpenClaw):
  - run production agent
  - collect traces
  - run exporters/replay manifests
- Host B (cloud training):
  - consume exported datasets
  - run Agent Lightning training/eval loops
  - publish model/prompt artifacts only after passing gates

## Data contract between hosts
Artifacts synced from A → B:
- `events.jsonl` (optional)
- `messages.jsonl` / `triplets.jsonl`
- replay splits + manifests
- feedback ledger snapshots (reaction-derived)

## Minimal infra options
- CPU-only cloud VM for preprocessing/eval first
- GPU instance only for short training windows
- object storage for dataset artifacts + manifests

## Guardrails
- Never auto-push optimized policy to production.
- Require quality + cost gates on canary set.
- Keep rollback to baseline one command away.

## Rollout phases
1. Offline shadow training (cloud)
2. Canary 5% with strict gates
3. Gradual traffic increase (20%/50%)
4. Weekly retrain cadence (if gains persist)
