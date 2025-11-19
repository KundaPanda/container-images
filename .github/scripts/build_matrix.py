#!/usr/bin/env python3
"""
Discover buildable services and emit the GitHub Actions matrix payload.

The previous inline bash script grew unwieldy and was error-prone when the
repository state changed (e.g., missing base commit or filenames containing
spaces).  This Python version keeps the same behaviour but in a clearer form,
adds better logging, and handles edge-cases like zero SHAs.
"""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
from typing import Dict, Iterable, List, Sequence, Set

ZERO_SHA = "0" * 40
# README-only updates should not trigger builds.
IGNORED_TOP_LEVEL_ENTRIES = {"README", "README.md"}


def log(msg: str) -> None:
    print(msg, flush=True)


def run_git(
    args: Sequence[str], check: bool = True
) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        ["git", *args],
        text=True,
        capture_output=True,
        check=False,
    )
    if check and proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc


def load_dirs_from_stdout(stdout: str) -> List[str]:
    dirs: Set[str] = set()
    for line in stdout.splitlines():
        if not line:
            continue
        parts = line.split("/", 1)
        top = parts[0]
        if top in IGNORED_TOP_LEVEL_ENTRIES:
            continue
        dirs.add(top)
    return sorted(dirs)


def tracked_top_level_dirs() -> List[str]:
    proc = run_git(["ls-files"])
    return load_dirs_from_stdout(proc.stdout)


def changed_top_level_dirs(base: str | None) -> List[str]:
    if not base or base == ZERO_SHA:
        log("No usable base SHA; treating all tracked dirs as changed.")
        return tracked_top_level_dirs()

    log(f"Fetching base commit {base} for diff comparison.")
    run_git(["fetch", "origin", base, "--depth=1"], check=False)

    diff = run_git(["diff", "--name-only", f"{base}...HEAD"], check=False)
    if diff.returncode != 0:
        log(
            f"git diff failed ({diff.stderr.strip() or diff.returncode}); "
            "falling back to building all services."
        )
        return tracked_top_level_dirs()

    return load_dirs_from_stdout(diff.stdout)


def load_services() -> List[Dict[str, str]]:
    services: List[Dict[str, str]] = []
    for cfg_path in sorted(pathlib.Path(".").glob("*/service.json")):
        dir_path = cfg_path.parent
        name = dir_path.name
        cfg = json.loads(cfg_path.read_text())

        context = cfg.get("context", str(dir_path))
        dockerfile = cfg.get("dockerfile")
        dockerfile_path = (
            str(dir_path / dockerfile) if dockerfile else str(dir_path / "Dockerfile")
        )

        platforms = cfg.get("platforms")
        platforms_value = (
            ",".join(platforms)
            if isinstance(platforms, list) and platforms
            else "linux/amd64"
        )

        services.append(
            {
                "name": name,
                "dir": str(dir_path),
                "context": context,
                "dockerfile": dockerfile_path,
                "platforms": platforms_value,
            }
        )

    return services


def select_services(
    services: Sequence[Dict[str, str]],
    changed_dirs: Iterable[str],
) -> List[Dict[str, str]]:
    changed = set(changed_dirs)
    log(f"Changed top-level dirs: {', '.join(changed) if changed else '(none)'}")

    if not services:
        return []

    if not changed:
        log("No changed dirs detected; building all services.")
        return list(services)

    selected = [
        svc
        for svc in services
        if svc["name"] in changed or svc["dir"].split("/", 1)[0] in changed
    ]

    if selected:
        log(
            f"Selected {len(selected)} services based on changes: "
            f"{', '.join(svc['name'] for svc in selected)}"
        )
        return selected

    log("No service-specific changes detected; defaulting to all services.")
    return list(services)


def write_output(matrix: Dict[str, List[Dict[str, str]]], has_work: bool) -> None:
    output_path = os.environ["GITHUB_OUTPUT"]
    with open(output_path, "a", encoding="utf-8") as fh:
        fh.write(f"matrix={json.dumps(matrix)}\n")
        fh.write(f"has_work={'true' if has_work else 'false'}\n")


def dump(label: str, data: object) -> None:
    log(f"{label}:")
    print(json.dumps(data, indent=2))


def main() -> int:
    event_name = os.environ.get("EVENT_NAME", "")
    base = (
        os.environ.get("PR_BASE_SHA")
        if event_name == "pull_request"
        else os.environ.get("BEFORE_SHA")
    )

    log("### Discovering services (*/service.json)")
    services = load_services()
    dump("All services", services)

    if not services:
        log("No services detected; emitting empty matrix.")
        write_output({"include": []}, False)
        return 0

    log("### Determining changed directories")
    changed_dirs = changed_top_level_dirs(base)

    selected = select_services(services, changed_dirs)
    has_work = bool(selected)

    matrix = {"include": selected}
    dump("Final matrix payload", matrix)
    write_output(matrix, has_work)
    return 0


if __name__ == "__main__":
    sys.exit(main())
