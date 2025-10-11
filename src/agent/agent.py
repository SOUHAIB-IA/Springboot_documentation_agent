from typing import TypedDict
from langchain import hub
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from src.agent.tools import CodeAndMemoryTools

class AgentState(TypedDict):
    project_path: str
    draft_documentation: str
    review_feedback: str
    revision_number: int

def create_agent(llm, tools, system_prompt: str):
    prompt = hub.pull("hwchase17/openai-tools-agent")
    llm_with_tools = llm.bind_tools(tools)
    agent = create_tool_calling_agent(llm_with_tools, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)


def writer_agent_node(state: AgentState):
    """The node for the Documentation Writer agent."""
    print("--- ✍️ CALLING WRITER AGENT ---")
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2, convert_system_message_to_human=True)
    
    tools_instance = CodeAndMemoryTools(project_path=state["project_path"])
    tools = [
        tools_instance.list_java_files,
        tools_instance.read_file_content,
        tools_instance.write_file_content,
        tools_instance.save_to_memory,
        tools_instance.search_memory
    ]

    if state.get("review_feedback"):
        # *** POLISHED PROMPT FOR REVISION ***
        task_prompt = f"""
        You are an autonomous technical writer AI. Your task is to revise a documentation draft based on the provided feedback.

        **CRITICAL INSTRUCTION: Focus ONLY on fixing the specific issues raised by the reviewer. Use your tools to read ONLY the relevant file(s) needed to address the feedback.** Do not rewrite the entire documentation from scratch.

        Previous Draft:
        (A snippet of the draft might be too long, so we just provide the feedback)
        
        Reviewer's Feedback to Address:
        `{state['review_feedback']}`
        
        Your process MUST be:
        1.  Analyze the feedback to identify the specific file or class that needs correction.
        2.  Use the `read_file_content` tool to read that specific file.
        3.  Rewrite the relevant section of the documentation to incorporate the fixes.
        4.  Combine your corrected section with the original draft to produce a new, complete version of the documentation for your final answer.
        """
    else:
        # (The initial draft prompt is good and remains the same)
        task_prompt = """
        You are an autonomous technical writer AI. Your mission is to generate complete Markdown documentation for a Spring Boot project.
        You MUST use your tools to acquire all necessary information yourself by first listing the files and then reading them one by one.
        After processing ALL relevant files, combine everything into ONE single, cohesive Markdown document.
        """

    writer_agent = create_agent(llm, tools, "")
    # We pass the full draft back into the scratchpad so the agent has context for revisions
    result = writer_agent.invoke({"input": task_prompt, "chat_history": [("assistant", state['draft_documentation'])]})
    return {"draft_documentation": result["output"], "revision_number": state["revision_number"] + 1}

def reviewer_agent_node(state: AgentState):
    """The node for the Documentation Reviewer agent."""
    print("--- 🧐 CALLING REVIEWER AGENT ---")
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, convert_system_message_to_human=True)

    tools_instance = CodeAndMemoryTools(project_path=state["project_path"])
    tools = [
        tools_instance.list_java_files,
        tools_instance.read_file_content,
    ]

    # *** POLISHED PROMPT FOR REVIEW ***
    task_prompt = f"""
    You are an autonomous, expert code reviewer. Your task is to review the provided documentation draft against the project's source code.

    **CRITICAL INSTRUCTION: Your review MUST focus exclusively on the accuracy and completeness of the documentation compared to the code. IGNORE any previous errors, logs, or metadata in your analysis.**

    Documentation Draft to Review:
    ```markdown
    {state['draft_documentation']}
    ```
    
    Your review process MUST be:
    1.  Read the documentation draft to understand what it claims about each class.
    2.  Use your tools (`list_java_files`, `read_file_content`) to find and read the corresponding source code for each documented class.
    3.  Compare the documentation's claims to the actual code. Look for inaccuracies, omissions, or unclear explanations.
    4.  If the documentation is 100% accurate and complete, your final answer MUST be the single word: "APPROVED".
    5.  Otherwise, your final answer MUST be a concise, bulleted list of specific, actionable feedback on what to fix in the documentation.
    """

    reviewer_agent = create_agent(llm, tools, "")
    result = reviewer_agent.invoke({"input": task_prompt})
    return {"review_feedback": result["output"]}

# --- (The rest of the file, should_continue and run_agent, is correct and remains unchanged) ---
def should_continue(state: AgentState):
    """Conditional edge. Determines whether to loop back to the writer for revisions or to end the process."""
    print("--- ⚖️ CHECKING REVIEW ---")
    feedback = state["review_feedback"]
    revision_number = state["revision_number"]
    
    if "APPROVED" in feedback.upper():
        print("Reviewer approved. Ending process.")
        return "end"
    
    if revision_number >= 3:
        print(f"Max revisions ({revision_number}) reached. Ending process.")
        return "end"
    
    print("Feedback received. Returning to writer for revision.")
    return "continue"

def run_agent(project_path: str):
    """Assembles and runs the graph."""
    print("=== Multi-Agent Graph Run Start ===")
    workflow = StateGraph(AgentState)
    workflow.add_node("writer", writer_agent_node)
    workflow.add_node("reviewer", reviewer_agent_node)
    workflow.set_entry_point("writer")
    workflow.add_edge("writer", "reviewer")
    workflow.add_conditional_edges(
        "reviewer",
        should_continue,
        {"continue": "writer", "end": END}
    )
    app = workflow.compile()
    initial_state = {
        "project_path": project_path,
        "draft_documentation": "",
        "review_feedback": "",
        "revision_number": 0
    }
    final_state = app.invoke(initial_state, {"recursion_limit": 10})
    
    print("\n=== Agent Run End ===")
    final_documentation = final_state.get('draft_documentation', 'Agent did not produce a final output.')
    report = {
        "status": "Complete",
        "feedback": f"Process finished after {final_state.get('revision_number')} revision(s). Final review feedback: {final_state.get('review_feedback')}"
    }
    return final_documentation, report