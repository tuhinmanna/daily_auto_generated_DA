```sql
WITH RankedLogins AS (
    SELECT
        employee_id,
        login_date,
        ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY login_date) AS rn
    FROM
        EmployeeLogins
),
StreakGroups AS (
    SELECT
        employee_id,
        login_date,
        -- Calculate a 'grouping_key'. For consecutive dates, login_date - rn will be constant.
        -- Example (assuming MySQL DATE_SUB for date arithmetic):
        -- If login_date = '2023-01-01', rn = 1 => '2023-01-01' - 1 day = '2022-12-31'
        -- If login_date = '2023-01-02', rn = 2 => '2023-01-02' - 2 days = '2022-12-31'
        -- If login_date = '2023-01-04', rn = 3 => '2023-01-04' - 3 days = '2023-01-01' (start of new streak)
        DATE_SUB(login_date, INTERVAL rn DAY) AS grouping_key
        -- Note: Date arithmetic syntax can vary by SQL dialect.
        -- PostgreSQL: login_date - (rn * INTERVAL '1 day')
        -- SQL Server: DATEADD(day, -rn, login_date)
    FROM
        RankedLogins
),
StreakLengths AS (
    SELECT
        employee_id,
        grouping_key,
        COUNT(login_date) AS current_streak_length
    FROM
        StreakGroups
    GROUP BY
        employee_id,
        grouping_key
)
SELECT
    employee_id,
    MAX(current_streak_length) AS longest_streak
FROM
    StreakLengths
GROUP BY
    employee_id
ORDER BY
    employee_id;
```