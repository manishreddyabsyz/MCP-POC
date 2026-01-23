from salesforce.connection import sf
def get_case_with_id(case_id: str):
    query = f"SELECT Id, CaseNumber, Subject, Description, Status, Priority, Contact.Name FROM Case WHERE Id = '{case_id}' LIMIT 1"
    return sf.query(query).get("records", [])

def get_case(case_number: str):
    query = f"""
    SELECT Id, CaseNumber, Subject, Description, Status, Priority, Contact.Name
    FROM Case
    WHERE CaseNumber = '{case_number}'
    LIMIT 1
    """
    return sf.query(query)["records"]


def find_case(search_text: str):
    escaped = search_text.replace("'", "\\'")
    query = f"""
    FIND {{{escaped}}}
    IN ALL FIELDS
    RETURNING Case(Id, CaseNumber, Subject, Status, Description)
    """
    return sf.search(query).get("searchRecords", [])


def get_case_comments(case_id: str):
    query = f"""
    SELECT CommentBody, CreatedDate, CreatedBy.Name
    FROM CaseComment
    WHERE ParentId = '{case_id}'
    ORDER BY CreatedDate DESC
    """
    return sf.query(query)["records"]


def get_case_history(case_id: str):
    query = f"""
    SELECT Field, OldValue, NewValue, CreatedDate, CreatedBy.Name
    FROM CaseHistory
    WHERE CaseId = '{case_id}'
    ORDER BY CreatedDate DESC
    LIMIT 20
    """
    return sf.query(query)["records"]


def get_case_feed(case_id: str):
    query = f"""
    SELECT Body, Type, CreatedDate, CreatedBy.Name
    FROM CaseFeed
    WHERE ParentId = '{case_id}'
    ORDER BY CreatedDate DESC
    LIMIT 20
    """
    return sf.query(query)["records"]
