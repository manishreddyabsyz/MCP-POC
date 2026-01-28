#!/usr/bin/env python3
"""
Test case number vs case ID detection logic
"""

import os
import sys

# Add project paths
project_root = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(project_root, 'backend')
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

def test_case_detection():
    print("🧪 Testing Case Detection Logic...")
    
    try:
        from agent.agent_core import _extract_case_number, _extract_case_id, _extract_primary_token
        
        test_cases = [
            "Show me case 00001163",
            "case 00001163", 
            "00001163",
            "5005g00001ABCdEFA1",  # Valid 18-char Case ID
            "123456789",  # 9 chars - should be invalid Case ID
            "12345678",   # 8 chars - should be Case Number
        ]
        
        print("\nTesting extraction functions:")
        print("-" * 50)
        
        for test in test_cases:
            print(f"\nInput: '{test}'")
            
            case_number = _extract_case_number(test)
            case_id = _extract_case_id(test)
            primary_token = _extract_primary_token(test)
            
            print(f"  Case Number: {case_number}")
            print(f"  Case ID: {case_id}")
            print(f"  Primary Token: {primary_token}")
            
            if primary_token:
                length = len(primary_token)
                print(f"  Token Length: {length}")
                
                if length == 18:
                    print(f"  → Would be treated as: CASE ID")
                elif 9 <= length < 18:
                    print(f"  → Would be treated as: INVALID CASE ID (ask for clarification)")
                else:
                    print(f"  → Would be treated as: CASE NUMBER")
            else:
                print(f"  → No primary token found")
        
        print("\n" + "=" * 50)
        print("Testing the actual agent logic...")
        
        # Test the actual agent function
        from agent.agent_core import handle_user_query
        from agent.memory import MemoryStore
        
        memory = MemoryStore()
        
        result = handle_user_query(
            user_query="Show me case 00001163",
            session_id="test",
            memory=memory
        )
        
        print(f"\nAgent Response Type: {result.get('type')}")
        print(f"Agent Response Message: {result.get('message', 'No message')}")
        
        if result.get('type') == 'clarification':
            print("❌ Still asking for clarification - logic issue not fixed")
        else:
            print("✅ Logic working - should query Salesforce")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_case_detection()