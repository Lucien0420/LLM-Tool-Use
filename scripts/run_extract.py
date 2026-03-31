"""CLI: extract structured fields from one inquiry (Ollama or OpenAI-compatible API)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from app.services.extract import InquiryExtractService


def _read_text(args: argparse.Namespace) -> str:
    if args.file:
        return Path(args.file).read_text(encoding="utf-8")
    if args.text is not None:
        return args.text
    if sys.stdin.isatty():
        return ""
    return sys.stdin.read()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract customer_name / contact / estimated_budget as JSON",
    )
    parser.add_argument("--text", "-t", help="Full inquiry text")
    parser.add_argument(
        "--file",
        "-f",
        metavar="PATH",
        help="Read UTF-8 text from file",
    )
    parser.add_argument(
        "--output",
        "-o",
        metavar="PATH",
        help="Also write JSON to this path (e.g. result.json)",
    )
    args = parser.parse_args()
    raw = _read_text(args).strip()
    if not raw:
        parser.error("Provide --text, --file, or pipe text on stdin")

    svc = InquiryExtractService()
    result = svc.extract_from_text(raw)
    out = result.model_dump_json(ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(out + "\n", encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
