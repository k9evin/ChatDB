"""State schema for the LangGraph agent workflow."""

from typing import Annotated, Optional, List, Dict, Any
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """State schema for the agent workflow."""

    messages: Annotated[List[BaseMessage], add_messages]
    query_context: Optional[Dict[str, Any]]
    validation_results: Optional[Dict[str, Any]]
    error_count: int
    user_id: Optional[str]
    sql_query: Optional[str]
    execution_result: Optional[Dict[str, Any]]
    database_url: Optional[str]
    tool_rounds: int
    tool_call_history: Optional[List[str]]
