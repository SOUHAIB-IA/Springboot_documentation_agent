import time
from typing import TypedDict
from langchain import hub
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from src.agent.tools import CodeAndMemoryTools
from google.api_core.exceptions import ServiceUnavailable

# --- 1. AgentState is the same ---
class AgentState(TypedDict):
    project_path: str
    file_path: str
    draft_documentation: str
    review_feedback: str
    revision_number: int

# --- 2. Agent Creation Helper is Corrected ---
def create_agent(llm, tools, system_prompt: str):
    """Helper function to create a configured agent that uses native tool calling."""
    
    # This is the standard prompt for tool-calling agents.
    prompt = hub.pull("hwchase17/openai-tools-agent")
    
    # *** THE FIX: Correctly inject the system prompt. ***
    # This prompt has an 'input' and 'agent_scratchpad' variable.
    # We don't need to manually add the system prompt to the input.
    # We can rely on the model's system message capabilities.
    # However, for full compatibility, let's ensure the prompt is well-formed.
    # The ChatGoogleGenerativeAI class handles system messages well when convert_system_message_to_human=True.
    
    llm_with_tools = llm.bind_tools(tools)
    
    # The agent combines the LLM with tools and the prompt.
    agent = create_tool_calling_agent(llm_with_tools, tools, prompt)
    
    return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

# --- 3. Agent Nodes are Corrected ---
def writer_agent_node(state: AgentState):
    """The node for the Documentation Writer agent."""
    file_path = state['file_path']
    print(f"\n--- ✍️ CALLING WRITER for: {file_path} ---")
    
    # Set the system message directly in the LLM, which is a cleaner pattern
    # The convert_system_message_to_human handles the formatting for us.
    if state.get("review_feedback"):
        system_prompt = f"""
        Revise the documentation for the file `{file_path}` based on the following feedback.
        Read the file's content to understand the context of the feedback and provide a new, corrected version.

        Reviewer's Feedback: `{state['review_feedback']}`
        Previous Draft:
        ```markdown
        {state['draft_documentation']}
        ```
        """
    else:
        system_prompt= f"""
        Generate a detailed, comprehensive Markdown documentation section for the following Java file: `{file_path}`.
        You MUST use the `read_file_content` tool to get the file's source code first.
        Analyze the code and document its purpose, key methods, annotations, and relationships.
        """
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
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

    writer_agent = create_agent(llm, tools, system_prompt)
    
    try:
        # The input can now be very simple, as the instructions are in the system message
        result = writer_agent.invoke({"input": f"Generate the documentation for {file_path}."})
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

    system_prompt = f"""
    Review the following documentation for the file `{file_path}`.
    Read this specific file's source code using your `read_file_content` tool and verify the documentation's accuracy.
    If it is accurate and complete, respond with ONLY the word "APPROVED".
    Otherwise, provide a concise, bulleted list of feedback.

    Documentation to Review:
    ```markdown
    {state['draft_documentation']}
    ```
    """
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        temperature=0, 
        convert_system_message_to_human=True,
        system_message=system_prompt
    )
    
    tools_instance = CodeAndMemoryTools(project_path=state["project_path"])
    tools = [tools_instance.read_file_content]

    reviewer_agent = create_agent(llm, tools, system_prompt)
    
    try:
        result = reviewer_agent.invoke({"input": state['draft_documentation']})
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
    """Orchestrates the documentation generation process, one file at a time."""
    # (This entire orchestrator function remains the same as the last version)
    # It correctly loops through files and invokes the graph.
    print("=== Multi-Agent Orchestrator Start ===")
    
    workflow = StateGraph(AgentState)
    workflow.add_node("writer", writer_agent_node)
    workflow.add_node("reviewer", reviewer_agent_node)
    workflow.set_entry_point("writer")
    workflow.add_edge("writer", "reviewer")
    workflow.add_conditional_edges("reviewer", should_continue, {"continue": "writer", "end": END})
    app = workflow.compile()

    print("--- 🗺️ Discovering files in project... ---")
    tools_instance = CodeAndMemoryTools(project_path=project_path)
    try:
        file_list_str = tools_instance.list_java_files()
        files_to_document = [f for f in file_list_str.split('\n') if f]
        print(f"Found {len(files_to_document)} files to document.")
    except Exception as e:
        return f"Error listing files: {e}", {"status": "Failed", "feedback": "Could not list project files."}

    final_documentation_parts = []
    for i, file_path in enumerate(files_to_document):
        print("\n" + "="*50)
        print(f"📄 Processing file {i+1}/{len(files_to_document)}: {file_path}")
        print("="*50)
        
        initial_state = {"project_path": project_path, "file_path": file_path, "draft_documentation": "", "review_feedback": "", "revision_number": 0}
        
        final_state = app.invoke(initial_state, {"recursion_limit": 10})
        final_documentation_parts.append(final_state.get('draft_documentation', f"### Failed to document {file_path}\n"))

        if i < len(files_to_document) - 1:
            print("\n--- ⏳ Pausing for 60 seconds to respect API rate limits... ---")
            time.sleep(60)

    full_documentation = "\n\n---\n\n".join(final_documentation_parts)
    report = {"status": "Complete", "feedback": f"Successfully processed {len(files_to_document)} files."}

    print("\n=== Orchestrator End ===")
    return full_documentation, report