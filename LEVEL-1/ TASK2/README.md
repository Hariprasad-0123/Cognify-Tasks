# Cuisine Combination Analysis

This script finds the most common cuisines and cuisine combinations in a
restaurant CSV, then compares ratings for those combinations.

## Run

Install pandas if needed, then run:

```sh
python -m pip install pandas
python cuisine_combinations.py path/to/restaurants.csv
```

It automatically recognizes common column names such as `Cuisines` and
`Aggregate rating`. For other names, specify them:

```sh
python cuisine_combinations.py restaurants.csv \
  --cuisines-column cuisine_list --rating-column score
```

By default, combinations must occur in at least five restaurants. Change that
threshold with `--min-restaurants N`. Results are saved in a
`cuisine_analysis/` directory next to the input CSV; use `--output-dir` to
choose another location.

## Output files

- `cuisine_frequencies.csv`: restaurant count for each cuisine.
- `exact_cuisine_combinations.csv`: counts and mean/median ratings for each
  complete cuisine list (for example, `Indian + Chinese`).
- `cuisine_pair_ratings.csv`: counts and mean/median ratings for each pair,
  including restaurants that offer additional cuisines.

Rating summaries exclude missing, nonnumeric, and non-positive values. Zero is
treated as unrated, as in the common Zomato dataset. The pair report is sorted
by frequency in its CSV; the command line also displays the highest-rated
pairs that meet the frequency threshold. Ratings are descriptive averages and
should be read alongside `rated_restaurant_count`.
