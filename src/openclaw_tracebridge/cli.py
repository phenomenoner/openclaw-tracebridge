from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from .adapters.openclaw_session import import_openclaw_session
from .io import iter_events
from .schema import RunMeta, new_run_id


def _cmd_run_init(args: argparse.Namespace) -> int:
    run_id = args.run_id or new_run_id()
    run_dir = Path(args.root) / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    meta = RunMeta(run_id=run_id, session_key=args.session_key, source=args.source)
    (run_dir / "run.json").write_text(meta.model_dump_json(indent=2), encoding="utf-8")
    print(json.dumps({"ok": True, "run_id": run_id, "run_dir": str(run_dir)}))
    return 0


def _cmd_import_session(args: argparse.Namespace) -> int:
    run_id = args.run_id or new_run_id()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    n = import_openclaw_session(
        session_jsonl=Path(args.session_jsonl),
        out_events=out,
        run_id=run_id,
        include_content=args.include_content,
        start_sequence_id=args.start_sequence_id,
    )
    print(json.dumps({"ok": True, "run_id": run_id, "events_written": n, "out": str(out)}))
    return 0


def _cmd_stats(args: argparse.Namespace) -> int:
    events = list(iter_events(Path(args.events)))
    kind_counts = Counter(e.kind for e in events)
    token_total = sum(e.token_estimate or 0 for e in events)
    cost_total_micros = sum(e.cost_usd_micros or 0 for e in events)

    payload = {
        "ok": True,
        "events": len(events),
        "token_estimate_total": token_total,
        "cost_usd": round(cost_total_micros / 1_000_000, 6),
        "kinds": {str(k): v for k, v in sorted(kind_counts.items(), key=lambda kv: str(kv[0]))},
    }
    print(json.dumps(payload, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="openclaw-tracebridge")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("run-init", help="Create a run directory and run metadata")
    p_init.add_argument("--root", default="traces")
    p_init.add_argument("--run-id")
    p_init.add_argument("--session-key")
    p_init.add_argument("--source", default="openclaw")
    p_init.set_defaults(func=_cmd_run_init)

    p_import = sub.add_parser("import-openclaw-session", help="Import OpenClaw session JSONL into trace events")
    p_import.add_argument("--session-jsonl", required=True)
    p_import.add_argument("--out", required=True)
    p_import.add_argument("--run-id")
    p_import.add_argument("--include-content", action="store_true")
    p_import.add_argument("--start-sequence-id", type=int, default=1)
    p_import.set_defaults(func=_cmd_import_session)

    p_stats = sub.add_parser("stats", help="Summarize an events JSONL file")
    p_stats.add_argument("--events", required=True)
    p_stats.set_defaults(func=_cmd_stats)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
