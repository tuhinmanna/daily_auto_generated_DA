import collections

def analyze_user_operations(log_entries: list[dict]) -> dict[str, int]:
    """
    Analyzes a list of log entries to count distinct operations per user.

    Args:
        log_entries: A list of dictionaries, each representing a log entry.
                     Each entry has an 'operation' key and may have
                     'user_id', 'userID', or 'client_id'.

    Returns:
        A dictionary mapping standardized user IDs (or 'UNKNOWN_USER')
        to the count of distinct operations performed by that user.
    """
    user_operations = collections.defaultdict(set)
    possible_user_keys = ['user_id', 'userID', 'client_id']
    
    for entry in log_entries:
        # Determine the standardized user ID
        current_user_id = 'UNKNOWN_USER'
        for key in possible_user_keys:
            if key in entry:
                current_user_id = entry[key]
                break # Found a user ID, stop checking other keys
        
        # Add the operation to the set for the current user
        operation = entry.get('operation')
        if operation: # Ensure operation key exists and has a value
            user_operations[current_user_id].add(operation)
            
    # Convert the defaultdict of sets into a dictionary of counts
    result = {user: len(ops) for user, ops in user_operations.items()}
    return result