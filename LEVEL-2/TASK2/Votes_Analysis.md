# Votes Analysis

## Dataset

The analysis uses all **9,551 restaurants** in `Dataset .csv`. There are no missing values in `Votes` or `Aggregate rating`.

## Restaurants with the most and fewest votes

- **Highest:** Toit, Bangalore — **10,934 votes**, aggregate rating **4.8**.
- **Lowest:** **1,094 restaurants are tied at 0 votes**. This is not a single restaurant. Examples include The Chaiwalas (Faridabad), Fusion Food Corner (Faridabad), and Punjabi Rasoi (Faridabad). These zero-vote entries have an aggregate rating of 0 in the dataset, which denotes “Not rated.”

## Votes and rating relationship

Using the full dataset, the **Pearson correlation is 0.314**, indicating a modest positive linear relationship: restaurants with more votes tend to have higher ratings, but vote count alone does not closely predict a restaurant’s rating. The **Spearman rank correlation is 0.846**, showing a strong positive association in the ordering of votes and ratings.

The two measures differ because vote counts and ratings are not normally distributed, and many restaurants have zero votes or a zero (“Not rated”) rating. Among the **7,403 restaurants with both votes and a nonzero rating**, the Pearson correlation is **0.409** and Spearman correlation is **0.682**, still positive. Correlation describes association and does not establish that votes cause higher ratings.

## Conclusion

Toit has the highest vote count. The lowest count is zero and is shared by 1,094 restaurants. Overall, votes and ratings move in the same direction, with a modest linear relationship across all records and a stronger rank-based relationship.
