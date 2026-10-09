import pandas as pd
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent / "data" / "restaurants.csv"
REPORT_PATH = Path(__file__).resolve().parent / "restaurant_chains_report.md"

CHAIN_NAME_ALIASES = {
    "mcdonald's": "McDonald's",
    "mcdonalds": "McDonald's",
    "starbucks": "Starbucks",
    "subway": "Subway",
    "pizza hut": "Pizza Hut",
    "domino's": "Domino's",
    "dominos": "Domino's",
    "kfc": "KFC",
    "burger king": "Burger King",
    "dunkin'": "Dunkin'",
    "dunkin": "Dunkin'",
    "taco bell": "Taco Bell",
    "cafe coffee day": "Café Coffee Day",
    "cafecoffee day": "Café Coffee Day",
    "cafe coffee": "Café Coffee Day",
}


def normalize_chain_name(name: str) -> str:
    cleaned = str(name).strip().lower()
    cleaned = cleaned.replace("&", " and ")
    cleaned = " ".join(cleaned.split())
    for key, value in CHAIN_NAME_ALIASES.items():
        if cleaned == key or key in cleaned:
            return value
    return str(name).strip()


def load_data():
    file_path = DATA_PATH
    if not file_path.exists():
        raise FileNotFoundError(f"Dataset not found: {file_path}")
    df = pd.read_csv(file_path)
    required = {"restaurant_name", "city", "rating", "review_count", "popularity_score"}
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    return df


def detect_chains(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["chain_name"] = df["restaurant_name"].apply(normalize_chain_name)

    chain_summary = (
        df.groupby("chain_name", as_index=False)
        .agg(
            outlets=("restaurant_name", "count"),
            avg_rating=("rating", "mean"),
            avg_popularity=("popularity_score", "mean"),
            total_reviews=("review_count", "sum"),
            cities=("city", lambda s: ", ".join(sorted(s.unique())))
        )
        .sort_values(["avg_popularity", "avg_rating"], ascending=False)
        .reset_index(drop=True)
    )

    return chain_summary


def build_report(chain_summary: pd.DataFrame) -> str:
    top_chain = chain_summary.iloc[0]
    avg_rating_overall = chain_summary["avg_rating"].mean()
    avg_popularity_overall = chain_summary["avg_popularity"].mean()

    lines = [
        "# Restaurant Chains Analysis",
        "",
        "## Summary",
        f"There are {len(chain_summary)} distinct restaurant chains present in the dataset.",
        f"The top-performing chain by popularity is {top_chain['chain_name']} with an average popularity score of {top_chain['avg_popularity']:.2f} and an average rating of {top_chain['avg_rating']:.2f}.",
        f"Overall average rating across chains: {avg_rating_overall:.2f}",
        f"Overall average popularity score across chains: {avg_popularity_overall:.2f}",
        "",
        "## Chain-by-chain comparison",
        "",
        "| Chain | Outlets | Avg Rating | Avg Popularity | Total Reviews | Cities |",
        "|---|---:|---:|---:|---:|---|",
    ]

    for row in chain_summary.itertuples(index=False):
        lines.append(
            f"| {row.chain_name} | {row.outlets} | {row.avg_rating:.2f} | {row.avg_popularity:.2f} | {row.total_reviews} | {row.cities} |"
        )

    lines.extend([
        "",
        "## Interpretation",
        "- Chains with a higher average popularity score generally attract more visits and stronger brand recognition.",
        "- High-rated chains with strong review volume indicate better customer satisfaction and scale.",
        "- Popularity is strongly related to both brand visibility and outlet count across markets.",
    ])

    return "\n".join(lines)


def main():
    df = load_data()
    chain_summary = detect_chains(df)
    print("Restaurant chain analysis")
    print(chain_summary.to_string(index=False))
    report = build_report(chain_summary)
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"\nReport saved to: {REPORT_PATH}")


if __name__ == "__main__":
    main()
