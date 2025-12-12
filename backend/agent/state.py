"""State schema for the LangGraph agent workflow."""

from typing import Annotated, Optional, List, Dict, Any
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """
    State schema for the agent workflow.

    Fields:
    - messages: Conversation history with automatic deduplication
    - query_context: Stores RAG-retrieved schema context
    - validation_results: Tracks validation outcomes for debugging
    - error_count: Prevents infinite retry loops (max 3)
    - user_id: For multi-tenant support (optional)
    - sql_query: Generated SQL query
    - execution_result: Query execution results
    - database_url: Optional database connection URL override
    """

    messages: Annotated[List[BaseMessage], add_messages]
    query_context: Optional[Dict[str, Any]]
    validation_results: Optional[Dict[str, Any]]
    error_count: int
    user_id: Optional[str]
    sql_query: Optional[str]
    execution_result: Optional[Dict[str, Any]]
    database_url: Optional[str]

    # Loop-guard fields (to prevent infinite tool-calling loops even when tools succeed)
    tool_rounds: int
    tool_call_history: Optional[List[str]]
