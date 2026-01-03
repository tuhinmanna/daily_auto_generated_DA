```sql
SELECT
    transaction_id,
    customer_id,
    transaction_date,
    amount,
    -- Calculate days since previous purchase using LAG
    -- DATEDIFF syntax might vary by SQL dialect (e.g., MySQL: DATEDIFF(date1, date2), PostgreSQL: date1 - date2, SQL Server: DATEDIFF(day, date2, date1))
    -- Assuming a common DATEDIFF(end_date, start_date) for simplicity in this solution.
    DATEDIFF(transaction_date, LAG(transaction_date) OVER (PARTITION BY customer_id ORDER BY transaction_date)) AS days_since_previous_purchase,
    -- Identify first purchase using LAG result
    CASE
        WHEN LAG(transaction_date) OVER (PARTITION BY customer_id ORDER BY transaction_date) IS NULL THEN 1
        ELSE 0
    END AS is_first_purchase
FROM
    transactions
ORDER BY
    customer_id,
    transaction_date;
```