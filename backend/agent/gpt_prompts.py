import json
import os
from typing import Any, Dict, List, Optional

import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def _extract_json_object(text: str) -> Dict[str, Any]:
    start = text.find("{")
    end = text.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError("No JSON object found in model output")
    return json.loads(text[start:end])


def _chat_json(
    *,
    model: str,
    system: str,
    user: str,
    schema: Optional[Dict[str, Any]] = None,
    temperature: float = 0.2,
) -> Dict[str, Any]:
    kwargs: Dict[str, Any] = {}
    if schema:
        kwargs["response_format"] = {"type": "json_schema", "json_schema": schema}
    response = openai.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=temperature,
        **kwargs,
    )
    content = response.choices[0].message.content or ""
    try:
        return json.loads(content)
    except Exception:
        return _extract_json_object(content)


def gpt_generate_case_pack(case_info: Dict[str, Any]) -> Dict[str, Any]:
    system = (
        "You are an expert technical support assistant.\n"
        "You must be precise, concise, and actionable.\n"
        "If information is missing, make assumptions explicit and propose what to collect.\n"
        "Return ONLY valid JSON matching the schema."
    )

    user = f"""
Create a structured support-case response.

CaseNumber: {case_info.get('CaseNumber')}
Subject: {case_info.get('Subject')}
Description: {case_info.get('Description')}
Status: {case_info.get('Status')}
Priority: {case_info.get('Priority')}
Contact: {(case_info.get('Contact') or {}).get('Name')}
Thread: {case_info.get('Thread')}
Artifacts: {case_info.get('Artifacts')}

Required capabilities (all must be present):
1) Case Summarization & Contextualization (main summary)
2) Separate Technical Case Summary (engineer-focused)
3) Troubleshooting Steps / Recommendations (distinct section)
4) Next Immediate Implementable Actions (distinct section)
5) Tree-based representation: start with crisp summary, then structured children for solution paths, next steps, deeper levels.
"""

    schema = {
        "name": "case_pack",
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "case_type": {"type": "string"},
                "case_summary": {"type": "string"},
                "technical_summary": {"type": "string"},
                "troubleshooting_steps": {"type": "array", "items": {"type": "string"}},
                "next_actions": {"type": "array", "items": {"type": "string"}},
                "assumptions_and_gaps": {"type": "array", "items": {"type": "string"}},
                "tree": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "title": {"type": "string"},
                        "content": {"type": "string"},
                        "children": {"type": "array", "items": {"type": "object"}},
                    },
                    "required": ["title", "content", "children"],
                },
            },
            "required": [
                "case_type",
                "case_summary",
                "technical_summary",
                "troubleshooting_steps",
                "next_actions",
                "assumptions_and_gaps",
                "tree",
            ],
        },
    }

    return _chat_json(model="gpt-4o", system=system, user=user, schema=schema, temperature=0.2)


def gpt_answer_followup_grounded(
    *,
    level1_case_pack: Dict[str, Any],
    level2_qa: List[Dict[str, str]],
    user_question: str,
) -> Dict[str, Any]:
    system = (
        "You are a support assistant constrained to the provided knowledge.\n"
        "GROUNDING RULES (mandatory):\n"
        "- Level-1 knowledge = the provided case_pack JSON.\n"
        "- Level-2 knowledge = the provided derived Q&A list.\n"
        "- You MUST NOT use any outside knowledge.\n"
        "- If not answerable, return `needs_clarification=true` and ask focused follow-up questions.\n"
        "Return ONLY valid JSON matching the schema."
    )

    user = f"""
Level-1 case_pack:
{json.dumps(level1_case_pack, ensure_ascii=False)}

Level-2 derived Q&A:
{json.dumps(level2_qa, ensure_ascii=False)}

User question:
{user_question}
"""

    schema = {
        "name": "grounded_answer",
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "needs_clarification": {"type": "boolean"},
                "answer": {"type": "string"},
                "follow_up_questions": {"type": "array", "items": {"type": "string"}},
                "citations": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["needs_clarification", "answer", "follow_up_questions", "citations"],
        },
    }

    return _chat_json(model="gpt-4o", system=system, user=user, schema=schema, temperature=0.2)


def gpt_generate_knowledge_article(
    *,
    level1_case_pack: Dict[str, Any],
    level2_qa: List[Dict[str, str]],
    title_hint: Optional[str] = None,
) -> Dict[str, Any]:
    system = (
        "You are a technical writer for internal support knowledge base.\n"
        "Write only from the provided case_pack and derived Q&A.\n"
        "Return ONLY valid JSON matching the schema."
    )
    user = f"""
Create a knowledge article draft.

Title hint: {title_hint or ""}

case_pack:
{json.dumps(level1_case_pack, ensure_ascii=False)}

derived Q&A:
{json.dumps(level2_qa, ensure_ascii=False)}
"""

    schema = {
        "name": "knowledge_article",
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "title": {"type": "string"},
                "problem_statement": {"type": "string"},
                "environment": {"type": "string"},
                "symptoms": {"type": "array", "items": {"type": "string"}},
                "root_cause": {"type": "string"},
                "resolution": {"type": "array", "items": {"type": "string"}},
                "verification": {"type": "array", "items": {"type": "string"}},
                "prevention_notes": {"type": "array", "items": {"type": "string"}},
                "tags": {"type": "array", "items": {"type": "string"}},
            },
            "required": [
                "title",
                "problem_statement",
                "environment",
                "symptoms",
                "root_cause",
                "resolution",
                "verification",
                "prevention_notes",
                "tags",
            ],
        },
    }

    return _chat_json(model="gpt-4o", system=system, user=user, schema=schema, temperature=0.2)

