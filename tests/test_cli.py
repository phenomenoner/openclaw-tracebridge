import json
from pathlib import Path

from openclaw_tracebridge.cli import main


def test_run_init(tmp_path: Path) -> None:
    rc = main(["run-init", "--root", str(tmp_path), "--run-id", "run_test"])
    assert rc == 0

    run_json = tmp_path / "run_test" / "run.json"
    assert run_json.exists()

    payload = json.loads(run_json.read_text(encoding="utf-8"))
    assert payload["run_id"] == "run_test"
    assert "export.agent-lightning.messages.v0" in payload["capabilities"]
