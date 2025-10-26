from langchain_core.prompts import ChatPromptTemplate

PUBLISHER_PROMPT_TEMPLATE = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert technical writer and document architect. Your task is to take a collection of raw, unordered Markdown documentation snippets for a Spring Boot project and assemble them into a single, polished, and cohesive technical document. The final output must be a single Markdown document."
        ),
        (
            "human",
            """
            Please assemble the following raw documentation snippets into a final, well-organized technical document.

            **Instructions:**
            1.  **Title:** Start the document with a main title, like `# Technical Documentation for [Project Name]`. Infer the project name from the file paths if possible.
            2.  **Introduction:** Write a brief, one-paragraph introduction explaining the purpose of the document.
            3.  **Table of Contents:** Create a "Table of Contents" section. It must contain clickable links to each major section you create (e.g., `1. [Entities](#entities)`).
            4.  **Logical Sorting:** You MUST sort the snippets into logical sections based on their purpose. The standard Spring Boot order is:
                *   Entities (Data Model)
                *   Repositories (Data Access Layer)
                *   Services (Business Logic Layer)
                *   Controllers (API Layer)
                *   Configuration
                *   Security
                *   DTOs (Data Transfer Objects)
                *   Exceptions
                *   Application Entrypoint
                *   Tests
            5.  **Section Headers:** Use a `##` header for each logical section (e.g., `## Entities`).
            6.  **Formatting:** Ensure the final output is clean, well-formatted Markdown. Use code fences for code snippets and tables where appropriate.
            7.  **Combine:** Combine all the provided snippets under their respective logical headers. Do not omit any of them. If a snippet contains an error message, include it as a note under the relevant file section.

            **Raw Documentation Snippets to process:**
            ---
            {documentation_snippets}
            ---

            Now, generate the complete and final Markdown document.
            """
        ),
    ]
)