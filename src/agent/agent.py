# agent.py (Improved Logic)

from parser.project_parser import parse_project
from planner.planner import plan_documentation
from generator.generator import generate_docs
from evaluator.evaluator import evaluate_docs

def run_agent(project_path, max_iterations=3): # Increased iterations for demo
    iteration = 0
    final_doc = ""
    report = {}
    feedback = None # Start with no feedback

    while iteration < max_iterations:
        print(f"=== Iteration {iteration + 1} ===")

        # Step 1: Observe (usually only needed once unless files change)
        project_info = parse_project(project_path)

        # Step 2: Plan
        tasks = plan_documentation(project_info)

        # Step 3: Act (Now takes feedback)
        final_doc = generate_docs(tasks, feedback)

        # Step 4: Reflect
        report = evaluate_docs(final_doc)
        print(report)

        # Step 5: Decide if another iteration is needed
        if report["status"] == "OK":
            print("Documentation complete!")
            break
        else:
            print("Improving documentation based on feedback...")
            # Pass the issues from the report as feedback for the next loop
            feedback = report.get("feedback", []) 
        
        iteration += 1

    return final_doc, report