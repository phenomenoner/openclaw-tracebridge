from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from .adapters.openclaw_session import import_openclaw_session
from .consumer_smoke import smoke_check_messages, smoke_check_triplets
from .exporters.agent_lightning import (
    export_to_agent_lightning_messages,
    export_to_agent_lightning_triplets,
)
from .io import iter_events
from .replay import build_replay_manifest, split_jsonl_for_replay
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
    if out.exists() and not args.append:
        out.unlink()
    n = import_openclaw_session(
        session_jsonl=Path(args.session_jsonl),
        out_events=out,
        run_id=run_id,
        include_content=args.include_content,
        start_sequence_id=args.start_sequence_id,
        profile=args.profile,
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


def _cmd_export_agent_lightning(args: argparse.Namespace) -> int:
    events_path = Path(args.events)
    out_path = Path(args.out)

    if args.format == "messages":
        summary = export_to_agent_lightning_messages(events_path=events_path, out_path=out_path)
    else:
        summary = export_to_agent_lightning_triplets(
            events_path=events_path,
            out_path=out_path,
            reward_mode=args.reward_mode,
        )

    print(
        json.dumps(
            {
                "ok": True,
                "format": summary.format,
                "out": str(out_path),
                "rows_written": summary.rows_written,
                "skipped_missing_content": summary.skipped_missing_content,
                "skipped_unpaired": summary.skipped_unpaired,
            },
            ensure_ascii=False,
        )
    )
    return 0


def _cmd_replay_split(args: argparse.Namespace) -> int:
    summary = split_jsonl_for_replay(
        input_path=Path(args.input),
        out_a_path=Path(args.out_a),
        out_b_path=Path(args.out_b),
        split_ratio=args.split_ratio,
        seed=args.seed,
        key_field=args.key_field,
        sample_size=args.sample_size,
        sample_seed=args.sample_seed,
    )
    print(
        json.dumps(
            {
                "ok": True,
                "input_rows": summary.input_rows,
                "sampled_rows": summary.sampled_rows,
                "out_a_rows": summary.out_a_rows,
                "out_b_rows": summary.out_b_rows,
                "out_a": args.out_a,
                "out_b": args.out_b,
            },
            ensure_ascii=False,
        )
    )
    return 0


def _cmd_replay_manifest(args: argparse.Namespace) -> int:
    manifest = build_replay_manifest(Path(args.input))
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ok": True, "out": str(out_path), "rows": manifest["rows"]}, ensure_ascii=False))
    return 0


def _cmd_agent_lightning_consumer_smoke(args: argparse.Namespace) -> int:
    in_path = Path(args.input)
    if args.format == "messages":
        summary = smoke_check_messages(in_path, max_rows=args.max_rows)
        payload = {
            "ok": summary.rows_bad == 0 and summary.rows_total > 0,
            "format": summary.format,
            "rows_total": summary.rows_total,
            "rows_ok": summary.rows_ok,
            "rows_bad": summary.rows_bad,
            "sample_ids": summary.sample_ids,
            "avg_user_chars": summary.avg_user_chars,
            "avg_assistant_chars": summary.avg_assistant_chars,
        }
    else:
        summary = smoke_check_triplets(in_path, max_rows=args.max_rows)
        payload = {
            "ok": summary.rows_bad == 0 and summary.rows_total > 0,
            "format": summary.format,
            "rows_total": summary.rows_total,
            "rows_ok": summary.rows_ok,
            "rows_bad": summary.rows_bad,
            "sample_ids": summary.sample_ids,
            "avg_state_chars": summary.avg_state_chars,
            "avg_action_chars": summary.avg_action_chars,
        }

    print(json.dumps(payload, ensure_ascii=False))
    if args.strict and not payload["ok"]:
        return 2
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
    p_import.add_argument("--profile", choices=["lean", "bridge", "debug"], default="lean")
    p_import.add_argument("--include-content", action="store_true", help="Force include text content payload")
    p_import.add_argument("--append", action="store_true", help="Append to existing output instead of overwrite")
    p_import.add_argument("--start-sequence-id", type=int, default=1)
    p_import.set_defaults(func=_cmd_import_session)

    p_stats = sub.add_parser("stats", help="Summarize an events JSONL file")
    p_stats.add_argument("--events", required=True)
    p_stats.set_defaults(func=_cmd_stats)

    p_export = sub.add_parser(
        "export-agent-lightning",
        help="Export trace events into Agent Lightning-friendly datasets",
    )
    p_export.add_argument("--events", required=True)
    p_export.add_argument("--out", required=True)
    p_export.add_argument("--format", choices=["messages", "triplets"], default="messages")
    p_export.add_argument("--reward-mode", choices=["none", "heuristic-basic"], default="none")
    p_export.set_defaults(func=_cmd_export_agent_lightning)

    p_split = sub.add_parser("replay-split", help="Create deterministic A/B replay splits from a JSONL dataset")
    p_split.add_argument("--input", required=True)
    p_split.add_argument("--out-a", required=True)
    p_split.add_argument("--out-b", required=True)
    p_split.add_argument("--split-ratio", type=float, default=0.5)
    p_split.add_argument("--seed", type=int, default=42)
    p_split.add_argument("--key-field", default="id")
    p_split.add_argument("--sample-size", type=int)
    p_split.add_argument("--sample-seed", type=int, default=42)
    p_split.set_defaults(func=_cmd_replay_split)

    p_manifest = sub.add_parser("replay-manifest", help="Generate manifest (rows + sha256) for replay input")
    p_manifest.add_argument("--input", required=True)
    p_manifest.add_argument("--out", required=True)
    p_manifest.set_defaults(func=_cmd_replay_manifest)

    p_consumer = sub.add_parser(
        "agent-lightning-consumer-smoke",
        help="Validate exported dataset shape with a lightweight trainer-side smoke check",
    )
    p_consumer.add_argument("--input", required=True)
    p_consumer.add_argument("--format", choices=["messages", "triplets"], default="messages")
    p_consumer.add_argument("--max-rows", type=int)
    p_consumer.add_argument("--strict", action="store_true", help="Exit non-zero when validation fails")
    p_consumer.set_defaults(func=_cmd_agent_lightning_consumer_smoke)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
