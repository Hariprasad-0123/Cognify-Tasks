# Price Range vs. Online Delivery and Table Booking

This task checks whether restaurant price range is associated with availability
of online delivery and table booking.

## Run the analysis

The expected input is the Zomato restaurant CSV with columns `Price range`,
`Has Online delivery`, and `Has Table booking`:

```sh
python3 analyze_services.py "Dataset .csv"
```

The script writes `price_range_services_report.md` in the current directory.
It reports service availability by price band, compares the lowest and highest
bands, and calculates chi-square and Cramér’s V for each service. It uses only
the Python standard library.

## Data availability

No source CSV is present in this task folder or among the available project
files. The nearby CSV files have different schemas and are unrelated sample
data, so they cannot support this analysis. Consequently, no numerical
findings are reported here. Add the intended restaurant CSV and run the command
above to generate evidence-based results; do not treat the template below as a
finding.
