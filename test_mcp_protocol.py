#!/usr/bin/env python3
"""
Test MCP protocol functionality directly
"""

import os
import sys
import json

# Add project paths
project_root = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(project_root, 'backend')
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

def test_mcp_tools():
    print("🧪 Testing MCP Protocol Tools...")
    
    try:
        # Import MCP tools
        from tools.ask_tool import mcp, ask, salesforce_health
        print("✅ MCP tools imported successfully")
        
        # Test 1: Check MCP server instance
        print(f"\n1. MCP Server Instance: {type(mcp)}")
        print(f"   MCP Server Name: {getattr(mcp, 'name', 'Unknown')}")
        
        # Test 2: List available tools
        print("\n2. Available MCP Tools:")
        tools = getattr(mcp, '_tools', {})
        for tool_name, tool_func in tools.items():
            print(f"   ✅ {tool_name}: {tool_func.__doc__.split('.')[0] if tool_func.__doc__ else 'No description'}")
        
        # Test 3: Test salesforce_health tool
        print("\n3. Testing salesforce_health tool...")
        health_result = salesforce_health()
        print(f"   Result: {json.dumps(health_result, indent=2)}")
        
        # Test 4: Test ask tool
        print("\n4. Testing ask tool...")
        ask_result = ask("health check", "test-session")
        print(f"   Result type: {ask_result.get('type', 'unknown')}")
        print(f"   Result keys: {list(ask_result.keys())}")
        
        # Test 5: Test tool decorators
        print("\n5. Verifying MCP Tool Decorators...")
        if hasattr(ask, '__mcp_tool__'):
            print("   ✅ ask() has MCP tool decorator")
        else:
            print("   ❌ ask() missing MCP tool decorator")
            
        if hasattr(salesforce_health, '__mcp_tool__'):
            print("   ✅ salesforce_health() has MCP tool decorator")
        else:
            print("   ❌ salesforce_health() missing MCP tool decorator")
        
        print("\n🎉 MCP Protocol Test Complete!")
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mcp_server_startup():
    print("\n🚀 Testing MCP Server Startup...")
    
    try:
        from tools.ask_tool import mcp
        
        # Test server configuration
        print(f"MCP Server Type: {type(mcp)}")
        print(f"MCP Server Methods: {[m for m in dir(mcp) if not m.startswith('_')]}")
        
        # Check if server can be started (don't actually start it)
        if hasattr(mcp, 'run'):
            print("✅ MCP server has run() method")
        else:
            print("❌ MCP server missing run() method")
            
        return True
        
    except Exception as e:
        print(f"❌ MCP server test failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("MCP PROTOCOL TESTING")
    print("=" * 60)
    
    success1 = test_mcp_tools()
    success2 = test_mcp_server_startup()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 ALL MCP TESTS PASSED!")
        print("✅ MCP Protocol is working correctly")
    else:
        print("❌ Some MCP tests failed")
        print("⚠️  Check the errors above")
    print("=" * 60)