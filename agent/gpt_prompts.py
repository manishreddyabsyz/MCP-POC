# agent/gpt_prompts.py
import os
import openai
import json
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def gpt_summarize(case_info: dict) -> dict:
    """
    Summarize a Salesforce case using GPT.
    Returns a dict with summary, technical_summary, troubleshooting_steps, next_actions.
    """
    prompt = f"""
You are a technical support assistant.

CaseNumber: {case_info.get('CaseNumber')}
Subject: {case_info.get('Subject')}
Description: {case_info.get('Description')}
Status: {case_info.get('Status')}
Priority: {case_info.get('Priority')}

Tasks:
1. Generate a concise CASE SUMMARY.
2. Generate a TECHNICAL SUMMARY for engineers.
3. Provide TROUBLESHOOTING STEPS as a list.
4. Provide NEXT IMMEDIATE ACTIONS as a list.

Return strictly as valid JSON like this:
{{
  "summary": "...",
  "technical_summary": "...",
  "troubleshooting_steps": ["step1", "step2"],
  "next_actions": ["action1", "action2"]
}}
"""
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )

        content = response.choices[0].message.content
        # Extract JSON if GPT adds extra text
        start = content.find("{")
        end = content.rfind("}") + 1
        json_content = content[start:end]

        return json.loads(json_content)

    except Exception as e:
        print("Error in GPT summarization:", e)
        return {
            "summary": "",
            "technical_summary": "",
            "troubleshooting_steps": [],
            "next_actions": []
        }
