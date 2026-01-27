def summarize_case(case):
    return {
        "summary": f"Case {case['CaseNumber']} is currently {case['Status']} with priority {case['Priority']}.",
        "subject": case["Subject"],
        "description": case.get("Description", "No description"),
    }

