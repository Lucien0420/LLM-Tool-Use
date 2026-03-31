"""Batch: many text files in a folder → one CSV (errors per row, run continues)."""

from __future__ import annotations

import csv
import logging
from pathlib import Path

from app.services.extract import InquiryExtractService

logger = logging.getLogger(__name__)

CSV_FIELDS = (
    "source",
    "customer_name",
    "contact",
    "estimated_budget",
    "error",
)


def extract_folder_to_csv(
    input_dir: Path,
    output_csv: Path,
    *,
    pattern: str = "*.txt",
    service: InquiryExtractService | None = None,
) -> tuple[int, int]:
    """
    Read each file matching `pattern` in `input_dir` as one inquiry; write `output_csv`.
    Returns (success_count, error_count). Failed rows still written with `error` set.
    """
    input_dir = input_dir.resolve()
    if not input_dir.is_dir():
        raise FileNotFoundError(f"Not a directory: {input_dir}")

    svc = service or InquiryExtractService()
    paths = sorted(input_dir.glob(pattern))
    if not paths:
        raise FileNotFoundError(f"No files matching {pattern!r} under {input_dir}")

    ok, err = 0, 0
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    with output_csv.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        w.writeheader()

        for path in paths:
            if not path.is_file():
                continue
            rel = path.name
            row = {
                "source": rel,
                "customer_name": "",
                "contact": "",
                "estimated_budget": "",
                "error": "",
            }
            try:
                raw = path.read_text(encoding="utf-8")
            except OSError as e:
                row["error"] = f"read failed: {e}"
                w.writerow(row)
                err += 1
                continue

            if not raw.strip():
                row["error"] = "empty file"
                w.writerow(row)
                err += 1
                continue

            try:
                r = svc.extract_from_text(raw)
                row["customer_name"] = r.customer_name or ""
                row["contact"] = r.contact or ""
                row["estimated_budget"] = r.estimated_budget or ""
                ok += 1
            except Exception as e:
                logger.exception("extract failed: %s", path)
                row["error"] = str(e)
                err += 1

            w.writerow(row)

    return ok, err
