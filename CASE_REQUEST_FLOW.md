# Case Request Flow: Step-by-Step File Execution

## Scenario: User asks "Show me case 12345"

### Complete File Execution Path

```
User Input: "Show me case 12345"
↓
ChatGPT Custom GPT
↓
HTTP POST to Railway URL
↓
File Execution Chain (8 files involved)
```

---

## Step-by-Step File Flow

### **Step 1: HTTP Request Entry**
**File**: `backend/server.py`
**Function**: `ask_endpoint()`
**Line**: ~70

```python
@app.post("/ask")
async def ask_endpoint(request: dict):
    print(f"🔍 Ask endpoint called")
    print(f"   Raw request: {request}")
    
    # Extract parameters
    user_query = request.get("user_query", "")  # "Show me case 12345"
    session_id = request.get("session_id", "default")  # "chatgpt-user-123"
    
    # Call MCP tool
    result = ask(user_query, session_id)
    return result
```

**What happens**: 
- Receives HTTP POST from ChatGPT
- Extracts `user_query` and `session_id`
- Calls the MCP `ask()` function

---

### **Step 2: MCP Tool Execution**
**File**: `backend/tools/ask_tool.py`
**Function**: `ask()`
**Line**: ~12

```python
@mcp.tool()
def ask(user_query: str, session_id: str = "default"):
    # user_query = "Show me case 12345"
    # session_id = "chatgpt-user-123"
    
    return handle_user_query(
        user_query=user_query, 
        session_id=session_id, 
        memory=_memory
    )
```

**What happens**:
- MCP tool receives parameters
- Calls core business logic function
- Passes global memory store

---

### **Step 3: Core Query Processing**
**File**: `backend/agent/agent_core.py`
**Function**: `handle_user_query()`
**Line**: ~185

```python
def handle_user_query(*, user_query: str, session_id: str, memory: MemoryStore) -> Dict[str, Any]:
    # Get or create session state
    state = memory.get(session_id)  # Calls memory.py
    
    q = (user_query or "").strip()  # "Show me case 12345"
    q_lower = q.lower()             # "show me case 12345"
    
    # Extract case identifier
    primary_token = _extract_primary_token(q)  # Returns "12345"
```

**What happens**:
- Gets session state from memory store
- Normalizes query string
- Calls token extraction function

---

### **Step 4: Session State Management**
**File**: `backend/agent/memory.py`
**Function**: `MemoryStore.get()`
**Line**: ~18

```python
def get(self, session_id: str) -> SessionState:
    if not session_id:
        session_id = "default"
    if session_id not in self._sessions:
        # Create new session
        self._sessions[session_id] = SessionState(session_id=session_id)
    return self._sessions[session_id]
```

**What happens**:
- Checks if session exists
- Creates new SessionState if needed
- Returns session object

**Returns to**: `agent_core.py`

---

### **Step 5: Case Identifier Extraction**
**File**: `backend/agent/agent_core.py`
**Function**: `_extract_primary_token()`
**Line**: ~42

```python
def _extract_primary_token(text: str) -> Optional[str]:
    # text = "Show me case 12345"
    
    # First, try Salesforce Case ID (18 chars starting with 500)
    case_id_match = _CASE_ID_RE.search(text)  # No match
    
    # Then, look for 15-18 character tokens
    long_id_match = re.search(r"\b[A-Za-z0-9]{15,18}\b", text)  # No match
    
    # Finally, look for 9-14 character tokens
    medium_token_match = re.search(r"\b[A-Za-z0-9]{9,14}\b", text)  # No match
    
    # For "12345" - this will be caught by case number extraction
    return "12345"  # Extracted token
```

**What happens**:
- Tries multiple regex patterns
- Identifies "12345" as potential case identifier
- Returns the token

**Returns to**: `agent_core.py` main function

---

