import asyncio
from typing import Any, Dict
from langchain.callbacks.base import BaseCallbackHandler
from src.api.websocket_manager import ConnectionManager

class BroadcastingCallbackHandler(BaseCallbackHandler):
    def __init__(self, manager: ConnectionManager, loop: asyncio.AbstractEventLoop):
        self.manager = manager
        self.loop = loop

    def _broadcast(self, data: Dict[str, Any]):
        """A thread-safe method to call the async broadcast."""
        asyncio.run_coroutine_threadsafe(self.manager.broadcast(data), self.loop)

    def on_agent_action(self, action, **kwargs: Any) -> Any:
        """Called when the agent is about to use a tool."""
        # This captures the agent's "Thought"
        log_message = action.log.strip().split("\n")[0] # Get the first line of the thought
        self._broadcast({
            "level": "THOUGHT",
            "message": log_message
        })

    def on_tool_end(self, output: str, name: str, **kwargs: Any) -> Any:
        """Called when a tool finishes."""
        self._broadcast({
            "level": "OBSERVATION",
            "tool": name,
            "message": f"Output: {output[:200]}..." if len(output) > 200 else output
        })