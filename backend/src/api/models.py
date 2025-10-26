from pydantic import BaseModel,Field
from typing import List, Dict, Any,Literal

class DocumentationRequest(BaseModel):
    project_path: str
    max_iterations: int = 1

class Report(BaseModel):
    status: str
    feedback: List[str] | str

class DocumentationResponse(BaseModel):
    documentation: str
    report: Report
class Task(BaseModel):
    id: int
    task_type: Literal["document_controller", "document_service", "document_entity"]
    class_name: str
    priority: int = Field(description="Priority from 1 (highest) to 10 (lowest)")
    dependencies: List[str] = Field(description="List of class names this task depends on")
    status: Literal["todo", "in_progress", "done", "failed"] = "todo"

class Plan(BaseModel):
    reasoning: str = Field(description="The LLM's step-by-step reasoning for creating this plan.")
    tasks: List[Task]