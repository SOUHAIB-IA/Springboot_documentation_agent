import uvicorn
import socketio
import asyncio
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from src.api.routes import router as api_router
from src.agent.agent import run_agent

# --- 1. Load Environment Variables ---
load_dotenv()

# --- 2. Create FastAPI App ---
app = FastAPI(
    title="AI Documentation Agent API",
    description="An API to automatically generate documentation for a Spring Boot project.",
    version="1.0.0"
)

# --- 3. Add CORS Middleware BEFORE including routers ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ✅ Fixed: was correct
    allow_credentials=True,
    allow_methods=["*"],  # ✅ Fixed: changed from methods to allow_methods
    allow_headers=["*"],  # ✅ Fixed: was correct
)

# --- 4. Include routers AFTER middleware ---
app.include_router(api_router, prefix="/api", tags=["Agent"])

# --- 5. Create Socket.IO Server ---
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    logger=True,
    engineio_logger=True
)

# --- 6. Define Socket.IO Event Handlers ---
@sio.event
async def connect(sid, environ):
    print(f"Socket.IO client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Socket.IO client disconnected: {sid}")

@sio.on('start_agent')
async def handle_start_agent(sid, data):
    project_path = data.get('project_path')
    if not project_path:
        await sio.emit('log', {'level': 'ERROR', 'message': 'Project path not provided.'}, to=sid)
        return
    
    # Get the current running event loop
    loop = asyncio.get_running_loop()
    
    # This custom class will safely redirect stdout to the WebSocket from a separate thread
    class SocketIOEmitter:
        def __init__(self, sid, loop):
            self.sid = sid
            self.loop = loop
        
        def write(self, s: str):
            if s.strip():
                # Use run_coroutine_threadsafe to safely call the async emit
                # from the synchronous thread where the agent is running.
                asyncio.run_coroutine_threadsafe(
                    sio.emit('log', {'level': 'AGENT', 'message': s.strip()}, to=self.sid),
                    self.loop
                )
        
        def flush(self):
            pass
    
    original_stdout = sys.stdout
    sys.stdout = SocketIOEmitter(sid, loop)
    
    try:
        await sio.emit('log', {'level': 'INFO', 'message': 'Agent mission started... Discovering files...'}, to=sid)
        
        # Run the long-running, synchronous agent function in a separate thread
        doc, report = await loop.run_in_executor(
            None,
            run_agent,
            project_path
        )
        
        # Restore stdout before sending the final result
        sys.stdout = original_stdout
        print("Agent run finished. Emitting final result.")
        await sio.emit('final_result', {'documentation': doc, 'report': report}, to=sid)
        
    except Exception as e:
        sys.stdout = original_stdout
        print(f"A critical agent error occurred: {e}")
        await sio.emit('log', {'level': 'ERROR', 'message': f"A critical agent error occurred: {str(e)}"}, to=sid)
        
    finally:
        # Ensure stdout is always restored
        if sys.stdout is not original_stdout:
            sys.stdout = original_stdout

# --- 7. Wrap FastAPI app with Socket.IO ---
socket_app = socketio.ASGIApp(sio, app)

# --- 8. Main Entry Point ---
if __name__ == "__main__":
    uvicorn.run(
        "main:socket_app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )