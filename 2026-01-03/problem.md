# Daily Python Pandas Challenge - 2026-01-03

## Question
You are given a Pandas DataFrame `df` representing user activity logs. Each row signifies that a `user_id` performed some activity on a specific `activity_date`.

Your task is to identify all unique `user_id`s who have had at least one streak of `N` or more *consecutive days* of activity. A consecutive day means the `activity_date` is exactly one day after the previous activity date for that user. If a user logs multiple activities on the same day, it still counts as a single day of activity.

**Input DataFrame Structure:**
```
import pandas as pd
data = {
    'user_id': ['A', 'A', 'A', 'A', 'A', 'A', 'B', 'B', 'B', 'B', 'C', 'C', 'D'],
    'activity_date': [
        '2023-01-01', '2023-01-02', '2023-01-03', '2023-01-05', '2023-01-06', '2023-01-07', # User A has 3-day and another 3-day streak
        '2023-01-01', '2023-01-03', '2023-01-04', '2023-01-05', # User B has a 3-day streak
        '2023-01-01', '2023-01-02', # User C has a 2-day streak
        '2023-01-10' # User D has a 1-day streak
    ]
}
df = pd.DataFrame(data)
```

**Required Output:**
A Pandas Series or list containing the unique `user_id`s that meet the criteria.

For the example above, if `N=3`, the expected output should be `['A', 'B']`.

## Explanation
The solution involves several key Pandas operations to efficiently identify streaks of consecutive days.

1.  **Date Conversion and Cleaning**: The `activity_date` column is first converted to `datetime` objects for proper date calculations. Then, the DataFrame is sorted by `user_id` and `activity_date`, and duplicate entries for the same user on the same date are removed using `drop_duplicates()`. This ensures that multiple activities on a single day correctly count as one day of activity.

2.  **Calculate Day Differences**: For each user, the `diff()` method is applied to the `activity_date` column within `groupby('user_id')`. This calculates the time difference between each activity date and the previous one for that specific user. `.dt.days` extracts this difference in days.

3.  **Identify Streak Breaks**: A new column `is_streak_break` is created. It's `True` if the `date_diff` is *not* `1` (meaning the activity is not on the very next day) or if it's `NaN` (which occurs for the first activity of each user). This column effectively marks the beginning of a potential new streak or the end of a previous one. `fillna(True)` handles the `NaN` values for the first entry of each group, correctly treating them as the start of a new streak.

4.  **Assign Streak IDs**: The `is_streak_break` column is then used with `cumsum()` (cumulative sum) within each `user_id` group. Each time `is_streak_break` is `True`, the cumulative sum increments, effectively assigning a unique `streak_id` to each continuous sequence of activities for a user.

5.  **Calculate Streak Lengths**: The DataFrame is then grouped by `user_id` and `streak_id`, and `size()` is used to count the number of activities (days) within each unique streak. This gives the length of each streak.

6.  **Filter and Extract Users**: Finally, the `streak_lengths` DataFrame is filtered to include only those streaks whose `streak_length` is greater than or equal to `N`. The `user_id`s from these qualifying streaks are then extracted using `unique()` to get the distinct set of users.