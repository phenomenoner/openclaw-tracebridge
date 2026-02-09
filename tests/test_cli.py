from pathlib import Path

from openclaw_tracebridge.cli import main


def test_run_init(tmp_path: Path) -> None:
    rc = main(["run-init", "--root", str(tmp_path), "--run-id", "run_test"]) 
    assert rc == 0
    assert (tmp_path / "run_test" / "run.json").exists()
