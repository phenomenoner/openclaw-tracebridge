# Agent Lightning Bridge Spec (v0)

## Why this exists
TraceBridge began as OpenClaw-native ingestion/replay infrastructure. We are now explicitly adding a bridge to Agent Lightning so we can leverage algorithm power without replacing OpenClaw runtime workflows.

## Layering model

1. **OpenClaw runtime layer**
   - Session JSONL, cron, heartbeat, tool events.
2. **TraceBridge normalization layer**
   - `tracebridge.event.v1` with deterministic sequence ordering.
3. **Agent Lightning bridge layer (this doc)**
   - Export normalized traces into training-friendly datasets.
4. **Algorithm execution layer**
   - APO/RL/SFT loops run in Agent Lightning or compatible stacks.

## Export targets

### A) `messages` export
Schema: `tracebridge.agent_lightning.messages.v0`

Each row contains:
- `messages` in OpenAI-style chat form (`user`, `assistant`)
- sequence and event linkage metadata
- middle-event counts (`tool.call`, `tool.result`, etc.)

Best fit:
- prompt optimization / supervised shaping workflows
- low-friction first integration with Agent Lightning adapters

### B) `triplets` export
Schema: `tracebridge.agent_lightning.triplet.v0`

Each row contains:
- `state_text`
- `action_text`
- `reward` (`null` or heuristic)

Best fit:
- reward-aware experimentation where explicit ground-truth rewards are not yet available

## Reward policy (v0)
- `reward-mode=none` (default): no fabricated reward.
- `reward-mode=heuristic-basic`: deterministic placeholder reward based on event structure and error signals.

Important:
- Heuristic rewards are **bootstrap-only**; not substitute for task-specific scoring.

## Content profiles

`import-openclaw-session --profile`:
- `lean`: token-efficient metadata-only (default)
- `bridge`: includes textual content, no raw payload
- `debug`: includes textual content + raw row payload

Bridge export requires content, therefore `bridge` or `debug` is recommended for source imports.

## MVP bridge acceptance

We call bridge MVP-ready when:
1. `messages` export works on real OpenClaw runs.
2. `triplets` export works with deterministic reward mode behavior.
3. At least one Agent Lightning smoke workflow can consume exported artifacts end-to-end.
4. Documentation includes limitations and integration boundaries.

## Non-goals (v0)
- No claim of one-click RL quality from arbitrary logs.
- No forced dependency on Agent Lightning runtime package.
- No invasive changes to OpenClaw core runtime.
