import json
from pathlib import Path

from openclaw_tracebridge.cli import main


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")


def test_consumer_smoke_messages_strict_ok(tmp_path: Path) -> None:
    src = tmp_path / "messages.jsonl"
    _write_jsonl(
        src,
        [
            {
                "schema": "tracebridge.agent_lightning.messages.v0",
                "id": "msgpair_000001",
                "messages": [
                    {"role": "user", "content": "hello"},
                    {"role": "assistant", "content": "hi"},
                ],
            }
        ],
    )

    rc = main(
        [
            "agent-lightning-consumer-smoke",
            "--input",
            str(src),
            "--format",
            "messages",
            "--strict",
        ]
    )
    assert rc == 0


def test_consumer_smoke_triplets_strict_fail(tmp_path: Path) -> None:
    src = tmp_path / "triplets.jsonl"
    _write_jsonl(
        src,
        [
            {
                "schema": "tracebridge.agent_lightning.triplet.v0",
                "id": "triplet_000001",
                "state_text": "",
                "action_text": "ok",
                "reward": 0.5,
            }
        ],
    )

    rc = main(
        [
            "agent-lightning-consumer-smoke",
            "--input",
            str(src),
            "--format",
            "triplets",
            "--strict",
        ]
    )
    assert rc == 2
