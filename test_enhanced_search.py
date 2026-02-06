#!/usr/bin/env python3
"""
Test script for enhanced case search functionality
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_subject_extraction():
    """Test the enhanced subject extraction"""
    from agent.agent_core import _extract_subject
    
    print("=== Testing Enhanced Subject Extraction ===")
    
    test_cases = [
        "Jira connection SSO issue",
        "Get me the details for Jira connection SSO issue",
        "Show me cases about Jira Connection is not working", 
        "Find database timeout issues",
        "Can you please get me the details for API authentication failed",
        "I need to see the information about login error",
        "Please show me the case details for permission denied error",
        "Get the details about database connection failed",
        "Fetch me information regarding payment processing error",
        "Display cases for timeout problem",
    ]
    
    for test in test_cases:
        result = _extract_subject(test)
        print(f"'{test}' -> '{result}'")
        print()

if __name__ == "__main__":
    test_subject_extraction()