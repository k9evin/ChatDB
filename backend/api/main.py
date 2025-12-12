"""FastAPI application with WebSocket support for streaming."""

import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage, ToolMessage, BaseMessage
from typing import Dict, Any
import json
import csv
import io
import re

# Configure logging
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

    # Fallback to uuid4 if langsmith is not available
    def uuid7():
        return uuid.uuid4()


from sqlalchemy import MetaData, Table, Column, Integer, Float, String, inspect
from sqlalchemy.exc import SQLAlchemyError
from langchain_core.runnables import RunnableConfig
from backend.database.connection import DatabaseManager
from backend.agent.graph import create_agent_graph
from backend.config.settings import get_settings

# Initialize agent graph
graph = create_agent_graph()

# Initialize FastAPI app
app = FastAPI(title="ChatDB API", version="1.0.0")

# CORS configuration
settings = get_settings()
cors_origins = (
    settings.cors_origins.split(",")
    if "," in settings.cors_origins
    else [settings.cors_origins] if settings.cors_origins != "*" else ["*"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Helpers
# ---------------------------

MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5 MB
MAX_UPLOAD_ROWS = 10000


def _serialize_for_json(obj: Any) -> Any:
    """
    Recursively serialize objects to JSON-compatible types.
    Handles LangChain message objects (ToolMessage, BaseMessage, etc.)
    and other non-serializable types.

    Uses LangChain's built-in serialization methods when available,
    with fallback to manual conversion for compatibility.
    """
    if isinstance(obj, BaseMessage):
        # Try using LangChain's model_dump if available (Pydantic v2)
        if hasattr(obj, "model_dump"):
            try:
                return obj.model_dump()
            except Exception:
                pass

        # Try using dumpd from langchain_core.load.dump if available
        try:
            from langchain_core.load.dump import dumpd

            return dumpd(obj)
        except (ImportError, Exception):
            pass

        # Fallback: Manual conversion to dict
        result = {
            "type": obj.__class__.__name__,
            "content": obj.content if hasattr(obj, "content") else str(obj),
        }
        # Add tool_call_id for ToolMessage
        if isinstance(obj, ToolMessage) and hasattr(obj, "tool_call_id"):
            result["tool_call_id"] = obj.tool_call_id
        # Add additional fields that might be present
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
        # For other types, try to convert to string
        try:
            return str(obj)
        except Exception:
            return None


def _sanitize_identifier(name: str) -> str:
    """Sanitize table/column names to alphanumerics and underscores."""
    safe = re.sub(r"[^0-9a-zA-Z_]", "_", name).strip("_")
    return safe or "table"


def _infer_sqlalchemy_type(values):
    """Infer a simple SQLAlchemy type from sample values."""
    has_float = False
    for v in values:
        if v in (None, ""):
            continue
        try:
            int(v)
            continue
        except Exception:
            try:
                float(v)
                has_float = True
                continue
            except Exception:
                return String
    return Float if has_float else Integer


def _create_table_and_insert(db_url: str | None, table_name: str, rows):
    """Create table (replace) and insert rows."""
    db_manager = DatabaseManager(db_url)
    engine = db_manager.engine
    metadata = MetaData()

    if not rows:
        raise HTTPException(status_code=400, detail="No rows to import")

    # Sanitize columns
    original_columns = list(rows[0].keys())
    safe_columns = [_sanitize_identifier(c) for c in original_columns]

    # Build type hints
    column_samples = {c: [] for c in safe_columns}
    for row in rows:
        for col, safe_col in zip(original_columns, safe_columns):
            column_samples[safe_col].append(row.get(col))

    columns = []
    for col, vals in column_samples.items():
        col_type = _infer_sqlalchemy_type(vals)
        columns.append(Column(col, col_type))

    sanitized_table = _sanitize_identifier(table_name)
    table = Table(sanitized_table, metadata, *columns)

    # Replace table if exists
    metadata.drop_all(engine, [table], checkfirst=True)
    metadata.create_all(engine, [table], checkfirst=True)

    # Remap rows to safe column names
    remapped_rows = []
    for row in rows:
        remapped = {}
        for orig, safe in zip(original_columns, safe_columns):
            remapped[safe] = row.get(orig)
        remapped_rows.append(remapped)

    with engine.begin() as conn:
        conn.execute(table.insert(), remapped_rows)

    return sanitized_table, len(remapped_rows), safe_columns


@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for streaming agent responses.

    Protocol:
    - Client sends: {"message": "show me all customers", "database_url": "optional"}
    - Server streams:
        {"type": "token", "content": "I'll"}
        {"type": "token", "content": " help"}
        {"type": "tool_start", "tool": "search_relevant_tables"}
        {"type": "tool_result", "output": {...}}
        {"type": "complete", "message": "Here are the results..."}
    """
    await websocket.accept()

    # Thread ID will be set from client message or generated if not provided
    thread_id = None

    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            user_message = data.get("message", "")
            database_url = data.get("database_url")  # Optional database URL
            
            # Use thread_id from client if provided, otherwise generate new one
            # This allows conversation continuity across multiple messages
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

            # Initialize state
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

            # Configure recursion limit to prevent infinite loops
            # Get recursion limit from settings (default: 50)
            settings = get_settings()
            recursion_limit = getattr(settings, "recursion_limit", 50)
            run_config = RunnableConfig(recursion_limit=recursion_limit, **config)

            logger.info(f"[WEBSOCKET] Recursion limit set to: {recursion_limit}")

            # Stream agent responses
            step_count = 0
            async for event in graph.astream_events(initial_state, run_config, version="v1"):
                step_count += 1
                if step_count % 10 == 0:
                    logger.info(f"[WEBSOCKET] Processed {step_count} events so far...")
                kind = event["event"]

                # Handle chat model streaming
                if kind == "on_chat_model_stream":
                    chunk = event.get("data", {}).get("chunk")
                    if chunk and hasattr(chunk, "content") and chunk.content:
                        await websocket.send_json({"type": "token", "content": chunk.content})

                # Handle tool start
                elif kind == "on_tool_start":
                    tool_name = event.get("name", "unknown_tool")
                    await websocket.send_json({"type": "tool_start", "tool": tool_name})

                # Handle tool end
                elif kind == "on_tool_end":
                    output = event.get("data", {}).get("output", {})
                    # Serialize output to handle ToolMessage and other non-JSON types
                    serialized_output = _serialize_for_json(output)
                    await websocket.send_json(
                        {
                            "type": "tool_result",
                            "tool": event.get("name", "unknown_tool"),
                            "output": serialized_output,
                        }
                    )

                # Handle chat model end (final response)
                elif kind == "on_chat_model_end":
                    response = event.get("data", {}).get("output", {})
                    if hasattr(response, "content") and response.content:
                        await websocket.send_json({"type": "complete", "content": response.content})

            await websocket.send_json({"type": "complete", "thread_id": thread_id})

    except WebSocketDisconnect:
        print(f"WebSocket disconnected for thread {thread_id}")
    except Exception as e:
        print(f"Error in WebSocket: {str(e)}")
        try:
            await websocket.send_json({"type": "error", "content": str(e)})
        except:
            pass
        await websocket.close(code=1011)


@app.post("/api/query")
async def query_database(request: Dict[str, Any]):
    """
    Non-streaming endpoint for simple queries.

    Request body:
        {
            "message": "show me all customers",
            "thread_id": "optional_thread_id",
            "database_url": "optional_database_url"
        }
    """
    user_message = request.get("message", "")
    database_url = request.get("database_url")  # Optional database URL

    if not user_message:
        raise HTTPException(status_code=400, detail="Message is required")

    thread_id = request.get("thread_id", f"api_{uuid7().hex[:8]}")

    config = {"configurable": {"thread_id": thread_id}}

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

    try:
        result = graph.invoke(initial_state, config)

        # Extract final message
        messages = result.get("messages", [])
        final_message = messages[-1] if messages else None

        response_content = ""
        if final_message and hasattr(final_message, "content"):
            response_content = final_message.content

        return {
            "response": response_content,
            "conversation_id": thread_id,
            "messages": [
                {
                    "role": msg.__class__.__name__.replace("Message", "").lower(),
                    "content": msg.content if hasattr(msg, "content") else str(msg),
                    "type": msg.__class__.__name__,
                }
                for msg in messages
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "ChatDB API"}


@app.post("/api/database/test")
async def test_database_connection(request: Dict[str, Any]):
    """
    Test database connection.

    Request body:
        {
            "database_url": "sqlite:///./demo_database.db"
        }
    """
    database_url = request.get("database_url")

    if not database_url:
        raise HTTPException(status_code=400, detail="database_url is required")

    try:
        from backend.database.connection import DatabaseManager

        # Try to create a connection
        db_manager = DatabaseManager(database_url)
        inspector = db_manager.get_inspector()

        # Try to get table names as a test
        tables = inspector.get_table_names()

        return {
            "connected": True,
            "tables_count": len(tables),
            "tables": tables[:10],  # Return first 10 tables
        }
    except Exception as e:
        return {"connected": False, "error": str(e)}


# ---------------------------
# SQL-only REST endpoints
# ---------------------------


@app.get("/api/sample-queries")
async def sample_queries(table_name: str, database_url: str | None = None):
    try:
        db_manager = DatabaseManager(database_url)
        inspector = inspect(db_manager.engine)
        columns = inspector.get_columns(table_name)

        col_names = [c["name"] for c in columns]
        numeric_cols = [
            c["name"]
            for c in columns
            if any(
                token in str(c["type"]).upper() for token in ["INT", "DEC", "REAL", "FLOAT", "NUM"]
            )
        ]

        samples = [
            f"SELECT * FROM {table_name} LIMIT 20;",
            f"SELECT COUNT(*) AS total_rows FROM {table_name};",
        ]

        if numeric_cols:
            col = numeric_cols[0]
            samples.append(
                f"SELECT {col}, COUNT(*) AS cnt FROM {table_name} GROUP BY {col} ORDER BY cnt DESC LIMIT 10;"
            )
            samples.append(
                f"SELECT AVG({col}) AS avg_{col}, MIN({col}) AS min_{col}, MAX({col}) AS max_{col} FROM {table_name};"
            )

        if len(col_names) >= 2:
            samples.append(
                f"SELECT {col_names[0]}, {col_names[1]} FROM {table_name} ORDER BY {col_names[0]} LIMIT 20;"
            )

        return {"sample_queries": samples}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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


@app.post("/api/upload")
async def upload_csv(
    file: UploadFile = File(...),
    table_name: str = Form(...),
    database_url: str | None = Form(None),
):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    raw = await file.read()
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=400, detail="File too large (max 5MB)")

    try:
        text_stream = io.StringIO(raw.decode("utf-8"))
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Failed to decode file as UTF-8")

    reader = csv.DictReader(text_stream)
    if not reader.fieldnames:
        raise HTTPException(status_code=400, detail="CSV header is required")

    rows = []
    for idx, row in enumerate(reader):
        rows.append(row)
        if idx + 1 >= MAX_UPLOAD_ROWS:
            break

    try:
        sanitized_table, row_count, columns = _create_table_and_insert(
            database_url, table_name, rows
        )
        return {"table_name": sanitized_table, "rows_imported": row_count, "columns": columns}
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
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
