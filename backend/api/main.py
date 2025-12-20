"""FastAPI application with WebSocket support for streaming."""

import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage, ToolMessage, BaseMessage
from typing import Dict, Any
import json
import re

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("chatdb_agent.log")],
)
logger = logging.getLogger(__name__)

try:
    from langsmith import uuid7
except ImportError:
    import uuid

    def uuid7():
        return uuid.uuid4()


from langchain_core.runnables import RunnableConfig
from backend.database.connection import DatabaseManager
from backend.agent.graph import create_agent_graph
from backend.config.settings import get_settings
from backend.agent.nodes import _clean_tool_call_syntax

graph = create_agent_graph()
app = FastAPI(title="ChatDB API", version="1.0.0")

settings = get_settings()
cors_origins = [origin.strip() for origin in settings.cors_origins.split(",")]
if "*" in cors_origins:
    cors_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _serialize_for_json(obj: Any) -> Any:
    """Recursively serialize objects to JSON-compatible types."""
    if isinstance(obj, BaseMessage):
        if hasattr(obj, "model_dump"):
            try:
                return obj.model_dump()
            except Exception:
                pass

        try:
            from langchain_core.load.dump import dumpd

            return dumpd(obj)
        except (ImportError, Exception):
            pass

        result = {
            "type": obj.__class__.__name__,
            "content": obj.content if hasattr(obj, "content") else str(obj),
        }
        if isinstance(obj, ToolMessage) and hasattr(obj, "tool_call_id"):
            result["tool_call_id"] = obj.tool_call_id
        if hasattr(obj, "id"):
            result["id"] = obj.id
        if hasattr(obj, "name"):
            result["name"] = obj.name
        return result
    elif isinstance(obj, dict):
        return {key: _serialize_for_json(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_serialize_for_json(item) for item in obj]
    elif isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    else:
        try:
            return str(obj)
        except Exception:
            return None


@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for streaming agent responses."""
    await websocket.accept()

    thread_id = None

    try:
        while True:
            data = await websocket.receive_json()
            user_message = data.get("message", "")
            database_url = data.get("database_url")

            if thread_id is None:
                client_thread_id = data.get("thread_id")
                if client_thread_id:
                    thread_id = client_thread_id
                    logger.info(f"[WEBSOCKET] Using client-provided thread_id: {thread_id}")
                else:
                    thread_id = f"thread_{uuid7().hex[:8]}"
                    logger.info(f"[WEBSOCKET] Generated new thread_id: {thread_id}")
            else:
                logger.info(f"[WEBSOCKET] Reusing existing thread_id: {thread_id}")

            config = {"configurable": {"thread_id": thread_id}}

            if not user_message:
                await websocket.send_json({"type": "error", "content": "Empty message received"})
                continue

            initial_state = {
                "messages": [HumanMessage(content=user_message)],
                "query_context": None,
                "validation_results": None,
                "error_count": 0,
                "user_id": None,
                "sql_query": None,
                "execution_result": None,
                "database_url": database_url,
                "tool_rounds": 0,
                "tool_call_history": [],
            }

            logger.info(f"[WEBSOCKET] Starting agent for query: {user_message[:200]}...")
            logger.info(f"[WEBSOCKET] Thread ID: {thread_id}, Database URL: {database_url}")

            settings = get_settings()
            recursion_limit = getattr(settings, "recursion_limit", 50)
            run_config = RunnableConfig(recursion_limit=recursion_limit, **config)

            logger.info(f"[WEBSOCKET] Recursion limit set to: {recursion_limit}")

            step_count = 0
            final_content = ""
            is_collecting_tool_call = False
            async for event in graph.astream_events(initial_state, run_config, version="v1"):
                step_count += 1
                if step_count % 10 == 0:
                    logger.info(f"[WEBSOCKET] Processed {step_count} events so far...")
                kind = event["event"]

                if kind == "on_chat_model_start":
                    is_collecting_tool_call = False

                if kind == "on_chat_model_stream":
                    chunk = event.get("data", {}).get("chunk")
                    if chunk:
                        tool_call_chunks = getattr(chunk, "tool_call_chunks", None)
                        additional_kwargs = getattr(chunk, "additional_kwargs", None) or {}
                        has_tool_calls = bool(tool_call_chunks) or bool(
                            isinstance(additional_kwargs, dict)
                            and additional_kwargs.get("tool_calls")
                        )
                        if has_tool_calls:
                            is_collecting_tool_call = True
                            continue

                        content = getattr(chunk, "content", "") or ""
                        if not content:
                            continue

                        if not is_collecting_tool_call and any(
                            marker in content.lower()
                            for marker in ["<tool_call", "<function", "<parameter", "[tool_call"]
                        ):
                            is_collecting_tool_call = True
                            logger.info(
                                "[WEBSOCKET] Detected tool call leak in stream content, silencing tokens"
                            )
                            continue

                        if not is_collecting_tool_call:
                            cleaned_content = _clean_tool_call_syntax(content)
                            if cleaned_content:
                                await websocket.send_json(
                                    {"type": "token", "content": cleaned_content}
                                )

                elif kind == "on_tool_start":
                    is_collecting_tool_call = True
                    tool_name = event.get("name", "unknown_tool")
                    await websocket.send_json({"type": "tool_start", "tool": tool_name})

                elif kind == "on_tool_end":
                    output = event.get("data", {}).get("output", {})
                    serialized_output = _serialize_for_json(output)
                    await websocket.send_json(
                        {
                            "type": "tool_result",
                            "tool": event.get("name", "unknown_tool"),
                            "output": serialized_output,
                        }
                    )

                elif kind == "on_chat_model_end":
                    response = event.get("data", {}).get("output", {})
                    if hasattr(response, "content") and response.content:
                        final_content = _clean_tool_call_syntax(response.content).strip()

            await websocket.send_json(
                {"type": "complete", "content": final_content, "thread_id": thread_id}
            )

    except WebSocketDisconnect:
        print(f"WebSocket disconnected for thread {thread_id}")
    except Exception as e:
        print(f"Error in WebSocket: {str(e)}")
        try:
            await websocket.send_json({"type": "error", "content": str(e)})
        except:
            pass
        await websocket.close(code=1011)


@app.post("/api/database/test")
async def test_database_connection(request: Dict[str, Any]):
    """Test database connection."""
    database_url = request.get("database_url")

    if not database_url:
        raise HTTPException(status_code=400, detail="database_url is required")

    try:
        from backend.database.connection import DatabaseManager

        db_manager = DatabaseManager(database_url)
        inspector = db_manager.get_inspector()
        tables = inspector.get_table_names()

        return {
            "connected": True,
            "tables_count": len(tables),
            "tables": tables[:10],
        }
    except Exception as e:
        return {"connected": False, "error": str(e)}


@app.post("/api/execute-query")
async def execute_query(request: Dict[str, Any]):
    query = request.get("query")
    database_url = request.get("database_url")
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")

    try:
        db_manager = DatabaseManager(database_url)
        rows = db_manager.execute_query(query)
        return {"rows": rows, "row_count": len(rows)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()

    uvicorn.run(
        "backend.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug,
        reload_dirs=["backend"],
    )
