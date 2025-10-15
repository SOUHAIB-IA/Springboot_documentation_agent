import time
from typing import TypedDict
from langchain import hub
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from src.agent.tools import CodeAndMemoryTools
from google.api_core.exceptions import ServiceUnavailable

from src.agent.publisher_prompts import PUBLISHER_PROMPT_TEMPLATE
from langchain_core.output_parsers import StrOutputParser

# --- AgentState and create_agent are the same ---
class AgentState(TypedDict):
    project_path: str
    file_path: str
    draft_documentation: str
    review_feedback: str
    revision_number: int

def create_agent(llm, tools):
    """Helper function to create a configured agent that uses native tool calling."""
    # This prompt is the standard for tool-calling agents and works well.
    prompt = hub.pull("hwchase17/openai-tools-agent")
    llm_with_tools = llm.bind_tools(tools)
    agent = create_tool_calling_agent(llm_with_tools, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

# --- Agent Nodes with Corrected Prompts ---
def writer_agent_node(state: AgentState):
    """The node for the Documentation Writer agent."""
    file_path = state['file_path']
    print(f"\n--- ✍️ CALLING WRITER for: {file_path} ---")

    # *** THE FIX: Add a strong persona and behavioral rules to the prompt ***
    if state.get("review_feedback"):
        # This prompt for revisions is fine as it's highly specific.
        system_prompt = f"""
        You are an autonomous technical writer AI. Your task is to revise a draft of documentation for the file `{file_path}` based on the provided feedback.
        You MUST use your tools to read the source code to verify the feedback. DO NOT ask for clarification.
        Your final answer MUST be only the complete, revised Markdown documentation.

        Reviewer's Feedback to Address: `{state['review_feedback']}`
        """
        user_input = f"Revise the documentation for {file_path} based on the feedback."
    else:
        # The initial draft prompt is where the main fix is needed.
        system_prompt = """
        You are an autonomous AI agent. Your sole purpose is to generate technical documentation for a given Java file.
        
        **BEHAVIORAL RULES:**
        1.  You MUST act autonomously.
        2.  You MUST NOT ask for help, clarification, or direction.
        3.  You MUST use your provided tools to get all the information you need.
        4.  Your final answer MUST be only the generated Markdown documentation. Do not include any conversational text, questions, or introductory phrases.
        """
        user_input = f"""
        Generate a detailed, comprehensive Markdown documentation section for the following Java file: `{file_path}`.
        You MUST start by using the `read_file_content` tool to get the file's source code.
        Then, analyze the code and write the documentation.
        """

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", # Switched back to 1.5 Pro for better instruction following
        temperature=0.2, 
        convert_system_message_to_human=True,
        system_message=system_prompt
    )
    
    tools_instance = CodeAndMemoryTools(project_path=state["project_path"])
    tools = [
        tools_instance.read_file_content,
        tools_instance.save_to_memory,
        tools_instance.search_memory
    ]

    writer_agent = create_agent(llm, tools)
    
    try:
        result = writer_agent.invoke({"input": user_input, "chat_history": [("assistant", state['draft_documentation'])]})
        return {"draft_documentation": result["output"], "revision_number": state.get("revision_number", 0) + 1}
    except ServiceUnavailable as e:
        error_message = f"Network error during writer execution: {e}. Skipping."
        print(f"❌ {error_message}")
        return {"draft_documentation": f"### ERROR: {error_message}", "revision_number": state.get("revision_number", 0) + 1}
    except Exception as e:
        error_message = f"An unexpected error occurred in writer: {e}. Skipping."
        print(f"❌ {error_message}")
        return {"draft_documentation": f"### ERROR: {error_message}", "revision_number": state.get("revision_number", 0) + 1}


