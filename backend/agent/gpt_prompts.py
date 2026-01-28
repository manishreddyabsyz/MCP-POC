"""
Data processing utilities for Salesforce case information.
No AI/LLM calls - just data structuring for ChatGPT consumption.
"""

from typing import Any, Dict, List, Optional


def prepare_case_data(case_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare raw Salesforce case data for ChatGPT analysis.
    Returns structured data without AI processing.
    """
    return {
        "case_number": case_info.get('CaseNumber'),
        "subject": case_info.get('Subject'),
        "description": case_info.get('Description'),
        "status": case_info.get('Status'),
        "priority": case_info.get('Priority'),
        "contact_name": (case_info.get('Contact') or {}).get('Name'),
        "created_date": case_info.get('CreatedDate'),
        "last_modified_date": case_info.get('LastModifiedDate'),
        "owner": case_info.get('Owner', {}).get('Name') if case_info.get('Owner') else None,
        "account": case_info.get('Account', {}).get('Name') if case_info.get('Account') else None,
        "thread": case_info.get('Thread'),
        "artifacts": case_info.get('Artifacts'),
        "raw_case_data": case_info  # Include full raw data for ChatGPT to analyze
    }


def prepare_followup_context(
    *,
    case_data: Dict[str, Any],
    conversation_history: List[Dict[str, str]],
    user_question: str,
) -> Dict[str, Any]:
    """
    Prepare context for ChatGPT to answer follow-up questions.
    Returns structured data without AI processing.
    """
    return {
        "case_context": case_data,
        "conversation_history": conversation_history,
        "current_question": user_question,
        "instructions": "Use the case context and conversation history to answer the user's question. If you need more information, ask specific follow-up questions."
    }


def prepare_knowledge_article_data(
    *,
    case_data: Dict[str, Any],
    conversation_history: List[Dict[str, str]],
    title_hint: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Prepare data for ChatGPT to generate a knowledge article.
    Returns structured data without AI processing.
    """
    return {
        "case_data": case_data,
        "conversation_history": conversation_history,
        "title_hint": title_hint,
        "instructions": "Create a knowledge article based on this case data and conversation. Include: title, problem statement, environment, symptoms, root cause, resolution steps, verification steps, and prevention notes."
    }

