#!/usr/bin/env python3
"""
Test script to verify SQL query formatting
"""

def test_query_formatting():
    """Test that SQL queries are formatted correctly"""
    
    # Simulate the same logic as in get_case_by_subject
    subject = "Jira connection SSO"
    safe_subject = subject.replace("'", "\\'")
    
    print(f"Original subject: '{subject}'")
    print(f"Safe subject: '{safe_subject}'")
    
    query1 = f"""
        SELECT Id, CaseNumber, Subject, Description, Status, Priority, Contact.Name
        FROM Case
        WHERE Subject LIKE '%{safe_subject}%'
           OR Description LIKE '%{safe_subject}%'
        ORDER BY CreatedDate DESC
        LIMIT 10
    """
    
    print(f"Formatted query:")
    print(query1)
    
    # Test with a subject that has quotes
    subject_with_quotes = "User's login issue"
    safe_subject_with_quotes = subject_with_quotes.replace("'", "\\'")
    
    print(f"\nTesting with quotes:")
    print(f"Original: '{subject_with_quotes}'")
    print(f"Safe: '{safe_subject_with_quotes}'")
    
    query2 = f"""
        SELECT Id, CaseNumber, Subject, Description, Status, Priority, Contact.Name
        FROM Case
        WHERE Subject LIKE '%{safe_subject_with_quotes}%'
           OR Description LIKE '%{safe_subject_with_quotes}%'
        ORDER BY CreatedDate DESC
        LIMIT 10
    """
    
    print(f"Query with escaped quotes:")
    print(query2)

if __name__ == "__main__":
    test_query_formatting()