# Reaction Calibration Protocol (v1, 30-second run)

Goal: lock emoji → score mapping so human intent and training signal stay aligned.

## Mapping candidate (current)
- ❤️ / ❤ = +2 (strong like)
- 👍 = +1 (like)
- 👎 = -1 (dislike)
- 🙈 = -2 (strong dislike)
- no reaction = unlabeled (NOT neutral)

## 30-second calibration steps
1. Assistant sends one test message with the 4 target emojis listed.
2. CK reacts once per target class (❤️, 👍, 👎, 🙈).
3. Harvester reads log events and verifies parsed emoji + score.
4. Assistant reports:
   - parsed emoji
   - mapped score
   - unknown/unmapped count
5. If mismatch exists, update `memory/feedback/reaction-mapping.json` and repeat once.

## Why this matters
Some emoji have visually similar variants (e.g., ❤ vs ❤️). We normalize and map both.

## Audit outputs
- Raw ledger: `memory/feedback/telegram-reactions.jsonl`
- Mapping file: `memory/feedback/reaction-mapping.json`
- Harvester state: `memory/feedback/reaction-harvester-state.json`

## Daily report requirement
Include in daily summary:
- harvested total today
- scored total today
- counts by emoji class
- unknown/unmapped counts
