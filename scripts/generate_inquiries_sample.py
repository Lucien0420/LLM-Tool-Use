"""One-off helper: regenerate samples/inquiries.csv with N varied rows (dev/demo)."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def body_for_row(i: int) -> str:
    names = [
        "Alex",
        "Jordan",
        "Sam",
        "Riley",
        "Casey",
        "Morgan",
        "Taylor",
        "Jamie",
        "Quinn",
        "Avery",
    ]
    co = [
        "Acme Co",
        "BlueSky",
        "Northwind",
        "Contoso",
        "Fabrikam",
        "Umbrella",
        "Globex",
        "Initech",
        "Hooli",
        "Stark",
    ]
    proj = [
        "landing page",
        "Shopify theme",
        "logo pack",
        "pitch deck",
        "API integration",
        "WordPress site",
        "brand guide",
        "email templates",
        "mobile app UI",
        "SEO audit",
    ]
    budgets = [
        "around $500",
        "under $2k",
        "~$5,000 USD",
        "ballpark EUR 3k",
        "GBP 1,500 max",
        "TBD",
        "NT$30k",
        "budget $12k–$18k",
        "no fixed budget yet",
        "starter under $300",
        "approved up to $25,000",
        "PO required; cap $8k",
        "split across two phases ~$4k each",
    ]
    p = 1000 + (i * 137) % 9000
    n = names[i % len(names)]
    c = co[i % len(co)]
    pr = proj[i % len(proj)]
    b = budgets[i % len(budgets)]

    templates = [
        f"We are {c}. Need {pr}. Email {n.lower()}@mail.test. Budget {b}.",
        f"Hi, {n} here from {c}. Looking for {pr}. Phone +1-555-{p:04d}. {b}.",
        f"RFP #{i}: {pr} for {c}. contact{i}@startup.io. Expected budget {b}.",
        f"Quick ask: quote for {pr}? I'm {n}. whatsapp +44 7700 {p:06d}. {b}.",
        f"From {c}: urgent {pr}. line: lineid_{i:03d}. Budget {b}.",
    ]
    return templates[i % len(templates)]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", type=int, default=50, help="number of rows")
    parser.add_argument(
        "-o",
        type=Path,
        default=Path("samples/inquiries.csv"),
        help="output path",
    )
    args = parser.parse_args()

    rows = [("id", "body")]
    for i in range(1, args.n + 1):
        rows.append((str(i), body_for_row(i)))

    args.o.parent.mkdir(parents=True, exist_ok=True)
    with args.o.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        for row in rows:
            w.writerow(row)
    print(f"Wrote {args.n} data rows to {args.o.resolve()}")


if __name__ == "__main__":
    main()
