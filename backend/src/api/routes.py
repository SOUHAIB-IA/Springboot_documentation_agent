import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from .models import DocumentationRequest
from src.agent.agent import run_agent # Import your main agent function
from .websocket_manager import manager
from src.agent.streaming_callback import BroadcastingCallbackHandler

router = APIRouter()

@router.get("/")
def read_root():
    return {"message": "Documentation Agent API is running."}

@router.websocket("/ws/agent-feed")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Keep the connection alive
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@router.post("/generate-documentation")
async def generate_documentation_endpoint(request: DocumentationRequest):
    """
    Triggers the agent to run in a background thread and returns immediately.
    Logs are streamed over the WebSocket.
    """
    loop = asyncio.get_event_loop()
    callback_handler = BroadcastingCallbackHandler(manager, loop)

    # Use `run_in_executor` to run the blocking `run_agent` function in a thread pool
    # This prevents it from freezing the server.
    loop.run_in_executor(
        None,  # Use the default thread pool executor
        run_agent,  # The synchronous function to run
        request.project_path,  # The first argument for run_agent
        [callback_handler]  # The second argument (callbacks)
    )
    
    # Return an immediate response to the front end
    return {"message": "Agent mission started. See live feed for progress."}