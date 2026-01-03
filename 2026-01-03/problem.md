# Daily SQL Challenge - 2026-01-03

## Question
You are given a table `transactions` that records customer purchases. Each row represents a single transaction.

**Table Schema:**
`transactions`
*   `transaction_id` (INT, PRIMARY KEY)
*   `customer_id` (INT)
*   `transaction_date` (DATE)
*   `amount` (DECIMAL(10, 2))

Your task is to write a SQL query that returns all original transaction columns along with two additional calculated columns:

1.  `days_since_previous_purchase`: The number of days between the current transaction's `transaction_date` and the customer's *immediately preceding* transaction's `transaction_date`. For a customer's very first purchase, this value should be `NULL`.
2.  `is_first_purchase`: A boolean indicator (e.g., 1 for true, 0 for false) that specifies if the current transaction is the customer's *first ever* purchase.

The final result set should be ordered by `customer_id` and then `transaction_date`.

## Explanation
This solution uses the `LAG()` window function to efficiently calculate the `days_since_previous_purchase` and `is_first_purchase` for each customer's transactions.

1.  **`LAG(transaction_date) OVER (PARTITION BY customer_id ORDER BY transaction_date)`**: This is the core of the solution.
    *   `PARTITION BY customer_id`: Divides the dataset into separate groups for each customer.
    *   `ORDER BY transaction_date`: Sorts the transactions within each customer's group chronologically.
    *   `LAG(transaction_date)`: For each row, it retrieves the `transaction_date` from the *previous* row within its respective `customer_id` partition, based on the `transaction_date` order. For the first transaction of any customer, `LAG()` will return `NULL`.

2.  **`days_since_previous_purchase`**:
    *   `DATEDIFF(transaction_date, LAG(...) )`: We calculate the difference in days between the current `transaction_date` and the `previous_transaction_date` obtained from `LAG()`. The `DATEDIFF` function's exact syntax can vary (e.g., MySQL uses `DATEDIFF(end_date, start_date)`, PostgreSQL uses `end_date - start_date`, SQL Server uses `DATEDIFF(day, start_date, end_date)`). The provided solution assumes a common `DATEDIFF(end_date, start_date)` format.
    *   When `LAG()` returns `NULL` (for the first purchase), `DATEDIFF` will also return `NULL`, correctly handling the requirement for the first purchase.

3.  **`is_first_purchase`**:
    *   `CASE WHEN LAG(...) IS NULL THEN 1 ELSE 0 END`: This `CASE` statement leverages the behavior of `LAG()`. If `LAG(transaction_date)` returns `NULL`, it means there was no preceding transaction for that customer, indicating it's their first purchase. In this scenario, `is_first_purchase` is set to `1`; otherwise, it's `0`.

Finally, the results are ordered by `customer_id` and `transaction_date` as requested.