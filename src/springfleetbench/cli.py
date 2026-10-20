from __future__ import annotations

import argparse
import json
from pathlib import Path

from springfleetbench.benchmark import SuiteError, load_suite, run_suite


def main() -> int:
    parser = argparse.ArgumentParser(prog="springfleetbench")
    subparsers = parser.add_subparsers(dest="command", required=True)
    inspect = subparsers.add_parser("inspect", help="validate and summarize a suite")
    inspect.add_argument("suite", type=Path)
    run = subparsers.add_parser("run", help="run a candidate against every service fixture")
    run.add_argument("--suite", type=Path, required=True)
    run.add_argument("--candidate", required=True, help="trusted local shell command to test")
    run.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "inspect":
            suite = load_suite(args.suite)
            print(json.dumps({"name": suite.get("name", args.suite.stem),
                              "version": suite.get("version", "unknown"),
                              "tasks": [{"id": task["id"], "description": task.get("description", "")}
                                        for task in suite["tasks"]]}, indent=2))
            return 0
        result = run_suite(args.suite, args.candidate)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(f"{result['tasks_passed']}/{result['tasks_total']} tasks passed; fleet_success={result['fleet_success']}")
        print(f"Wrote {args.output}")
        return 0 if result["fleet_success"] else 1
    except SuiteError as exc:
        parser.error(str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
