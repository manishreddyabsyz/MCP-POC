from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

from agent.data_processing import (
    prepare_case_data,
    prepare_followup_context,
    prepare_knowledge_article_data,
)
from agent.memory import MemoryStore


_CASE_NUMBER_RE = re.compile(r"\b\d+\b")
# Typical Salesforce Case Ids start with '500' and must be 18 characters long
_CASE_ID_RE = re.compile(r"\b500[0-9A-Za-z]{15}\b")


def _extract_case_number(text: str) -> Optional[str]:
    """
    Extract a numeric case number (like 00001159).
    """
    if not text:
        return None
    
    # Look for patterns like "case 00001159" or "CaseNumber = 00001159"
    case_num_pattern = re.search(r"(?:case|casenumber)\s*[=:]?\s*(\d+)", text, re.IGNORECASE)
    if case_num_pattern:
        return case_num_pattern.group(1)
    
    # Fallback: any standalone number (but be more specific)
    standalone_num = re.search(r"\b(\d{5,10})\b", text)
    if standalone_num:
        return standalone_num.group(1)
    
    return None


def _extract_case_id(text: str) -> Optional[str]:
    m = _CASE_ID_RE.search(text or "")
    return m.group(0) if m else None


def _extract_primary_token(text: str) -> Optional[str]:
    """
    Extract a 9–18 character alphanumeric token that could be a Case Id.
    Prioritize tokens that look like Salesforce IDs (start with numbers or specific patterns).
    """
    if not text:
        return None
    
    # First, try to find a proper Salesforce Case ID (starts with 500, 18 chars)
    case_id_match = _CASE_ID_RE.search(text)
    if case_id_match:
        return case_id_match.group(0)
    
    # Then, look for any 15-18 character alphanumeric token that looks like an ID
    # Must start with a number or contain mixed alphanumeric (not just letters)
    long_id_matches = re.findall(r"\b[A-Za-z0-9]{15,18}\b", text)
    for token in long_id_matches:
        # Skip pure alphabetic words (like 'troubleshooting')
        if not token.isalpha() and not token.lower() in ['salesforce', 'casenumber']:
            return token
    
    # Finally, look for 9-14 character tokens that look like IDs
    medium_token_matches = re.findall(r"\b[A-Za-z0-9]{9,14}\b", text)
    for token in medium_token_matches:
        # Skip common words and pure alphabetic tokens
        if (not token.isalpha() and 
            token.lower() not in ['salesforce', 'casenumber', 'case', 'troubleshooting']):
            return token
    
    return None


def _looks_like_confirmation(text: str) -> Optional[bool]:
    q = (text or "").strip().lower()
    if q in {"yes", "y", "confirm", "confirmed", "ok", "okay", "please do", "go ahead"}:
        return True
    if q in {"no", "n", "cancel", "stop", "don't", "do not"}:
        return False
    return None


def _clarification_payload(*, message: str, questions: List[str], session_id: str) -> Dict[str, Any]:
    return {"type": "clarification", "session_id": session_id, "message": message, "questions": questions}


