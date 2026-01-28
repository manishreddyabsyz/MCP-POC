from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

from agent.gpt_prompts import (
    gpt_answer_followup_grounded,
    gpt_generate_case_pack,
    gpt_generate_knowledge_article,
)
from agent.memory import MemoryStore


_CASE_NUMBER_RE = re.compile(r"\b\d+\b")
# Typical Salesforce Case Ids start with '500' and must be 18 characters long
_CASE_ID_RE = re.compile(r"\b500[0-9A-Za-z]{15}\b")


def _extract_case_number(text: str) -> Optional[str]:
    m = _CASE_NUMBER_RE.search(text or "")
    return m.group(0) if m else None


def _extract_case_id(text: str) -> Optional[str]:
    m = _CASE_ID_RE.search(text or "")
    return m.group(0) if m else None


def _extract_primary_token(text: str) -> Optional[str]:
    """
    Extract a 9–18 character alphanumeric token that could be a Case Id.
    """
    m = re.search(r"\b[A-Za-z0-9]{9,18}\b", text or "")
    return m.group(0) if m else None


def _looks_like_confirmation(text: str) -> Optional[bool]:
    q = (text or "").strip().lower()
    if q in {"yes", "y", "confirm", "confirmed", "ok", "okay", "please do", "go ahead"}:
        return True
    if q in {"no", "n", "cancel", "stop", "don't", "do not"}:
        return False
    return None


def _clarification_payload(*, message: str, questions: List[str], session_id: str) -> Dict[str, Any]:
    return {"type": "clarification", "session_id": session_id, "message": message, "questions": questions}


def _case_response_payload(*, case: Dict[str, Any], pack: Dict[str, Any], session_id: str) -> Dict[str, Any]:
    return {
        "type": "case_response",
        "session_id": session_id,
        "case_number": case.get("CaseNumber"),
        "case_type": pack.get("case_type"),
        "case_summary": pack.get("case_summary"),
        "technical_summary": pack.get("technical_summary"),
        "troubleshooting_steps": pack.get("troubleshooting_steps"),
        "next_actions": pack.get("next_actions"),
        "assumptions_and_gaps": pack.get("assumptions_and_gaps"),
        "tree": pack.get("tree"),
        "level1_knowledge": {
            "case_summary": pack.get("case_summary"),
            "technical_summary": pack.get("technical_summary"),
            "troubleshooting_steps": pack.get("troubleshooting_steps"),
            "next_actions": pack.get("next_actions"),
        },
        "prompt_knowledge_article_confirmation": (
            "If the solution is validated, reply 'confirm' to generate a knowledge article draft."
        ),
    }


def _followup_answer_payload(
    *, grounded: Dict[str, Any], session_id: str, stored: bool, new_qa: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    payload = {
        "type": "followup_answer",
        "session_id": session_id,
        "needs_clarification": grounded.get("needs_clarification"),
        "answer": grounded.get("answer"),
        "follow_up_questions": grounded.get("follow_up_questions"),
        "citations": grounded.get("citations"),
        "stored_as_level2_knowledge": stored,
    }
    if new_qa:
        payload["new_level2_qa"] = new_qa
    return payload


def _knowledge_article_payload(*, article: Dict[str, Any], session_id: str) -> Dict[str, Any]:
    return {"type": "knowledge_article", "session_id": session_id, "article": article}


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
            article = gpt_generate_knowledge_article(
                level1_case_pack=state.level1_case_pack or {},
                level2_qa=state.level2_qa,
                title_hint=(state.level1_case_pack or {}).get("case_type"),
            )
            state.pending_knowledge_article = None
            return _knowledge_article_payload(article=article, session_id=session_id)
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
    # - If it is between 9 and 17 characters, it is probably an invalid Case Id
    #   → ask the user to enter the correct Case Id instead of treating it as a CaseNumber
    # - Otherwise, treat it as CaseNumber (no strict length limit)
    if primary_token:
        if len(primary_token) == 18:
            case_id = primary_token
            case_number = None
            print(f"   → Treating as Case ID: {case_id}")
        elif 9 <= len(primary_token) < 18:  # Fixed: was 8 < len, now 9 <=
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
            case_id = None
            case_number = _extract_case_number(q)
            print(f"   → Treating as Case Number: {case_number}")
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
        # Explicit "comments" request
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
            if not comments:
                return {
                    "type": "case_comments",
                    "session_id": session_id,
                    "case_id": case_id or (case or {}).get("Id"),
                    "case_number": case_number or (case or {}).get("CaseNumber"),
                    "comments": [],
                    "message": "No comments found for this case.",
                }
            return {
                "type": "case_comments",
                "session_id": session_id,
                "case_id": case_id or (case or {}).get("Id"),
                "case_number": case_number or (case or {}).get("CaseNumber"),
                "comments": comments,
                "message": "Here are the most recent case comments.",
            }

        # Explicit "history" request
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
            if not history:
                return {
                    "type": "case_history",
                    "session_id": session_id,
                    "case_id": case_id or (case or {}).get("Id"),
                    "case_number": case_number or (case or {}).get("CaseNumber"),
                    "history": [],
                    "message": "No history found for this case.",
                }
            return {
                "type": "case_history",
                "session_id": session_id,
                "case_id": case_id or (case or {}).get("Id"),
                "case_number": case_number or (case or {}).get("CaseNumber"),
                "history": history,
                "message": "Here are the most recent case history changes.",
            }

        # Explicit "feed" request
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
            if not feed:
                return {
                    "type": "case_feed",
                    "session_id": session_id,
                    "case_id": case_id or (case or {}).get("Id"),
                    "case_number": case_number or (case or {}).get("CaseNumber"),
                    "feed": [],
                    "message": "No feed activity found for this case.",
                }
            return {
                "type": "case_feed",
                "session_id": session_id,
                "case_id": case_id or (case or {}).get("Id"),
                "case_number": case_number or (case or {}).get("CaseNumber"),
                "feed": feed,
                "message": "Here are the most recent case feed activities.",
            }

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

        if wants_status and ("resolve" not in q_lower) and ("summary" not in q_lower):
            return {
                "type": "case_status",
                "session_id": session_id,
                "case_number": case.get("CaseNumber"),
                "status": case.get("Status"),
                "priority": case.get("Priority"),
                "subject": case.get("Subject"),
                "case_source": source,
            }

        pack = gpt_generate_case_pack(case)
        state.level1_case_pack = pack
        state.level1_case_summary = pack.get("case_summary")
        state.level2_qa = []

        payload = _case_response_payload(case=case, pack=pack, session_id=session_id)
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

    if state.level1_case_pack:
        grounded = gpt_answer_followup_grounded(
            level1_case_pack=state.level1_case_pack,
            level2_qa=state.level2_qa,
            user_question=q,
        )
        if grounded.get("needs_clarification"):
            return _followup_answer_payload(grounded=grounded, session_id=session_id, stored=False)

        new_qa = {"q": q, "a": grounded.get("answer", "")}
        state.level2_qa.append(new_qa)
        return _followup_answer_payload(grounded=grounded, session_id=session_id, stored=True, new_qa=new_qa)

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

