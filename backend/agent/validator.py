def validate_query(query: str):
    if not query or len(query.strip()) < 5:
        return False
    return True

