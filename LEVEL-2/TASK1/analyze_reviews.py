#!/usr/bin/env python3
"""Analyze restaurant review text, sentiment keywords, length, and ratings.

Usage: python analyze_reviews.py reviews.csv [--output report.md]

CSV needs a review/text column and optionally a rating/score column. Column
names are detected automatically; override them with --review-column and
--rating-column where needed.
"""

from __future__ import annotations

import argparse
import csv
import math
import re
from collections import Counter
from pathlib import Path

STOPWORDS = set("""a about above after again against all am an and any are as at be because been before being below between both but by can did do does doing down during each few for from further had has have having he her here hers herself him himself his how i if in into is it its itself just me more most my myself no nor not of off on once only or other our ours ourselves out over own same she should so some such than that the their theirs them themselves then there these they this those through to too under until up very was we were what when where which while who whom why will with you your yours yourself yourselves""".split())

# Small transparent lexicon used as a fallback when ratings are unavailable.
POSITIVE = set("""amazing awesome best delicious excellent fantastic favorite fresh friendly good great happy love loved lovely perfect pleasant recommend tasty wonderful""".split())
NEGATIVE = set("""awful bad bland cold disappointing disgusting dislike hated horrible poor rude slow terrible worst""".split())
TOKEN_RE = re.compile(r"[a-z]+(?:'[a-z]+)?")


