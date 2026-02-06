#!/usr/bin/env python3
"""
Debug script for subject search functionality
"""

import sys
import os
import re
from typing import Optional

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def _extract_subject_debug(q: str) -> Optional[str]:
    """Extract subject keywords from various patterns - with debug info"""
    import re
    
    print(f"Input query: '{q}'")
    
    # Look for explicit subject patterns
    patterns = [
        r'(?:subject|about|regarding|topic)[\s:-]+(.+?)(?:\s+case|\s+issue|$)',
        r'(?:find|search|show).*?(?:subject|about|regarding)[\s:-]+(.+?)(?:\s+case|\s+issue|$)',
        r'(?:case|cases).*?(?:subject|about|regarding)[\s:-]+(.+?)(?:\s+case|\s+issue|$)',
    ]
    
    for i, pattern in enumerate(patterns):
        match = re.search(pattern, q, re.I)
        print(f"Pattern {i+1}: {pattern}")
        if match:
            subject = match.group(1).strip()
            print(f"  Matched: '{subject}'")
            # Clean up common words that might be captured
            cleaned = re.sub(r'\b(?:case|cases|issue|issues|problem|problems)\b', '', subject, flags=re.I).strip()
            print(f"  After cleanup: '{cleaned}'")
            if len(cleaned) > 2:  # Only return if meaningful content
                return cleaned
        else:
            print(f"  No match")
    
    # If no explicit pattern, look for quoted strings or key phrases
    quoted_match = re.search(r'["\']([^"\']{3,})["\']', q)
    if quoted_match:
        result = quoted_match.group(1)
        print(f"Quoted match: '{result}'")
        return result
    
    # Look for keywords that might indicate subject content
    keywords = ['error', 'failed', 'issue', 'problem', 'bug', 'timeout', 'connection']
    matching_keywords = [word for word in keywords if word in q.lower()]
    print(f"Matching keywords: {matching_keywords}")
    
    if matching_keywords:
        # Extract the main content after removing common query words
        cleaned = re.sub(r'\b(?:show|find|search|get|case|cases|with|for|about|regarding)\b', '', q, flags=re.I)
        cleaned = cleaned.strip()
        print(f"After removing query words: '{cleaned}'")
        if len(cleaned) > 5:
            return cleaned
    
    print("No subject extracted")
    return None

def test_subject_extraction():
    """Test subject extraction with various inputs"""
    test_cases = [
        "Jira Connection is not working",
        "Show cases about Jira Connection is not working",
        "Find cases regarding database timeout",
        "subject: login error",
        "Cases with subject connection timeout",
        "Search for 'payment processing error'",
        "Show cases with error 500",
        "Find timeout problem cases",
        "connection issue with API",
        "database connection failed",
    ]
    
    print("=== Subject Extraction Test ===")
    for test in test_cases:
        print(f"\n--- Testing: '{test}' ---")
        result = _extract_subject_debug(test)
        print(f"Final result: '{result}'\n")

if __name__ == "__main__":
    test_subject_extraction()