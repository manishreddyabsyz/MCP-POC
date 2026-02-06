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

def get_case_by_compliance(compliance_no: str):
    """Search for cases by compliance number in Subject and Description fields"""
    safe_compliance = compliance_no.replace("'", "\\'")
    query = f"""
        SELECT Id, CaseNumber, Subject, Description, Status, Priority, Contact.Name
        FROM Case
        WHERE Subject LIKE '%{safe_compliance}%'
           OR Description LIKE '%{safe_compliance}%'
        ORDER BY CreatedDate DESC
        LIMIT 10
    """
    return sf.query(query)["records"]

def get_case_by_subject(subject: str):
    subject = subject.strip()

    print(f"🔍 Searching with SOSL for: '{subject}'")

    # Escape single quotes for SOSL
    safe_subject = subject.replace("'", "\\'")

    # SOSL query: searches across all fields
    sosl_query = f"""
        FIND '{{{safe_subject}}}' IN ALL FIELDS
        RETURNING Case(
            Id, CaseNumber, Subject, Description, Status, Priority
            ORDER BY CreatedDate DESC
            LIMIT 10
        )
    """

    print("🔎 SOSL query:", sosl_query)

    result = sf.search(sosl_query)
    records = result.get("searchRecords", [])

    print("Matches found:", len(records))

    return records

def search_cases_by_keywords(keywords: str):
    """Enhanced search across multiple case fields"""
    safe_keywords = keywords.replace("'", "\\'")
    query = f"""
        SELECT Id, CaseNumber, Subject, Description, Status, Priority, Contact.Name
        FROM Case
        WHERE Subject LIKE '%{safe_keywords}%'
           OR Description LIKE '%{safe_keywords}%'
           OR CaseNumber LIKE '%{safe_keywords}%'
        ORDER BY LastModifiedDate DESC
    """
    return sf.query(query)["records"]
           