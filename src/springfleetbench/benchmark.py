from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any


class SuiteError(ValueError):
    """Raised when a suite manifest is malformed."""


def load_suite(path: Path) -> dict[str, Any]:
    try:
        suite = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SuiteError(f"cannot read suite {path}: {exc}") from exc
    if not isinstance(suite, dict) or not isinstance(suite.get("tasks"), list) or not suite["tasks"]:
        raise SuiteError("suite must be an object with a non-empty 'tasks' array")
    ids: set[str] = set()
    for task in suite["tasks"]:
        if not isinstance(task, dict) or not isinstance(task.get("id"), str):
            raise SuiteError("each task must be an object with a string id")
        if task["id"] in ids:
            raise SuiteError(f"duplicate task id: {task['id']}")
        ids.add(task["id"])
        if not isinstance(task.get("fixture"), str):
            raise SuiteError(f"task {task['id']} is missing fixture")
    return suite


def _check(check: dict[str, Any], repo: Path) -> dict[str, Any]:
    relative = Path(check.get("path", ""))
    if relative.is_absolute() or ".." in relative.parts:
        raise SuiteError(f"unsafe check path: {relative}")
    path = repo / relative
    kind = check.get("type")
    if kind == "file_contains":
        found = path.is_file() and check.get("value", "") in path.read_text(encoding="utf-8")
        return {"name": check.get("name", f"{relative} contains expected value"), "passed": found}
    if kind == "file_not_contains":
        found = path.is_file() and check.get("value", "") not in path.read_text(encoding="utf-8")
        return {"name": check.get("name", f"{relative} excludes obsolete value"), "passed": found}
    raise SuiteError(f"unsupported check type in {check}")


def _run_commands(commands: list[list[str]], repo: Path) -> list[dict[str, Any]]:
    results = []
    for command in commands:
        if not isinstance(command, list) or not command or not all(isinstance(part, str) for part in command):
            raise SuiteError("validation commands must be non-empty arrays of strings")
        started = time.monotonic()
        try:
            proc = subprocess.run(command, cwd=repo, capture_output=True, text=True, timeout=300, check=False)
            results.append({
                "command": command,
                "exit_code": proc.returncode,
                "passed": proc.returncode == 0,
                "elapsed_seconds": round(time.monotonic() - started, 3),
                "stdout_tail": proc.stdout[-2000:],
                "stderr_tail": proc.stderr[-2000:],
            })
        except subprocess.TimeoutExpired as exc:
            results.append({"command": command, "passed": False, "timed_out": True,
                            "elapsed_seconds": round(time.monotonic() - started, 3),
                            "stdout_tail": str(exc.stdout or "")[-2000:],
                            "stderr_tail": str(exc.stderr or "")[-2000:]})
    return results


def run_suite(suite_path: Path, candidate: str) -> dict[str, Any]:
    suite_path = suite_path.resolve()
    suite = load_suite(suite_path)
    suite_root = suite_path.parent
    task_results = []
    for task in suite["tasks"]:
        fixture = (suite_root / task["fixture"]).resolve()
        if not fixture.is_dir():
            raise SuiteError(f"fixture directory does not exist for {task['id']}: {fixture}")
        with tempfile.TemporaryDirectory(prefix=f"sfb-{task['id']}-") as temp:
            repo = Path(temp) / "repo"
            shutil.copytree(fixture, repo)
            env = os.environ.copy()
            env["SFB_REPO_DIR"] = str(repo)
            env["SFB_TASK_ID"] = task["id"]
            started = time.monotonic()
            try:
                proc = subprocess.run(candidate, cwd=repo, env=env, shell=True, capture_output=True,
                                      text=True, timeout=600, check=False)
                candidate_result = {"exit_code": proc.returncode, "passed": proc.returncode == 0,
                                    "stdout_tail": proc.stdout[-3000:], "stderr_tail": proc.stderr[-3000:]}
            except subprocess.TimeoutExpired as exc:
                candidate_result = {"passed": False, "timed_out": True,
                                    "stdout_tail": str(exc.stdout or "")[-3000:],
                                    "stderr_tail": str(exc.stderr or "")[-3000:]}
            candidate_result["elapsed_seconds"] = round(time.monotonic() - started, 3)
            checks = [_check(check, repo) for check in task.get("checks", [])]
            commands = _run_commands(task.get("validation_commands", []), repo)
            passed = candidate_result["passed"] and all(c["passed"] for c in checks) and all(c["passed"] for c in commands)
            task_results.append({"id": task["id"], "description": task.get("description", ""),
                                 "passed": passed, "candidate": candidate_result,
                                 "checks": checks, "validation_commands": commands})

    passed_count = sum(result["passed"] for result in task_results)
    return {"suite": suite.get("name", suite_path.stem), "suite_version": suite.get("version", "unknown"),
            "candidate": candidate, "tasks_total": len(task_results), "tasks_passed": passed_count,
            "fleet_success": passed_count == len(task_results), "success_rate": passed_count / len(task_results),
            "tasks": task_results}