### **Step 6: Case Number vs Case ID Decision**
**File**: `backend/agent/agent_core.py`
**Function**: `handle_user_query()` (continued)
**Line**: ~240

```python
if primary_token:
    if len(primary_token) == 18:
        case_id = primary_token
        case_number = None
    elif 9 <= len(primary_token) < 18:
        # Invalid Case ID - ask for clarification
        return _clarification_payload(...)
    else:
        case_id = None
        case_number = _extract_case_number(q)  # Calls extraction function
```

**What happens**:
- Checks token length (5 characters for "12345")
- Since length < 9, treats as case number
- Calls case number extraction

---

### **Step 7: Case Number Extraction**
**File**: `backend/agent/agent_core.py`
**Function**: `_extract_case_number()`
**Line**: ~17

```python
def _extract_case_number(text: str) -> Optional[str]:
    # text = "Show me case 12345"
    
    # Look for patterns like "case 12345"
    case_num_pattern = re.search(r"(?:case|casenumber)\s*[=:]?\s*(\d+)", text, re.IGNORECASE)
    if case_num_pattern:
        return case_num_pattern.group(1)  # Returns "12345"
    
    # Fallback: standalone number
    standalone_num = re.search(r"\b(\d{5,10})\b", text)
    if standalone_num:
        return standalone_num.group(1)
    
    return None
```

**What happens**:
- Finds "case 12345" pattern
- Extracts "12345" as case number
- Returns the case number

**Returns to**: `agent_core.py` main function

---

### **Step 8: Salesforce Data Loading**
**File**: `backend/agent/agent_core.py`
**Function**: `_load_case_by_number()`
**Line**: ~120

```python
def _load_case_by_number(case_number: str) -> Tuple[Optional[Dict[str, Any]], str, Optional[str]]:
    try:
        from salesforce import case_queries  # Lazy import
        
        sf_cases = case_queries.get_case(case_number)  # Calls Salesforce module
        if sf_cases:
            return sf_cases[0], "salesforce", None
        return None, "salesforce_empty", None
    except Exception as e:
        return None, "salesforce_error", f"{type(e).__name__}: {e}"
```

**What happens**:
- Lazy imports Salesforce module
- Calls case query function
- Handles errors gracefully

---

### **Step 9: Salesforce Connection**
**File**: `backend/salesforce/connection.py`
**Line**: ~8

```python
from simple_salesforce import Salesforce

sf = Salesforce(
    username=os.getenv("SF_USERNAME"),
    password=os.getenv("SF_PASSWORD"),
    security_token=os.getenv("SF_SECURITY_TOKEN"),
    domain=os.getenv("SF_DOMAIN", "login")
)
```

**What happens**:
- Establishes Salesforce connection
- Uses environment variables
- Creates global `sf` object

---

### **Step 10: SOQL Query Execution**
**File**: `backend/salesforce/case_queries.py`
**Function**: `get_case()`
**Line**: ~12

```python
def get_case(case_number: str):
    # case_number = "12345"
    query = f"""
    SELECT Id, CaseNumber, Subject, Description, Status, Priority, Contact.Name
    FROM Case
    WHERE CaseNumber = '{case_number}'
    LIMIT 1
    """
    return sf.query(query)["records"]  # Uses connection from connection.py
```

**What happens**:
- Builds SOQL query with case number
- Executes query against Salesforce
- Returns case records array

**Returns to**: `agent_core.py` → `_load_case_by_number()`

---

### **Step 11: Data Preparation**
**File**: `backend/agent/agent_core.py`
**Function**: `handle_user_query()` (continued)
**Line**: ~398

```python
# case now contains Salesforce data
case_data = prepare_case_data(case)  # Calls data preparation
state.case_data = case_data          # Store in session
state.level2_qa = []                 # Initialize conversation history

payload = _case_response_payload(case=case, case_data=case_data, session_id=session_id)
```

**What happens**:
- Calls data preparation function
- Updates session state
- Creates response payload

