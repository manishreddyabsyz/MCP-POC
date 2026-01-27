from salesforce.connection import sf


def get_case_with_id(case_id: str):
    # INTEGRATED: Used in agent_core.py _load_case_by_id()
    query = (
        "SELECT Id, CaseNumber, Subject, Description, Status, Priority, Contact.Name "
        f"FROM Case WHERE Id = '{case_id}' LIMIT 1"
    )
    return sf.query(query).get("records", [])


def get_case(case_number: str):
    # INTEGRATED: Used in agent_core.py _load_case_by_number()
    query = f"""
    SELECT Id, CaseNumber, Subject, Description, Status, Priority, Contact.Name
    FROM Case
    WHERE CaseNumber = '{case_number}'
    LIMIT 1
    """
    return sf.query(query)["records"]


def find_case(search_text: str):
    # INTEGRATED: Used in agent_core.py _search_cases()
    escaped = search_text.replace("'", "\\'")
    query = f"""
    FIND {{{escaped}}}
    IN ALL FIELDS
    RETURNING Case(Id, CaseNumber, Subject, Status, Description)
    """
    return sf.search(query).get("searchRecords", [])


def list_cases_by_status(statuses: list[str], limit: int = 20):
    # INTEGRATED: Used in agent_core.py for "in progress" case queries
    if not statuses:
        return []
    escaped_statuses = [s.replace("'", "\\'") for s in statuses]
    status_list = ",".join([f"'{s}'" for s in escaped_statuses])
    query = f"""
    SELECT Id, CaseNumber, Subject, Status, Priority, LastModifiedDate
    FROM Case
    WHERE Status IN ({status_list})
    ORDER BY LastModifiedDate DESC
    LIMIT {int(limit)}
    """
    return sf.query(query).get("records", [])


def get_case_comments(case_id: str):
    # INTEGRATED: Used in agent_core.py _load_case_comments()
    print("case comments")
    query = f"""
    SELECT CommentBody, CreatedDate, CreatedBy.Name
    FROM CaseComment
    WHERE ParentId = '{case_id}'
    ORDER BY CreatedDate DESC
    """
    return sf.query(query)["records"]


def get_case_history(case_id: str):
    # INTEGRATED: Used in agent_core.py _load_case_history()
    query = f"""
    SELECT Field, OldValue, NewValue, CreatedDate, CreatedBy.Name
    FROM CaseHistory
    WHERE CaseId = '{case_id}'
    ORDER BY CreatedDate DESC
    LIMIT 20
    """
    return sf.query(query)["records"]


def get_case_feed(case_id: str):
    # INTEGRATED: Used in agent_core.py _load_case_feed()
    query = f"""
    SELECT Body, Type, CreatedDate, CreatedBy.Name
    FROM CaseFeed
    WHERE ParentId = '{case_id}'
    ORDER BY CreatedDate DESC
    LIMIT 20
    """
    return sf.query(query)["records"]

