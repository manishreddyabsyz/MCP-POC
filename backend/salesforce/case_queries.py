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
    """Search for cases by subject keywords in Subject and Description fields with multiple strategies"""
    subject = subject.strip()
    safe_subject = subject.replace("'", "\\'")

    print(f"🔍 Searching for subject: '{subject}'")
    
    # Strategy 1: Exact phrase search
    query1 = f"""
        SELECT Id, CaseNumber, Subject, Description, Status, Priority, Contact.Name
        FROM Case
        WHERE Subject LIKE '%{safe_subject}%'
           OR Description LIKE '%{safe_subject}%'
        ORDER BY CreatedDate DESC
    """
    
    print(f"Query 1 (exact phrase): {query1}")
    result = sf.query(query1)
    print(f"Exact phrase search found: {len(result['records'])} records")
    
    if result["records"]:
        return result["records"]
    
    # Strategy 2: Individual word search if exact phrase fails
    words = [word.strip() for word in subject.split() if len(word.strip()) > 2]
    if len(words) > 1:
        print(f"Trying individual words: {words}")
        
        # Create conditions for each word
        word_conditions = []
        for word in words:
            safe_word = word.replace("'", "\\'")
            word_conditions.append(f"Subject LIKE '%{safe_word}%' OR Description LIKE '%{safe_word}%'")
        
        query2 = f"""
            SELECT Id, CaseNumber, Subject, Description, Status, Priority, Contact.Name
            FROM Case
            WHERE {' OR '.join(word_conditions)}
            ORDER BY CreatedDate DESC
        """
        
        print(f"Query 2 (individual words): {query2}")
        result2 = sf.query(query2)
        print(f"Individual words search found: {len(result2['records'])} records")
        
        if result2["records"]:
            return result2["records"]
    
    # Strategy 3: Use SOSL search as fallback
    try:
        print(f"Trying SOSL search for: '{subject}'")
        escaped_subject = subject.replace("'", "\\'")
        sosl_query = f"""
            FIND {{{escaped_subject}}}
            IN ALL FIELDS
            RETURNING Case(Id, CaseNumber, Subject, Description, Status, Priority, Contact.Name)
        """
        
        print(f"SOSL Query: {sosl_query}")
        sosl_result = sf.search(sosl_query)
        sosl_records = sosl_result.get("searchRecords", [])
        print(f"SOSL search found: {len(sosl_records)} records")
        
        if sosl_records:
            return sosl_records
            
    except Exception as e:
        print(f"SOSL search failed: {e}")
    
    print("No records found with any search strategy")
    return []

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
           