def normalize(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def find_column(headers: list[str], explicit: str | None, candidates: tuple[str, ...], required: bool) -> str | None:
    if explicit:
        for header in headers:
            if header.lower() == explicit.lower():
                return header
        raise ValueError(f"Column {explicit!r} was not found. Available columns: {', '.join(headers)}")
    normalized = {normalize(h): h for h in headers}
    for candidate in candidates:
        if candidate in normalized:
            return normalized[candidate]
    if required:
        raise ValueError(f"Could not detect a review column. Available columns: {', '.join(headers)}. Use --review-column.")
    return None


def correlation(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 2:
        return None
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    dx, dy = [x - mx for x in xs], [y - my for y in ys]
    denom = math.sqrt(sum(x*x for x in dx) * sum(y*y for y in dy))
    return sum(x*y for x, y in zip(dx, dy)) / denom if denom else None


def read_reviews(path: Path, review_column: str | None, rating_column: str | None):
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("CSV has no header row.")
        text_col = find_column(reader.fieldnames, review_column, ("review", "reviews", "text", "comment", "comments", "content"), True)
        rating_col = find_column(reader.fieldnames, rating_column, ("rating", "ratings", "score", "stars", "star"), False)
        rows = []
        skipped = 0
        for row in reader:
            text = (row.get(text_col) or "").strip()
            if not text:
                skipped += 1
                continue
            tokens = TOKEN_RE.findall(text.lower())
            rating = None
            if rating_col:
                try:
                    rating = float(row.get(rating_col, "").strip())
                except (AttributeError, ValueError):
                    pass
            rows.append({"text": text, "tokens": tokens, "length": len(tokens), "rating": rating})
    return rows, text_col, rating_col, skipped


def fmt(value: float | None, digits: int = 2) -> str:
    return "N/A" if value is None else f"{value:.{digits}f}"


def analyze(rows, rating_col: str | None, top: int):
    rated = [r for r in rows if r["rating"] is not None]
    # When ratings are available, use their midpoint to define positive/negative
    # (e.g. 1–5 stars => <=2 negative, >=4 positive). Otherwise use lexicon hits.
    if rated:
        low, high = min(r["rating"] for r in rated), max(r["rating"] for r in rated)
        midpoint = (low + high) / 2
        negative_reviews = [r for r in rated if r["rating"] < midpoint]
        positive_reviews = [r for r in rated if r["rating"] > midpoint]
        sentiment_method = f"rating midpoint ({midpoint:g}; ratings below are negative, above are positive)"
    else:
        positive_reviews = [r for r in rows if sum(w in POSITIVE for w in r["tokens"]) > sum(w in NEGATIVE for w in r["tokens"])]
        negative_reviews = [r for r in rows if sum(w in NEGATIVE for w in r["tokens"]) > sum(w in POSITIVE for w in r["tokens"])]
        sentiment_method = "built-in word lexicon (no usable ratings)"

    def keywords(group):
        counts = Counter(token for r in group for token in r["tokens"] if token not in STOPWORDS and len(token) > 1)
        return counts.most_common(top)

    lengths = [float(r["length"]) for r in rows]
    usable = [r for r in rated if r["rating"] is not None]
    corr = correlation([float(r["length"]) for r in usable], [r["rating"] for r in usable])
    return {
        "positive": keywords(positive_reviews), "negative": keywords(negative_reviews),
        "average": sum(lengths) / len(lengths), "median": sorted(lengths)[len(lengths)//2] if len(lengths) % 2 else sum(sorted(lengths)[len(lengths)//2-1:len(lengths)//2+1])/2,
        "corr": corr, "rated_count": len(usable), "positive_count": len(positive_reviews),
        "negative_count": len(negative_reviews), "sentiment_method": sentiment_method,
        "rating_average": sum(r["rating"] for r in usable) / len(usable) if usable else None,
        "length_by_rating": {rating: sum(r["length"] for r in usable if r["rating"] == rating) / sum(r["rating"] == rating for r in usable) for rating in sorted({r["rating"] for r in usable})},
    }


def make_report(result, count: int, skipped: int, rating_col: str | None, top: int) -> str:
    def table(items):
        return "\n".join(f"| {word} | {count} |" for word, count in items) or "| _No reviews in this group_ | 0 |"
    lines = ["# Restaurant Reviews Analysis", "", f"Analyzed **{count}** non-empty reviews; skipped **{skipped}** empty rows.", "",
             "## Common keywords", "", f"Groups were assigned using {result['sentiment_method']}.", "",
             "### Positive reviews", "", "| Keyword | Count |", "|---|---:|", table(result["positive"]), "",
             "### Negative reviews", "", "| Keyword | Count |", "|---|---:|", table(result["negative"]), "",
             "## Review length", "", f"- Average: **{result['average']:.2f} words**", f"- Median: **{result['median']:.2f} words**", "",
             "## Review length and rating", ""]
    if rating_col and result["rated_count"]:
        corr = result["corr"]
        if corr is None:
            interpretation = "Length and rating have no measurable linear correlation in these rows (one variable is constant)."
        elif abs(corr) < 0.1:
            interpretation = "The linear relationship is negligible."
        elif abs(corr) < 0.4:
            interpretation = "The linear relationship is weak."
        elif abs(corr) < 0.7:
            interpretation = "The linear relationship is moderate."
        else:
            interpretation = "The linear relationship is strong."
        direction = "positive" if corr is not None and corr > 0 else "negative" if corr is not None and corr < 0 else ""
        lines += [f"- Mean rating: **{fmt(result['rating_average'])}**", f"- Pearson correlation (word count vs. rating): **{fmt(corr, 3)}**", f"- Interpretation: {interpretation} " + (f"It is {direction}, so longer reviews tend to have {'higher' if direction == 'positive' else 'lower'} ratings." if direction else ""), "", "Average word count by rating:", "", "| Rating | Average words |", "|---:|---:|"]
        lines += [f"| {rating:g} | {avg:.2f} |" for rating, avg in result["length_by_rating"].items()]
    else:
        lines += ["No usable numeric rating column was found, so the relationship between length and rating could not be calculated."]
    lines += ["", "## Method and limits", "", f"Keywords are the top {top} individual words after lowercasing and removing common English stopwords. Counts are token occurrences, not number of reviews mentioning a word. The rating correlation is Pearson's r and describes linear association; it does not imply causation. If ratings are absent, sentiment grouping uses a small built-in lexicon and should be treated as a rough fallback.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path, help="Path to reviews CSV")
    parser.add_argument("--output", type=Path, default=Path("restaurant_reviews_report.md"), help="Markdown report path (default: restaurant_reviews_report.md)")
    parser.add_argument("--review-column", help="Review text column name")
    parser.add_argument("--rating-column", help="Rating column name; omit to auto-detect")
    parser.add_argument("--top", type=int, default=15, help="Number of keywords per sentiment group")
    args = parser.parse_args()
    if args.top < 1:
        parser.error("--top must be at least 1")
    rows, _, rating_col, skipped = read_reviews(args.csv, args.review_column, args.rating_column)
    if not rows:
        parser.error("No non-empty review text was found.")
    result = analyze(rows, rating_col, args.top)
    report = make_report(result, len(rows), skipped, rating_col, args.top)
    args.output.write_text(report, encoding="utf-8")
    print(report)
    print(f"\nSaved report to {args.output}")


if __name__ == "__main__":
    main()
