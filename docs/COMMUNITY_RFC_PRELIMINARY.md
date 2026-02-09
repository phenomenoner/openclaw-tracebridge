# [Preliminary RFC] OpenClaw TraceBridge → Agent Lightning Training Bridge

## Status (preliminary)
We are building an integration path from OpenClaw runtime traces to Agent Lightning-compatible training datasets.

Current scope (already working):
- OpenClaw session import (`tracebridge.event.v1`)
- Agent-Lightning-oriented export (`messages`, `triplets`)
- Deterministic replay split + manifest
- Consumer smoke checks
- Reaction-feedback harvesting (Telegram logs)

We are **not** claiming benchmark superiority yet.

## Why this RFC
We want feedback early on integration design before scaling experiments.

## Architecture (current)
1. OpenClaw runtime (agent + tools + cron)
2. TraceBridge normalize layer
3. Export bridge (`messages` / `triplets`)
4. Replay/eval layer (deterministic splits)
5. Optional training host (Agent Lightning)

## Key design choices
- Keep OpenClaw runtime unchanged as much as possible.
- Keep capture and training decoupled (can run on separate hosts).
- Keep defaults token-lean (`lean` profile) and training-friendly (`bridge` profile) only when needed.
- Keep fail-open behavior in production usage.

## Questions for community feedback
1. Preferred minimal schema for cross-framework agent training?
2. Best practices for reward shaping when feedback is sparse/noisy?
3. Recommended eval protocol for agent-trace-derived datasets?
4. Pitfalls when using emoji/reaction signals as weak supervision?
5. Suggested benchmark tasks for practical agent workflows (tool-use heavy)?

## Planned next milestones
- V1: first offline train/eval report with clear caveats
- V2: canary rollout with strict guardrails (quality+cost gates)
- V3: generalized adapter docs for OpenClaw ecosystem

## Contact / repo
- Repo: `phenomenoner/openclaw-tracebridge`
- Feedback welcome via issues/discussions.
