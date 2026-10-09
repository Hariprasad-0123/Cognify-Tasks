#!/usr/bin/env python3
"""Analyze cuisine combinations and their restaurant ratings.

Usage:
    python cuisine_combinations.py path/to/restaurants.csv

The input should contain a cuisine-list column (commonly ``Cuisines``) and a
numeric rating column (commonly ``Aggregate rating``). Results are written to
``cuisine_analysis/`` beside the input file unless ``--output-dir`` is given.
"""

from __future__ import annotations

import argparse
import itertools
import re
from pathlib import Path

import pandas as pd


def find_column(columns: list[str], requested: str | None, candidates: tuple[str, ...], label: str) -> str:
    """Resolve a requested column, or find a common equivalent by name."""
    if requested:
        if requested not in columns:
            raise ValueError(f"{label} column {requested!r} not found. Available columns: {columns}")
        return requested

    normalized = {re.sub(r"[^a-z0-9]", "", c.lower()): c for c in columns}
    for candidate in candidates:
        key = re.sub(r"[^a-z0-9]", "", candidate.lower())
        if key in normalized:
            return normalized[key]
    raise ValueError(
        f"Could not identify the {label} column. Available columns: {columns}. "
        f"Pass it explicitly with --{label}-column."
    )


def parse_cuisines(value: object) -> tuple[str, ...]:
    """Split a comma-separated cuisine cell into a normalized, sorted tuple."""
    if pd.isna(value):
        return ()
    # Cuisine names in the source data are comma-separated. Normalize spaces
    # and case so duplicate spellings do not split the counts.
    items = {part.strip().casefold() for part in str(value).split(",") if part.strip()}
    return tuple(sorted(items))


def build_report(data: pd.DataFrame, cuisines_column: str, rating_column: str,
                 min_restaurants: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Return cuisine frequencies, exact-list statistics, and pair statistics."""
    work = data[[cuisines_column, rating_column]].copy()
    work["_cuisines"] = work[cuisines_column].map(parse_cuisines)
    work["_rating"] = pd.to_numeric(work[rating_column], errors="coerce")
    # In the common Zomato source, 0 denotes "Not rated" rather than a real
    # score. Treat non-positive values as missing for rating comparisons.
    work.loc[work["_rating"] <= 0, "_rating"] = float("nan")
    work = work[work["_cuisines"].map(bool)]

    # Count each cuisine once per restaurant.
    cuisine_frequency: dict[str, int] = {}
    # Exact sets keep combinations such as (A, B) distinct from restaurants
    # offering (A, B, C).
    exact: dict[tuple[str, ...], list[float]] = {}
    pairs: dict[tuple[str, str], list[float]] = {}
    for cuisine_set, rating in zip(work["_cuisines"], work["_rating"]):
        for cuisine in cuisine_set:
            cuisine_frequency[cuisine] = cuisine_frequency.get(cuisine, 0) + 1
        exact.setdefault(cuisine_set, [])
        if pd.notna(rating):
            exact[cuisine_set].append(float(rating))
        for pair in itertools.combinations(cuisine_set, 2):
            pairs.setdefault(pair, [])
            if pd.notna(rating):
                pairs[pair].append(float(rating))

    frequencies = pd.DataFrame(
        [{"cuisine": name.title(), "restaurant_count": count}
         for name, count in cuisine_frequency.items()]
    , columns=["cuisine", "restaurant_count"])
    if not frequencies.empty:
        frequencies.sort_values(["restaurant_count", "cuisine"], ascending=[False, True], inplace=True)

    def stats_rows(groups: dict[tuple[str, ...], list[float]], label: str) -> list[dict[str, object]]:
        rows = []
        for combo, ratings in groups.items():
            count = sum(1 for cuisine_set in work["_cuisines"] if cuisine_set == combo) if label == "exact" else len(ratings)
            # For pairs, rating count is also the number of restaurants with a
            # usable rating; recover total occurrences for a fair frequency.
            if label == "pair":
                count = sum(1 for cuisine_set in work["_cuisines"] if set(combo).issubset(cuisine_set))
            if count < min_restaurants:
                continue
            rows.append({
                "cuisines": " + ".join(name.title() for name in combo),
                "restaurant_count": count,
                "rated_restaurant_count": len(ratings),
                "mean_rating": round(sum(ratings) / len(ratings), 3) if ratings else None,
                "median_rating": round(float(pd.Series(ratings).median()), 3) if ratings else None,
            })
        return rows

    exact_report = pd.DataFrame(stats_rows(exact, "exact"))
    pair_report = pd.DataFrame(stats_rows(pairs, "pair"))
    for report in (exact_report, pair_report):
        if not report.empty:
            report.sort_values(["restaurant_count", "mean_rating"], ascending=[False, False], inplace=True)
            report.reset_index(drop=True, inplace=True)
    return frequencies, exact_report, pair_report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path, help="Restaurant dataset in CSV format")
    parser.add_argument("--cuisines-column", help="Cuisine-list column (auto-detected when omitted)")
    parser.add_argument("--rating-column", help="Rating column (auto-detected when omitted)")
    parser.add_argument("--min-restaurants", type=int, default=5,
                        help="Minimum combination frequency included in reports (default: 5)")
    parser.add_argument("--output-dir", type=Path, help="Where to write CSV reports")
    args = parser.parse_args()

    if args.min_restaurants < 1:
        parser.error("--min-restaurants must be at least 1")
    data = pd.read_csv(args.csv, encoding="utf-8-sig")
    cuisines_column = find_column(
        list(data.columns), args.cuisines_column,
        ("Cuisines", "Cuisine", "cuisine types"), "cuisines"
    )
    rating_column = find_column(
        list(data.columns), args.rating_column,
        ("Aggregate rating", "Rating", "Average rating", "Stars"), "rating"
    )
    frequencies, exact_report, pair_report = build_report(
        data, cuisines_column, rating_column, args.min_restaurants
    )

    output_dir = args.output_dir or args.csv.parent / "cuisine_analysis"
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "cuisine_frequencies.csv": frequencies,
        "exact_cuisine_combinations.csv": exact_report,
        "cuisine_pair_ratings.csv": pair_report,
    }
    for filename, frame in outputs.items():
        frame.to_csv(output_dir / filename, index=False)

    print(f"Analyzed {len(data):,} rows; results saved to {output_dir}")
    print("\nMost common cuisines:")
    print(frequencies.head(10).to_string(index=False))
    print("\nMost common exact cuisine combinations:")
    print(exact_report.head(10).to_string(index=False) if not exact_report.empty else "No combinations meet the frequency threshold.")
    print("\nCuisine pairs with the highest mean ratings (frequency threshold applied):")
    if pair_report.empty:
        print("No pairs meet the frequency threshold.")
    else:
        print(pair_report.sort_values(["mean_rating", "restaurant_count"], ascending=[False, False]).head(10).to_string(index=False))


if __name__ == "__main__":
    main()
