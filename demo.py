#!/usr/bin/env python3
"""Single entry for portfolio: automated checks (no LLM) or optional Ollama smoke demo."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(cmd: list[str]) -> int:
    print("→", " ".join(cmd))
    return subprocess.run(cmd, cwd=ROOT, check=False).returncode


def main() -> int:
    p = argparse.ArgumentParser(
        description="demo.py — one command for tests and optional LLM pipeline",
    )
    p.add_argument(
        "mode",
        nargs="?",
        default="all",
        choices=["all", "test", "lint", "config", "llm"],
        help="all=lint + pytest + main config (no Ollama). llm=smoke extract + batch + csv (needs Ollama).",
    )
    args = p.parse_args()
    py = sys.executable

    if args.mode == "lint":
        return run([py, "-m", "ruff", "check", "app", "scripts", "main.py", "tests", "demo.py"])

    if args.mode == "test":
        return run([py, "-m", "pytest", "tests", "-q"])

    if args.mode == "config":
        return run([py, "main.py"])

    if args.mode == "all":
        for step in (
            [py, "-m", "ruff", "check", "app", "scripts", "main.py", "tests", "demo.py"],
            [py, "-m", "pytest", "tests", "-q"],
            [py, "main.py"],
        ):
            code = run(step)
            if code != 0:
                return code
        print("\nOK: lint + tests + config. Run `python demo.py llm` with Ollama for live extraction.")
        return 0

    if args.mode == "llm":
        # Smoke: one JSON line, small batch, first 5 CSV rows only
        steps = [
            [
                py,
                "scripts/run_extract.py",
                "-t",
                "Hi, I'm Alex. Email alex@example.com. Budget under $900.",
            ],
            [py, "scripts/batch_extract.py", "-i", "samples", "-o", "output/demo_batch.csv"],
            [
                py,
                "scripts/csv_extract.py",
                "-i",
                "samples/inquiries.csv",
                "-o",
                "output/demo_from.csv",
                "--limit",
                "5",
            ],
        ]
        for step in steps:
            code = run(step)
            if code != 0:
                print("LLM step failed — is Ollama running and LLM_MODEL set?", file=sys.stderr)
                return code
        print("\nOK: LLM smoke done. See output/demo_batch.csv and output/demo_from.csv")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
