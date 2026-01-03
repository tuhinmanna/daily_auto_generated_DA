```python
import pandas as pd

def find_users_with_long_streaks(df: pd.DataFrame, N: int = 3) -> pd.Series:
    """
    Identifies unique user_ids who have had at least one streak of N or more
    consecutive days of activity.

    Args:
        df (pd.DataFrame): Input DataFrame with 'user_id' and 'activity_date' columns.
        N (int): Minimum number of consecutive days for a streak to qualify.

    Returns:
        pd.Series: A Series of unique user_ids with qualifying streaks.
    """
    # 1. Ensure 'activity_date' is in datetime format
    df['activity_date'] = pd.to_datetime(df['activity_date'])

    # 2. Sort by user and date, then drop duplicate dates for the same user
    #    (multiple activities on the same day count as one day of activity)
    df_cleaned = df.sort_values(by=['user_id', 'activity_date']).drop_duplicates(subset=['user_id', 'activity_date'])

    # 3. Calculate the difference in days between consecutive activity dates for each user
    df_cleaned['date_diff'] = df_cleaned.groupby('user_id')['activity_date'].diff().dt.days

    # 4. Identify the start of a new non-consecutive streak
    #    A new streak starts if date_diff is not 1 (or NaN for the first activity of a user)
    #    fillna(True) ensures the first activity of each user correctly marks a streak start.
    df_cleaned['is_streak_break'] = (df_cleaned['date_diff'] != 1).fillna(True)

    # 5. Create streak IDs within each user group
    #    Using cumsum on 'is_streak_break' assigns a unique ID to each consecutive streak
    df_cleaned['streak_id'] = df_cleaned.groupby('user_id')['is_streak_break'].cumsum()

    # 6. Count the length of each streak
    streak_lengths = df_cleaned.groupby(['user_id', 'streak_id']).size().reset_index(name='streak_length')

    # 7. Filter for streaks that meet or exceed the minimum length N
    long_streaks_users = streak_lengths[streak_lengths['streak_length'] >= N]

    # 8. Return the unique user_ids who have at least one qualifying streak
    return long_streaks_users['user_id'].unique()

# Example Usage:
data = {
    'user_id': ['A', 'A', 'A', 'A', 'A', 'A', 'B', 'B', 'B', 'B', 'C', 'C', 'D'],
    'activity_date': [
        '2023-01-01', '2023-01-02', '2023-01-03', '2023-01-05', '2023-01-06', '2023-01-07',
        '2023-01-01', '2023-01-03', '2023-01-04', '2023-01-05',
        '2023-01-01', '2023-01-02',
        '2023-01-10'
    ]
}
df = pd.DataFrame(data)

N = 3
result = find_users_with_long_streaks(df.copy(), N)
print(result)
```