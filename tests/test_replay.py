import json
from pathlib import Path

from openclaw_tracebridge.cli import main


def _write_rows(path: Path, n: int = 20) -> None:
    rows = [{"id": f"row_{i:03d}", "v": i} for i in range(n)]
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")


def _load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_replay_split_is_deterministic(tmp_path: Path) -> None:
    inp = tmp_path / "input.jsonl"
    a1 = tmp_path / "a1.jsonl"
    b1 = tmp_path / "b1.jsonl"
    a2 = tmp_path / "a2.jsonl"
    b2 = tmp_path / "b2.jsonl"

    _write_rows(inp, n=50)

    rc1 = main(
        [
            "replay-split",
            "--input",
            str(inp),
            "--out-a",
            str(a1),
            "--out-b",
            str(b1),
            "--seed",
            "7",
            "--split-ratio",
            "0.5",
        ]
    )
    rc2 = main(
        [
            "replay-split",
            "--input",
            str(inp),
            "--out-a",
            str(a2),
            "--out-b",
            str(b2),
            "--seed",
            "7",
            "--split-ratio",
            "0.5",
        ]
    )

    assert rc1 == 0
    assert rc2 == 0
    assert a1.read_text(encoding="utf-8") == a2.read_text(encoding="utf-8")
    assert b1.read_text(encoding="utf-8") == b2.read_text(encoding="utf-8")


def test_replay_split_sample_size(tmp_path: Path) -> None:
    inp = tmp_path / "input.jsonl"
    a = tmp_path / "a.jsonl"
    b = tmp_path / "b.jsonl"

    _write_rows(inp, n=40)
    rc = main(
        [
            "replay-split",
            "--input",
            str(inp),
            "--out-a",
            str(a),
            "--out-b",
            str(b),
            "--sample-size",
            "10",
            "--sample-seed",
            "99",
        ]
    )
    assert rc == 0

    total = len(_load_jsonl(a)) + len(_load_jsonl(b))
    assert total == 10


def test_replay_manifest(tmp_path: Path) -> None:
    inp = tmp_path / "input.jsonl"
    out = tmp_path / "manifest.json"

    _write_rows(inp, n=5)
    rc = main(["replay-manifest", "--input", str(inp), "--out", str(out)])
    assert rc == 0

    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["schema"] == "tracebridge.replay.manifest.v0"
    assert payload["rows"] == 5
    assert len(payload["sha256"]) == 64
