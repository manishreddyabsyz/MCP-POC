def route_query(query: str):
    q = query.lower()

    if "comment" in q:
        return "comments"
    if "history" in q:
        return "history"
    if "feed" in q:
        return "feed"
    if "status" in q:
        return "status"
    if "case" in q:
        return "case"
    return "search"
