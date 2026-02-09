import json
from pathlib import Path

from openclaw_tracebridge.cli import main


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")


def test_optimization_loop_smoke_uplift(tmp_path: Path) -> None:
    src = tmp_path / "triplets.jsonl"
    out = tmp_path / "report.json"

    rows = [
        {
            "schema": "tracebridge.agent_lightning.triplet.v0",
            "id": "t1",
            "state_text": "s1",
            "action_text": "operation failed with timeout",
            "metadata": {"middle_counts": {"tool.result": 1}},
        },
        {
            "schema": "tracebridge.agent_lightning.triplet.v0",
            "id": "t2",
            "state_text": "s2",
            "action_text": "completed successfully",
            "metadata": {"middle_counts": {"tool.result": 1}},
        },
        {
            "schema": "tracebridge.agent_lightning.triplet.v0",
            "id": "t3",
            "state_text": "s3",
            "action_text": "error occurred",
            "metadata": {"middle_counts": {"tool.result": 1}},
        },
        {
            "schema": "tracebridge.agent_lightning.triplet.v0",
            "id": "t4",
            "state_text": "s4",
            "action_text": "all good",
            "metadata": {"middle_counts": {"tool.result": 1}},
        },
    ]
    _write_jsonl(src, rows)

    rc = main(
        [
            "optimization-loop-smoke",
            "--triplets",
            str(src),
            "--seed",
            "9",
            "--val-ratio",
            "0.5",
            "--out",
            str(out),
        ]
    )
    assert rc == 0

    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["best_policy"] in {"sanitize_errors", "safe_rewrite", "short_safe", "identity"}
    assert payload["best_train_reward"] >= payload["baseline_train_reward"]


def test_runtime_smoke_nonstrict_returns_zero_when_missing_dependency(tmp_path: Path) -> None:
    src = tmp_path / "messages.jsonl"
    _write_jsonl(
        src,
        [
            {
                "schema": "tracebridge.agent_lightning.messages.v0",
                "id": "m1",
                "messages": [
                    {"role": "user", "content": "hi"},
                    {"role": "assistant", "content": "hello"},
                ],
            }
        ],
    )

    rc = main(["agent-lightning-runtime-smoke", "--input", str(src), "--max-rows", "1"])
    assert rc == 0
