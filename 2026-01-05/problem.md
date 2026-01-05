# Daily SQL Challenge - 2026-01-05

## Question
You are tasked with analyzing employee login data to identify work habits. Specifically, you need to find the longest consecutive streak of login days for each employee.

Assume you have a table called `EmployeeLogins` with the following schema:

```sql
CREATE TABLE EmployeeLogins (
    employee_id INT,
    login_date DATE
);
```

*   `employee_id`: An integer representing the unique ID of an employee.
*   `login_date`: A date representing a day an employee logged into the system. Assume there are no duplicate `login_date` entries for the same `employee_id`.

Your task is to write a SQL query that returns `employee_id` and the `longest_streak` (the maximum number of consecutive days an employee logged in).

**Example Data:**

```
INSERT INTO EmployeeLogins (employee_id, login_date) VALUES
(1, '2023-01-01'),
(1, '2023-01-02'),
(1, '2023-01-04'),
(1, '2023-01-05'),
(1, '2023-01-06'),
(2, '2023-01-10'),
(2, '2023-01-11'),
(3, '2023-02-01'),
(3, '2023-02-03'),
(3, '2023-02-04'),
(3, '2023-02-05');
```

**Expected Output:**

| employee_id | longest_streak |
|-------------|----------------|
| 1           | 3              |
| 2           | 2              |
| 3           | 3              |

## Explanation
This solution uses a common pattern for identifying "islands and gaps" or consecutive sequences in data, leveraging window functions and CTEs.

1.  **`RankedLogins` CTE**:
    *   It assigns a row number (`rn`) to each login date for every employee, ordered chronologically. This `rn` will increase by 1 for each subsequent login date for a given employee.

2.  **`StreakGroups` CTE**:
    *   This is the core of the solution. It calculates a `grouping_key` by subtracting the `rn` from the `login_date`.
    *   **How it works**: If `login_date` values are consecutive (e.g., '2023-01-01', '2023-01-02', '2023-01-03'), and their corresponding `rn` values are consecutive (1, 2, 3), then the result of `login_date - rn` will be constant for all dates within that consecutive sequence. For example:
        *   '2023-01-01' - 1 day = '2022-12-31'
        *   '2023-01-02' - 2 days = '2022-12-31'
        *   '2023-01-03' - 3 days = '2022-12-31'
    *   When there's a gap in `login_date` (e.g., from '2023-01-03' to '2023-01-05'), the `rn` continues to increment, but `login_date` jumps more. This causes `login_date - rn` to change, effectively creating a new `grouping_key` and thus delineating the start of a new streak.

3.  **`StreakLengths` CTE**:
    *   It groups the data by `employee_id` and the `grouping_key`.
    *   By counting the `login_date` occurrences within each group, it determines the length of each individual consecutive login streak.

4.  **Final SELECT Statement**:
    *   Finally, it groups the results by `employee_id` and finds the `MAX(current_streak_length)`. This gives the longest streak observed for each employee across all their identified login streaks.
    *   The `ORDER BY employee_id` is for presentation.