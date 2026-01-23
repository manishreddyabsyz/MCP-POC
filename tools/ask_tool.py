# tools/interactive_ask.py
import re
from mcp.server.fastmcp import FastMCP
from salesforce import case_queries  # your Salesforce query functions
from agent.gpt_prompts import gpt_summarize

mcp = FastMCP()

def extract_case_number(query: str):
    match = re.search(r"\b\d{8}\b", query)
    return match.group(0) if match else None

def build_case_tree(case):
    gpt_output = gpt_summarize(case)

    tree = {
        "title": f"Case {case['CaseNumber']}",
        "content": gpt_output.get("summary"),
        "children": [
            {"title": "Technical Summary", "content": gpt_output.get("technical_summary"), "children": []},
            {"title": "Troubleshooting Steps", "content": "\n".join(gpt_output.get("troubleshooting_steps", [])), "children": []},
            {"title": "Next Actions", "content": "\n".join(gpt_output.get("next_actions", [])), "children": [
                {"title": "View Comments", "action": lambda: case_queries.get_case_comments(case["Id"]), "children": []},
                {"title": "View History", "action": lambda: case_queries.get_case_history(case["Id"]), "children": []},
                {"title": "View Feed", "action": lambda: case_queries.get_case_feed(case["Id"]), "children": []},
            ]}
        ],
        "follow_up_questions": [
            "Do you want to see technical details?",
            "Do you want comments for this case?",
            "Do you want history or feed updates?"
        ]
    }
    return tree

@mcp.tool()
def ask(user_query: str):
    case_number = extract_case_number(user_query)
    if not case_number:
        return {"clarification": "Please provide the 8-digit case number."}

    # Fetch the case from Salesforce
    case_list = case_queries.get_case(case_number)
    if not case_list:
        return {"error": "Case not found"}

    case = case_list[0]
    return build_case_tree(case)