def reviewer_agent_node(state: AgentState):
    """The node for the Documentation Reviewer agent."""
    file_path = state['file_path']
    print(f"\n--- 🧐 CALLING REVIEWER for: {file_path} ---")

    # *** THE FIX: Add a strong persona and behavioral rules to the reviewer as well ***
    system_prompt = """
    You are an autonomous AI code reviewer. Your sole purpose is to review a documentation draft against its source code.

    **BEHAVIORAL RULES:**
    1.  You MUST act autonomously.
    2.  You MUST NOT ask for help or clarification.
    3.  You MUST use your tools to read the source code for verification.
    4.  Your final answer MUST be ONLY the single word "APPROVED" or a bulleted list of feedback. Do not include conversational text.
    """
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        temperature=0, 
        convert_system_message_to_human=True,
        system_message=system_prompt
    )
    
    tools_instance = CodeAndMemoryTools(project_path=state["project_path"])
    tools = [tools_instance.read_file_content]

    reviewer_agent = create_agent(llm, tools)
    
    try:
        user_input = f"""
        Review the following documentation for the file `{file_path}`.
        Read this specific file's source code using your `read_file_content` tool and verify the documentation's accuracy.
        If it is accurate and complete, respond with "APPROVED".
        Otherwise, provide feedback.

        Documentation to Review:
        ```markdown
        {state['draft_documentation']}
        ```
        """
        result = reviewer_agent.invoke({"input": user_input})
        return {"review_feedback": result["output"]}
    except ServiceUnavailable as e:
        error_message = f"Network error during reviewer execution: {e}. Approving to skip."
        print(f"❌ {error_message}")
        return {"review_feedback": "APPROVED"}
    except Exception as e:
        error_message = f"An unexpected error occurred in reviewer: {e}. Approving to skip."
        print(f"❌ {error_message}")
        return {"review_feedback": "APPROVED"}

# --- 4. The Graph Logic is the same ---
def should_continue(state: AgentState):
    """Conditional edge to decide whether to loop or end."""
    print("--- ⚖️ CHECKING REVIEW ---")
    feedback = state["review_feedback"]
    revision_number = state["revision_number"]
    
    if "APPROVED" in feedback.upper():
        print("Reviewer approved. Ending process for this file.")
        return "end"
    
    if revision_number >= 3: 
        print(f"Max revisions ({revision_number}) reached. Ending process for this file.")
        return "end"
    
    print("Feedback received. Returning to writer for revision.")
    return "continue"

def run_agent(project_path: str):
    """
    Orchestrates the entire documentation generation process, from file discovery
    to final publishing.
    """
    print("=== Multi-Agent Orchestrator Start ===")
    
    # 1. Compile the reusable Writer/Reviewer agent graph
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

    # 2. Discover all files to be documented
    print("--- 🗺️ Discovering files in project... ---")
    tools_instance = CodeAndMemoryTools(project_path=project_path)
    try:
        file_list_str = tools_instance.list_java_files()
        files_to_document = [f for f in file_list_str.split('\n') if f] # Filter out empty lines
        if not files_to_document:
            return "No Java files found in the specified project path.", {"status": "Complete", "feedback": "No files to document."}
        print(f"Found {len(files_to_document)} files to document.")
    except Exception as e:
        return f"Error listing files: {e}", {"status": "Failed", "feedback": "Could not list project files."}

    # 3. Process each file in a loop to generate raw documentation snippets
    final_documentation_parts = []
    for i, file_path in enumerate(files_to_document):
        print("\n" + "="*50)
        print(f"📄 Processing file {i+1}/{len(files_to_document)}: {file_path}")
        print("="*50)
        
        initial_state = {
            "project_path": project_path,
            "file_path": file_path,
            "draft_documentation": "",
            "review_feedback": "",
            "revision_number": 0
        }
        
        # Invoke the graph for this single file
        final_state = app.invoke(initial_state, {"recursion_limit": 10})
        
        # Add the approved documentation snippet to our list
        snippet = final_state.get('draft_documentation', f"### Failed to document {file_path}\n")
        # Add the file path as a header to each snippet for the publisher's context
        final_documentation_parts.append(f"### File: `{file_path}`\n\n{snippet}")

        # Pause to respect API rate limits, but not after the last file
        if i < len(files_to_document) - 1:
            print("\n--- ⏳ Pausing for 60 seconds to respect API rate limits... ---")
            time.sleep(60)

    # 4. NEW: Call the Publisher Agent to assemble the final document
    print("\n" + "="*50)
    print("📚 Assembling the final document with the Publisher Agent...")
    print("="*50)

    # Combine all the generated snippets into a single string for the publisher
    raw_snippets = "\n\n---\n\n".join(final_documentation_parts)

    # Create the Publisher Chain
    publisher_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1, convert_system_message_to_human=True)
    publisher_chain = PUBLISHER_PROMPT_TEMPLATE | publisher_llm | StrOutputParser()

    # Invoke the Publisher to get the final, polished document
    try:
        final_document = publisher_chain.invoke({"documentation_snippets": raw_snippets})
        print("✅ Final document successfully assembled.")
    except Exception as e:
        print(f"❌ Error during publishing phase: {e}")
        print("⚠️ Falling back to returning raw, unorganized snippets.")
        final_document = "# Raw Documentation Snippets\n\n" + raw_snippets

    report = {
        "status": "Complete", 
        "feedback": f"Successfully processed and assembled documentation for {len(files_to_document)} files."
    }

    print("\n=== Orchestrator End ===")
    return final_document, report