# Restaurant Reviews

This project analyzes review text to find frequent words in positive and
negative reviews, calculate average and median review length, and measure the
relationship between review length and rating.

## Run

Use Python 3.10 or newer. No third-party packages are required.

```sh
python analyze_reviews.py path/to/reviews.csv
```

The CSV should have a header row with a review text column (`review`, `text`,
`comment`, or `content`) and, if available, a numeric rating column (`rating`,
`score`, or `stars`). The script also accepts explicit column names:

```sh
python analyze_reviews.py reviews.csv --review-column "Review Text" --rating-column "Overall Rating" --output report.md
```

The script prints the analysis and saves it to
`restaurant_reviews_report.md` by default. Positive and negative review groups
are based on ratings below/above the midpoint of the observed rating range.
When no usable rating values are present, a small built-in sentiment word list
is used as a rough fallback. Review length is measured in whitespace-like
word tokens (alphabetic words, with internal apostrophes retained). Rating
association is reported as Pearson's correlation and is descriptive, not
causal.

## Data

No review dataset was included in the task workspace. Provide the CSV when
running the script to generate actual keyword and length findings; no results
are invented in advance.