---

### **Step 12: Data Structuring**
**File**: `backend/agent/gpt_prompts.py`
**Function**: `prepare_case_data()`
**Line**: ~8

```python
def prepare_case_data(case_info: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "case_number": case_info.get('CaseNumber'),      # "12345"
        "subject": case_info.get('Subject'),             # "Login Issues"
        "description": case_info.get('Description'),     # "User cannot..."
        "status": case_info.get('Status'),               # "Working"
        "priority": case_info.get('Priority'),           # "High"
        "contact_name": (case_info.get('Contact') or {}).get('Name'),
        "created_date": case_info.get('CreatedDate'),
        "last_modified_date": case_info.get('LastModifiedDate'),
        "raw_case_data": case_info  # Full Salesforce object
    }
```

**What happens**:
- Extracts key fields from Salesforce case
- Structures data for ChatGPT consumption
- Preserves raw data for flexibility

**Returns to**: `agent_core.py`

---

### **Step 13: Response Payload Creation**
**File**: `backend/agent/agent_core.py`
**Function**: `_case_response_payload()`
**Line**: ~85

```python
def _case_response_payload(*, case: Dict[str, Any], case_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
    return {
        "type": "case_response",
        "session_id": session_id,
        "case_number": case.get("CaseNumber"),
        "case_data": case_data,
        "raw_case": case,
        "instructions": "Analyze this Salesforce case data and provide: 1) Case summary, 2) Technical analysis, 3) Troubleshooting steps, 4) Next actions, 5) Any assumptions or information gaps. Ask follow-up questions if you need clarification."
    }
```

**What happens**:
- Creates structured response for ChatGPT
- Includes both processed and raw data
- Adds analysis instructions

**Returns to**: `agent_core.py` main function

---

### **Step 14: Response Chain Back**
**File**: `backend/agent/agent_core.py` → `backend/tools/ask_tool.py` → `backend/server.py`

```python
# agent_core.py returns payload
return payload

# ask_tool.py returns result
return handle_user_query(...)

# server.py returns HTTP response
return result
```

**What happens**:
- Response bubbles back through call stack
- Each layer passes data unchanged
- HTTP response sent to ChatGPT

---

## Complete File Execution Order

```
1. backend/server.py              (HTTP entry point)
2. backend/tools/ask_tool.py      (MCP tool)
3. backend/agent/agent_core.py    (Query processing)
4. backend/agent/memory.py        (Session management)
5. backend/agent/agent_core.py    (Token extraction)
6. backend/agent/agent_core.py    (Case number extraction)
7. backend/agent/agent_core.py    (Salesforce data loading)
8. backend/salesforce/connection.py (SF connection)
9. backend/salesforce/case_queries.py (SOQL query)
10. backend/agent/gpt_prompts.py  (Data preparation)
11. backend/agent/agent_core.py   (Response creation)
12. backend/tools/ask_tool.py     (Return to MCP)
13. backend/server.py             (HTTP response)
```

## Data Flow Summary

```
Input:  "Show me case 12345"
↓
Extract: "12345" (case number)
↓
Query:  SELECT * FROM Case WHERE CaseNumber = '12345'
↓
Result: Salesforce case object
↓
Process: Structure data for ChatGPT
↓
Output: JSON response with case data + instructions
```

## Key Decision Points

1. **Token Length Check** (`agent_core.py:240`):
   - 18 chars = Case ID
   - 9-17 chars = Invalid (ask clarification)
   - <9 chars = Case Number

2. **Query Type Detection** (`agent_core.py:300`):
   - "comments" → Load case comments
   - "history" → Load case history
   - "status" → Return status only
   - Default → Full case analysis

3. **Error Handling** (`agent_core.py:120`):
   - Salesforce connection failed
   - Case not found
   - Invalid case format

This shows exactly how your request flows through 8 different files to retrieve and process Salesforce case data!