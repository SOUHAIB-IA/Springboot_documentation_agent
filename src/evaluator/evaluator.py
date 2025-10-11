def evaluate_docs(doc_text):
    issues = []

    # Check if controllers have endpoints
    if "Controller" in doc_text and "Endpoints:" not in doc_text:
        issues.append("Controller docs missing endpoint section.")

    # Check for missing descriptions
    if "description TBD" in doc_text:
        issues.append("Some methods still have placeholder descriptions.")

    # Check formatting
    if not doc_text.strip().startswith("##"):
        issues.append("Docs missing section headers.")

    # Return evaluation summary
    if not issues:
        return {"status": "OK", "feedback": "Documentation looks complete."}
    else:
        return {"status": "NEEDS_IMPROVEMENT", "feedback": issues}
