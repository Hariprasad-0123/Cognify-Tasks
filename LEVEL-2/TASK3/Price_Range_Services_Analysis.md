# Price Range vs. Online Delivery and Table Booking

## Question

Are higher-priced restaurants more likely to offer online delivery or table
booking?

## Result status

**Not yet measurable from the files provided.** The task folder contains no
restaurant dataset, and the other CSVs available in the project use unrelated
columns and sample records. Giving service rates or claiming a relationship
without the intended data would be unsupported.

The analysis is ready in [`analyze_services.py`](analyze_services.py). Run it
with the restaurant CSV containing `Price range`, `Has Online delivery`, and
`Has Table booking`; it will generate `price_range_services_report.md` with
availability rates for every price range and association measures for each
service.

## How to interpret the generated results

Higher Yes percentages at higher price bands would indicate that those
restaurants are more likely to offer the service in this dataset. Compare all
price bands because rates may not rise steadily. Chi-square and Cramér’s V
summarize association across bands; neither establishes that price causes
service availability.
