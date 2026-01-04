# Daily Python Challenge - 2026-01-04

## Question
You are a Senior Data Analyst tasked with processing raw log entries to gain insights into user behavior. The log entries are provided as a list of dictionaries, where each dictionary represents a single event.

A common issue with these logs is that the key for identifying a user can vary. It might be `user_id`, `userID`, or `client_id`. If none of these keys are present, the user should be categorized as `UNKNOWN_USER`. Additionally, each log entry is guaranteed to have an `operation` key.

Your task is to write a Python function that processes this list of log entries and returns a dictionary. This dictionary should map each *standardized* user ID (or `UNKNOWN_USER`) to the *count of distinct operations* they performed.

**Input:** A list of dictionaries, `log_entries`. Each dictionary has an `operation` key and may have one of `user_id`, `userID`, or `client_id`.

**Example Input:**
```python
log_entries = [
    {'event_id': 'e1', 'user_id': 'user_A', 'operation': 'login'},
    {'event_id': 'e2', 'userID': 'user_A', 'operation': 'view_product'},
    {'event_id': 'e3', 'client_id': 'user_B', 'operation': 'login'},
    {'event_id': 'e4', 'user_id': 'user_C', 'operation': 'add_to_cart'},
    {'event_id': 'e5', 'user_id': 'user_A', 'operation': 'login'}, # 'login' is a duplicate operation for user_A
    {'event_id': 'e6', 'userID': 'user_B', 'operation': 'view_product'},
    {'event_id': 'e7', 'operation': 'system_event'}, # No user ID
    {'event_id': 'e8', 'user_id': 'user_C', 'operation': 'checkout'},
    {'event_id': 'e9', 'client_id': 'user_A', 'operation': 'logout'}
]
```

**Expected Output for the example input:**
```
{
    'user_A': 3,  # Distinct operations: 'login', 'view_product', 'logout'
    'user_B': 2,  # Distinct operations: 'login', 'view_product'
    'user_C': 2,  # Distinct operations: 'add_to_cart', 'checkout'
    'UNKNOWN_USER': 1 # Distinct operation: 'system_event'
}
```

## Explanation
The solution uses a `collections.defaultdict(set)` to efficiently group and count distinct operations.

1.  **Initialization**: `user_operations = collections.defaultdict(set)` creates a dictionary where if you try to access a key that doesn't exist, it automatically initializes its value as an empty set. This is perfect for collecting unique operations for each user.
2.  **User ID Standardization**: It iterates through each `entry` in `log_entries`. For each entry, it attempts to find a user ID by checking a predefined list of `possible_user_keys` (`'user_id'`, `'userID'`, `'client_id'`). The first key found determines the `current_user_id`. If none are found, `current_user_id` remains `'UNKNOWN_USER'`.
3.  **Collecting Distinct Operations**: The `operation` for the current entry is retrieved using `entry.get('operation')` for safe access. If an operation is found, it's added to the set associated with the `current_user_id` in `user_operations`. Sets automatically handle duplicates, ensuring that only distinct operations are stored.
4.  **Final Count**: After processing all log entries, a dictionary comprehension `{user: len(ops) for user, ops in user_operations.items()}` is used to iterate through the `user_operations` defaultdict. For each user, it takes the length of their set of operations, which gives the count of distinct operations, and stores it in the `result` dictionary.