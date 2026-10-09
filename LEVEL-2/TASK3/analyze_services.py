#!/usr/bin/env python3
"""Analyze online delivery and table booking availability by price range.

Uses only the Python standard library. Expected input columns are
`Price range`, `Has Online delivery`, and `Has Table booking`.
"""

import argparse
import csv
import math
from collections import Counter, defaultdict
from pathlib import Path


PRICE = "Price range"
DELIVERY = "Has Online delivery"
BOOKING = "Has Table booking"


def normalize_bool(value):
    value = (value or "").strip().casefold()
    if value in {"yes", "true", "1"}:
        return "Yes"
    if value in {"no", "false", "0"}:
        return "No"
    return None


def chi_square(table):
    """Pearson chi-square statistic and df for a 2-column contingency table."""
    row_totals = [sum(row) for row in table]
    col_totals = [sum(row[col] for row in table) for col in range(2)]
    total = sum(row_totals)
    if total == 0 or min(row_totals, default=0) == 0 or min(col_totals) == 0:
        return None
    statistic = 0.0
    for i, row in enumerate(table):
        for j, observed in enumerate(row):
            expected = row_totals[i] * col_totals[j] / total
            statistic += (observed - expected) ** 2 / expected
    return statistic, (len(table) - 1)


def cramers_v(statistic, rows, columns, total):
    if not total or min(rows - 1, columns - 1) <= 0:
        return None
    return math.sqrt(statistic / (total * min(rows - 1, columns - 1)))


def fmt_pct(numerator, denominator):
    return "—" if denominator == 0 else f"{100 * numerator / denominator:.1f}%"


def analyze(path):
    with open(path, newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        missing = [name for name in (PRICE, DELIVERY, BOOKING) if name not in (reader.fieldnames or [])]
        if missing:
            raise ValueError("Missing required column(s): " + ", ".join(missing))
        records = []
        invalid_price = 0
        for row in reader:
            try:
                price = int(row[PRICE].strip())
            except (AttributeError, ValueError):
                invalid_price += 1
                continue
            records.append((price, normalize_bool(row[DELIVERY]), normalize_bool(row[BOOKING])))

    if not records:
        raise ValueError("No rows with a usable price range were found.")
    levels = sorted({r[0] for r in records})
    grouped = defaultdict(list)
    for record in records:
        grouped[record[0]].append(record)

    lines = ["# Price Range vs. Online Delivery and Table Booking", "", "## Coverage", "",
             f"- Source: `{Path(path).name}`.", f"- Rows with a usable price range: **{len(records):,}**.",
             f"- Rows excluded for missing/invalid price range: **{invalid_price:,}**.",
             "- Availability percentages use only rows with a valid Yes/No value for that service.", "",
             "## Availability by price range", "",
             "| Price range | Restaurants | Online delivery: Yes | Table booking: Yes | Both services: Yes |",
             "|---:|---:|---:|---:|---:|"]
    for price in levels:
        group = grouped[price]
        d = [r[1] for r in group if r[1]]
        b = [r[2] for r in group if r[2]]
        both = [r for r in group if r[1] and r[2]]
        both_count = sum(r[1] == "Yes" and r[2] == "Yes" for r in both)
        lines.append(f"| {price} | {len(group):,} | {fmt_pct(d.count('Yes'), len(d))} | "
                     f"{fmt_pct(b.count('Yes'), len(b))} | {fmt_pct(both_count, len(both))} |")

    lines += ["", "## Association", ""]
    for index, (label, field_index) in enumerate((("Online delivery", 1), ("Table booking", 2))):
        eligible = [r for r in records if r[field_index]]
        counts = Counter((r[0], r[field_index]) for r in eligible)
        observed = [[counts[(level, answer)] for answer in ("Yes", "No")] for level in levels]
        lines.append(f"### {label}")
        lines.append("")
        if len(levels) < 2 or len(eligible) == 0:
            lines.append("Insufficient valid data to assess association.")
            lines.append("")
            continue
        result = chi_square(observed)
        if result is None:
            lines.append("Insufficient variation in the service values to calculate association.")
            lines.append("")
            continue
        statistic, df = result
        v = cramers_v(statistic, len(levels), 2, len(eligible))
        rates = [(level, counts[(level, "Yes")] / sum(observed[i]))
                 for i, level in enumerate(levels) if sum(observed[i])]
        low_price, low_rate = rates[0]
        high_price, high_rate = rates[-1]
        direction = "higher" if high_rate > low_rate else "lower" if high_rate < low_rate else "the same"
        lines.append(f"- Yes rates are **{fmt_pct(counts[(low_price, 'Yes')], sum(observed[0]))}** "
                     f"at the lowest price range ({low_price}) and **{fmt_pct(counts[(high_price, 'Yes')], sum(observed[-1]))}** "
                     f"at the highest ({high_price}); the highest-range rate is {direction}.")
        lines.append(f"- Pearson chi-square: **{statistic:.3f}** (df = {df}); Cramér’s V: **{v:.3f}** "
                     f"(n = {len(eligible):,}).")
        lines.append("")

    lines += ["## Interpretation", "",
              "Compare service rates across all price bands to see whether availability rises with price. "
              "The low-to-high comparison alone can miss a non-monotonic pattern. Chi-square and Cramér’s V "
              "describe association across the full table; they do not show that price causes a service to be offered. "
              "Cramér’s V measures strength (0 is no association; larger values indicate stronger association). "
              "This script does not calculate p-values.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", help="Restaurant CSV with the three expected columns")
    parser.add_argument("--output", default="price_range_services_report.md", help="Markdown report path")
    args = parser.parse_args()
    report = analyze(args.csv)
    Path(args.output).write_text(report, encoding="utf-8")
    print(report)
    print(f"Saved report to {args.output}")


if __name__ == "__main__":
    main()
