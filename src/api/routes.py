from fastapi import APIRouter, HTTPException
from .models import DocumentationRequest, DocumentationResponse
from src.agent.agent import run_agent

router = APIRouter()

@router.post("/generate-documentation", response_model=DocumentationResponse)
def generate_documentation_endpoint(request: DocumentationRequest):
    """
    Endpoint to trigger the documentation generation agent.
    """
    try:
        doc, report_dict = run_agent(
            project_path=request.project_path,
            max_iterations=request.max_iterations
        )
        return DocumentationResponse(documentation=doc, report=report_dict)
    except Exception as e:
        # A real app would have more specific error handling
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
def read_root():
    return {"message": "Documentation Agent API is running."}