import os
from langchain.tools import tool
from src.memory import memory_instance # IMPORT the memory service
from src.agent.tool_models import ReadFileArgs, WriteFileArgs, SaveMemoryArgs, SearchMemoryArgs, EmptyArgs # Import the models

class CodeAndMemoryTools:
    def __init__(self, project_path: str):
        if not os.path.isdir(project_path):
            raise ValueError(f"Project path does not exist: {project_path}")
        self.project_path = project_path
        
        # NOTE: Methods are decorated with @tool below. Do NOT re-wrap them here.
        # Create a bound, no-argument tool for listing Java files. Wrapping the
        # callable here ensures it closes over `self` and avoids unbound-method
        # issues when the tools framework calls the function.
        def _list_java_files_plain():
            """Return a newline-separated string of Java file paths (relative to project_path)."""
            java_files = []
            for root, _, files in os.walk(self.project_path):
                for file in files:
                    if file.endswith('.java'):
                        relative_path = os.path.relpath(os.path.join(root, file), self.project_path)
                        java_files.append(relative_path)
            return "\n".join(java_files)

        # Expose a plain callable that can be used directly by non-tool code.
        self.list_java_files = _list_java_files_plain

        # Also expose a tool-wrapped version for use by tool-calling agents if needed.
        # Keep the tool wrapper under a different name to avoid accidental invocation
        # of the tool object as if it were a normal callable.
        self.list_java_files_tool = tool(args_schema=EmptyArgs)(_list_java_files_plain)

        # Create bound tools for the other instance methods so the tool system
        # calls bound callables (no missing 'self'). Each wrapper delegates to
        # the corresponding instance method.
        def _bound_read_file_content(file_path: str):
            """Read the contents of a file given its relative path.

            Args:
                file_path: Relative path to the file within the project.

            Returns:
                The file contents as a string, or an error message.
            """
            return CodeAndMemoryTools.read_file_content(self, file_path)

        def _bound_save_to_memory(content: str, source_file: str):
            """Save a piece of content to long-term memory with source metadata.

            Args:
                content: The text to save.
                source_file: The source file path associated with the content.

            Returns:
                A confirmation message.
            """
            return CodeAndMemoryTools.save_to_memory(self, content, source_file)

        def _bound_search_memory(query: str):
            """Search saved memory for a query string and return matches.

            Args:
                query: Search query.

            Returns:
                Search results joined by separators or a not-found message.
            """
            return CodeAndMemoryTools.search_memory(self, query)

        def _bound_write_file_content(file_path: str, content: str):
            """Write content to a file at the given relative path.

            Args:
                file_path: Relative path to write to.
                content: Text content to write.

            Returns:
                A success or error message.
            """
            return CodeAndMemoryTools.write_file_content(self, file_path, content)

        self.read_file_content = tool(args_schema=ReadFileArgs)(_bound_read_file_content)
        self.save_to_memory = tool(args_schema=SaveMemoryArgs)(_bound_save_to_memory)
        self.search_memory = tool(args_schema=SearchMemoryArgs)(_bound_search_memory)
        self.write_file_content = tool(args_schema=WriteFileArgs)(_bound_write_file_content)

  
    # Note: list_java_files is attached to the instance in __init__ as a bound tool.

 
    def read_file_content(self, file_path: str) -> str:
        """
        Reads the full source code of a specific Java file from the project.
        The input must be a relative path to a file, obtained from the list_java_files tool.
        """
        full_path = os.path.join(self.project_path, file_path)
        try:
            # Added encoding for better cross-platform compatibility
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return f"Error: File not found at '{file_path}'. Please verify the path with list_java_files."
        except Exception as e:
            return f"Error reading file: {e}"

    def save_to_memory(self, content: str, source_file: str) -> str:
        """
        Saves a piece of generated documentation or code analysis to long-term memory.
        The 'content' is what you want to remember, and 'source_file' is the file it came from.
        """
        # The tool now delegates to the memory service
        memory_instance.add_content(content, metadata={"source": source_file})
        return f"Successfully saved content from {source_file} to memory."

  
    def search_memory(self, query: str) -> str:
        """
        Searches long-term memory for relevant information about a topic or file.
        Use this BEFORE documenting a file to get related context.
        """
        # The tool now delegates to the memory service
        results = memory_instance.search_content(query)
        if not results:
            return "No relevant information found in memory."
        return "\n---\n".join(results)

    def write_file_content(self, file_path: str, content: str) -> str:
        """
        Writes or overwrites the content of a specific file in the project.
        Use this tool with caution as it will overwrite existing files.
        The input 'file_path' must be a relative path.
        The input 'content' is the new text to be written to the file.
        For example, you can use this to add Javadoc comments to a Java file.
        """
        full_path = os.path.join(self.project_path, file_path)
        try:
            # Create directories if they don't exist
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            # Added encoding for better cross-platform compatibility
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully wrote content to {file_path}."
        except Exception as e:
            return f"Error writing to file: {e}"