def _case_response_payload(*, case: Dict[str, Any], case_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
    return {
        "type": "case_response",
        "session_id": session_id,
        "case_number": case.get("CaseNumber"),
        "case_data": case_data,
        "raw_case": case,
        "instructions": """Analyze this Salesforce case data and provide a structured response with these 4 sections. Answer the user's specific question while maintaining this structure:

1. Case Summarization & Contextualization
   - Brief overview of the case type and current state
   - Context about customer situation and case history
   - Address the user's specific question in context

2. Technical Case Summary
   - Issue Type: [Category/Area]
   - Fix Status: [Current status]
   - Validation Status: [Testing/verification state]
   - Current State: [What's happening now]
   - Closure Dependency: [What's needed for closure]

3. Troubleshooting / Resolution Recommendation Steps
   - List specific steps to resolve or progress the case
   - Include validation and verification steps
   - Mention any dependencies or prerequisites
   - Address any specific actions related to the user's query

4. Action
   - Clear next steps to take
   - Who should do what
   - Timeline considerations
   - Specific actions related to the user's question

IMPORTANT: Always answer the user's specific question within this 4-section structure. If they asked for status, emphasize status information. If they asked for comments, include comment analysis. The structure should enhance, not replace, the direct answer to their query.

Format your response with clear section headers and structured information."""
    }


def _technical_followup_payload(*, case_data: Dict[str, Any], session_id: str, user_question: str) -> Dict[str, Any]:
    return {
        "type": "technical_followup",
        "session_id": session_id,
        "case_data": case_data,
        "user_question": user_question,
        "instructions": """This is a follow-up on an existing technical case. Structure your response with these 4 sections:

1. Case Summarization & Contextualization
   - Summarize the ongoing technical case and current status
   - Contextualize the customer's follow-up question
   - Reference any previous work done

2. Technical Case Summary
   - Issue Type: [Firmware/SDK/Runtime/etc.]
   - Fix Status: [Implemented/In Progress/Pending/etc.]
   - Validation Status: [Testing Complete/In Progress/Pending/etc.]
   - Current State: [Monitoring/Closed/Open/etc.]
   - Closure Dependency: [What's needed before case closure]

3. Troubleshooting / Resolution Recommendation Steps
   - Review previously implemented changes
   - Verify testing results and current status
   - List steps to confirm resolution or next actions
   - Include any monitoring or validation steps

4. Action
   - Immediate next steps required
   - Who should take action and when
   - Communication plan for case closure
   - Timeline considerations

Always include a knowledge article prompt at the end: 'This resolved technical issue can be reused as a reference. Would you like to convert this solution into a Knowledge Article for future cases?'"""
    }


def _followup_answer_payload(
    *, context_data: Dict[str, Any], session_id: str, stored: bool, new_qa: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    payload = {
        "type": "followup_answer",
        "session_id": session_id,
        "context_data": context_data,
        "stored_as_conversation": stored,
        "instructions": """Use the case context and conversation history to answer the user's question. For technical follow-up cases, structure your response with these 4 sections:

1. Case Summarization & Contextualization
   - Current case status and what has been done
   - Customer's specific follow-up question context

2. Technical Case Summary
   - Issue Type: [Category/Area]
   - Fix Status: [What's been implemented]
   - Validation Status: [Testing/monitoring state]
   - Current State: [Current situation]
   - Closure Dependency: [What's needed for closure]

3. Troubleshooting / Resolution Recommendation Steps
   - Review what has been done
   - Verify current status
   - Confirm next steps needed

4. Action
   - Immediate next steps
   - Timeline for completion
   - Communication plan

If you need more information, ask specific follow-up questions."""
    }
    if new_qa:
        payload["new_qa_pair"] = new_qa
    return payload


def _knowledge_article_payload(*, article_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
    return {
        "type": "knowledge_article", 
        "session_id": session_id, 
        "article_data": article_data,
        "instructions": "Create a knowledge article based on this case data and conversation. Include: title, problem statement, environment, symptoms, root cause, resolution steps, verification steps, and prevention notes."
    }


def _load_case_by_number(case_number: str) -> Tuple[Optional[Dict[str, Any]], str, Optional[str]]:
    try:
        from salesforce import case_queries  # lazy import

        sf_cases = case_queries.get_case(case_number)
        if sf_cases:
            return sf_cases[0], "salesforce", None
        # Explicitly indicate that Salesforce returned no rows
        return None, "salesforce_empty", None
    except Exception as e:
        # Signal that the Salesforce query itself failed (auth, network, etc.)
        return None, "salesforce_error", f"{type(e).__name__}: {e}"


def _load_case_by_id(case_id: str) -> Tuple[Optional[Dict[str, Any]], str, Optional[str]]:
    try:
        from salesforce import case_queries  # lazy import

        sf_cases = case_queries.get_case_with_id(case_id)
        if sf_cases:
            return sf_cases[0], "salesforce", None
        return None, "salesforce_empty", None
    except Exception as e:
        return None, "salesforce_error", f"{type(e).__name__}: {e}"


def _load_case_comments(case_id: str) -> Tuple[List[Dict[str, Any]], str, Optional[str]]:
    try:
        from salesforce import case_queries  # lazy import

        records = case_queries.get_case_comments(case_id)
        print(records,"records")
        return records or [], "salesforce", None
    except Exception as e:
        return [], "salesforce_error", f"{type(e).__name__}: {e}"


def _load_case_history(case_id: str) -> Tuple[List[Dict[str, Any]], str, Optional[str]]:
    try:
        from salesforce import case_queries  # lazy import

        records = case_queries.get_case_history(case_id)
        return records or [], "salesforce", None
    except Exception as e:
        return [], "salesforce_error", f"{type(e).__name__}: {e}"


def _load_case_feed(case_id: str) -> Tuple[List[Dict[str, Any]], str, Optional[str]]:
    try:
        from salesforce import case_queries  # lazy import

        records = case_queries.get_case_feed(case_id)
        return records or [], "salesforce", None
    except Exception as e:
        return [], "salesforce_error", f"{type(e).__name__}: {e}"


def _search_cases(search_text: str) -> List[Dict[str, Any]]:
    try:
        from salesforce import case_queries  # lazy import

        return case_queries.find_case(search_text)
    except Exception:
        return []


def handle_user_query(*, user_query: str, session_id: str, memory: MemoryStore) -> Dict[str, Any]:
    state = memory.get(session_id)
    q = (user_query or "").strip()
    q_lower = q.lower()

    wants_status = "status" in q_lower and ("case" in q_lower or _extract_primary_token(q) is not None)
    wants_in_progress = ("in progress" in q_lower) or ("in-progress" in q_lower) or ("working" in q_lower)

    if state.pending_knowledge_article is not None:
        conf = _looks_like_confirmation(q)
        if conf is True:
            article_data = prepare_knowledge_article_data(
                case_data=state.case_data or {},
                conversation_history=state.level2_qa,
                title_hint=(state.case_data or {}).get("subject"),
            )
            state.pending_knowledge_article = None
            return _knowledge_article_payload(article_data=article_data, session_id=session_id)
        if conf is False:
            state.pending_knowledge_article = None
            return {"type": "ok", "session_id": session_id, "message": "Okay—knowledge article creation cancelled."}
        return _clarification_payload(
            session_id=session_id,
            message="Do you want me to generate a knowledge article draft from the validated solution?",
            questions=["Reply 'confirm' to generate it, or 'cancel' to skip."],
        )

    if "knowledge article" in q_lower or "kb" in q_lower or "convert" in q_lower:
        if not state.level1_case_pack:
            return _clarification_payload(
                session_id=session_id,
                message="I can create a knowledge article after we summarize a case and validate the solution.",
                questions=[
                    "Share the CaseNumber from Salesforce.",
                    "Confirm the solution is validated, then I’ll convert it into a knowledge article.",
                ],
            )
        state.pending_knowledge_article = {"requested": True}
        return _clarification_payload(
            session_id=session_id,
            message="Before I create the knowledge article, please confirm the solution is validated.",
            questions=["Reply 'confirm' to generate the knowledge article draft, or 'cancel'."],
        )

    primary_token = _extract_primary_token(q)
    print(f"🔍 Case detection debug:")
    print(f"   Input query: '{q}'")
    print(f"   Primary token: '{primary_token}'")
    print(f"   Primary token length: {len(primary_token) if primary_token else 'None'}")

    # Business rule:
    # - If the primary token is 18 chars long, treat it as Case Id
    # - If it is between 9 and 17 characters and looks like an ID, it is probably an invalid Case Id
    #   → ask the user to enter the correct Case Id instead of treating it as a CaseNumber
    # - Otherwise, treat it as CaseNumber (no strict length limit)
    if primary_token:
        if len(primary_token) == 18:
            case_id = primary_token
            case_number = None
            print(f"   → Treating as Case ID: {case_id}")
        elif 9 <= len(primary_token) < 18:
            print(f"   → Invalid Case ID length, asking for clarification")
            return _clarification_payload(
                session_id=session_id,
                message="That looks like a Case Id but it is not 18 characters long. Please enter the correct 18-character Case Id, or provide the numeric CaseNumber instead.",
                questions=[
                    "Paste the full 18-character Salesforce Case Id.",
                    "Or share the CaseNumber from Salesforce.",
                ],
            )
        else:
            # This shouldn't happen with the updated _extract_primary_token, but fallback to case number
            case_id = None
            case_number = _extract_case_number(q)
            print(f"   → Unexpected primary token length, treating as Case Number: {case_number}")
    else:
        case_id = None
        case_number = _extract_case_number(q)
        print(f"   → No primary token, extracted case number: {case_number}")

    case: Dict[str, Any] | None
    source: str
    detail: Optional[str]
    print(case_number,"case number")
    if case_id:
        case, source, detail = _load_case_by_id(case_id)
    elif case_number:
        case, source, detail = _load_case_by_number(case_number)
    else:
        case, source, detail = None, "", None
    print(case_id,"caseid")
    if case_id or case_number:
        # Explicit "comments" request - use 4-section structure with comments focus
        if "comment" in q_lower:
            comments, source, detail = _load_case_comments(case_id or (case or {}).get("Id")) if (case_id or case) else ([], "", None)
            print(comments,"comments")
            if source == "salesforce_error":
                return {
                    "type": "error",
                    "session_id": session_id,
                    "error": "Salesforce query failed. Check SF credentials / connection.",
                    "case_id": case_id,
                    "case_number": case_number,
                    "detail": detail,
                }
            
            # Always use 4-section structure, even for comments
            case_data = prepare_case_data(case)
            state.case_data = case_data
            state.level2_qa = []
            
            payload = _case_response_payload(case=case, case_data=case_data, session_id=session_id)
            payload["case_source"] = source
            payload["comments"] = comments
            payload["query_focus"] = "Focus on analyzing the case comments in your response while maintaining the full 4-section structure. Include comment analysis in section 1 (contextualization) and relevant actions in section 4."
            return payload

        # Explicit "history" request - use 4-section structure with history focus
        if "history" in q_lower:
            history, source, detail = _load_case_history(case_id or (case or {}).get("Id")) if (case_id or case) else ([], "", None)
            if source == "salesforce_error":
                return {
                    "type": "error",
                    "session_id": session_id,
                    "error": "Salesforce query failed. Check SF credentials / connection.",
                    "case_id": case_id,
                    "case_number": case_number,
                    "detail": detail,
                }
            
            # Always use 4-section structure, even for history
            case_data = prepare_case_data(case)
            state.case_data = case_data
            state.level2_qa = []
            
            payload = _case_response_payload(case=case, case_data=case_data, session_id=session_id)
            payload["case_source"] = source
            payload["history"] = history
            payload["query_focus"] = "Focus on analyzing the case history and changes in your response while maintaining the full 4-section structure. Include history analysis in section 1 (contextualization) and track progress in section 2."
            return payload

        # Explicit "feed" request - use 4-section structure with feed focus
        if "feed" in q_lower:
            feed, source, detail = _load_case_feed(case_id or (case or {}).get("Id")) if (case_id or case) else ([], "", None)
            if source == "salesforce_error":
                return {
                    "type": "error",
                    "session_id": session_id,
                    "error": "Salesforce query failed. Check SF credentials / connection.",
                    "case_id": case_id,
                    "case_number": case_number,
                    "detail": detail,
                }
            
            # Always use 4-section structure, even for feed
            case_data = prepare_case_data(case)
            state.case_data = case_data
            state.level2_qa = []
            
            payload = _case_response_payload(case=case, case_data=case_data, session_id=session_id)
            payload["case_source"] = source
            payload["feed"] = feed
            payload["query_focus"] = "Focus on analyzing the case feed activities in your response while maintaining the full 4-section structure. Include feed activity analysis in section 1 (contextualization) and relevant insights in section 3."
            return payload

        if not case:
            if source == "salesforce_error":
                return {
                    "type": "error",
                    "session_id": session_id,
                    "error": "Salesforce query failed. Check SF credentials / connection.",
                    "case_id": case_id,
                    "case_number": case_number,
                    "detail": detail,
                }
            return {
                "type": "error",
                "session_id": session_id,
                "error": "Case not found in Salesforce",
                "case_id": case_id,
                "case_number": case_number,
            }

        # Always use 4-section structure for case queries, but customize the focus based on the question
        case_data = prepare_case_data(case)
        state.case_data = case_data
        state.level2_qa = []

        # Determine the specific focus of the query for customized instructions
        query_focus = ""
        if wants_status:
            query_focus = "Focus on providing current status information in section 2 (Technical Case Summary) while maintaining the full 4-section structure."
        
        payload = _case_response_payload(case=case, case_data=case_data, session_id=session_id)
        payload["case_source"] = source
        payload["query_focus"] = query_focus
        return payload

        case_data = prepare_case_data(case)
        state.case_data = case_data
        state.level2_qa = []

        payload = _case_response_payload(case=case, case_data=case_data, session_id=session_id)
        payload["case_source"] = source
        return payload

    if wants_in_progress and ("case" in q_lower or "cases" in q_lower):
        try:
            from salesforce import case_queries  # lazy import

            records = case_queries.list_cases_by_status(["Working", "In Progress"], limit=20)
            candidates = [
                {
                    "Id": r.get("Id"),
                    "CaseNumber": r.get("CaseNumber"),
                    "Subject": r.get("Subject"),
                    "Status": r.get("Status"),
                    "Priority": r.get("Priority"),
                    "LastModifiedDate": r.get("LastModifiedDate"),
                }
                for r in records
            ]
            return {
                "type": "in_progress_cases",
                "session_id": session_id,
                "count": len(candidates),
                "cases": candidates,
                "message": "Reply with a CaseNumber to summarize any of these cases.",
            }
        except Exception:
            pass

    if state.case_data:
        # Check if this is a technical follow-up case
        is_technical_followup = (
            "follow" in q_lower and ("up" in q_lower or "followup" in q_lower) or
            "status" in q_lower or "done" in q_lower or "resolved" in q_lower or
            "fix" in q_lower or "implementation" in q_lower or "changes" in q_lower or
            "monitoring" in q_lower or "closure" in q_lower or "complete" in q_lower
        )
        
        if is_technical_followup:
            # Use technical followup structure for follow-up questions
            new_qa = {"q": q, "a": ""}  # ChatGPT will provide the answer
            state.level2_qa.append(new_qa)
            return _technical_followup_payload(
                case_data=state.case_data, 
                session_id=session_id, 
                user_question=q
            )
        else:
            # Use regular followup for general questions
            context_data = prepare_followup_context(
                case_data=state.case_data,
                conversation_history=state.level2_qa,
                user_question=q,
            )
            
            new_qa = {"q": q, "a": ""}  # ChatGPT will provide the answer
            state.level2_qa.append(new_qa)
            return _followup_answer_payload(context_data=context_data, session_id=session_id, stored=True, new_qa=new_qa)

    hits = _search_cases(q) if len(q) >= 5 else []
    if hits:
        candidates = [
            {
                "Id": h.get("Id"),
                "CaseNumber": h.get("CaseNumber"),
                "Subject": h.get("Subject"),
                "Status": h.get("Status"),
                "Description": h.get("Description"),
            }
            for h in hits[:10]
        ]
        return {
            "type": "case_search_results",
            "session_id": session_id,
            "message": "I found matching cases. Reply with the CaseNumber you want me to summarize.",
            "candidates": candidates,
        }

    return _clarification_payload(
        session_id=session_id,
        message="I can help, but I need a case number or enough details to search.",
        questions=[
            "Share the CaseNumber (for example, 00001163).",
            "Or describe the issue (keywords like subject, error message, order/RO number, etc.) and I’ll search cases.",
        ],
    )

