"""LangGraph workflow construction."""

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from backend.agent.state import AgentState
from backend.agent.nodes import (
    create_agent_node,
    create_finalize_node,
    create_tool_node_with_fallback,
)
from backend.agent.routers import should_continue, check_error_limit
from backend.config.settings import get_settings
from backend.tools.database import get_all_tables, get_table_schema
from backend.tools.rag import search_relevant_tables
from backend.tools.validation import validate_sql_syntax, validate_schema_attributes
from backend.tools.execution import execute_sql_query
from backend.tools.visualization import suggest_chart_type, prepare_chart_data


def create_agent_graph():
    """Build the complete LangGraph workflow."""
    settings = get_settings()

    llm = ChatOpenAI(
        model=settings.openrouter_model,
        temperature=settings.temperature,
        streaming=True,
        openai_api_key=settings.openrouter_api_key,
        openai_api_base=settings.openrouter_base_url,
        default_headers={
            "HTTP-Referer": "https://github.com/yourusername/chatdb",
            "X-Title": "ChatDB Agent",
        },
    )

    tools = [
        get_all_tables,
        get_table_schema,
        search_relevant_tables,
        validate_sql_syntax,
        validate_schema_attributes,
        execute_sql_query,
        suggest_chart_type,
        prepare_chart_data,
    ]

    agent = create_agent_node(llm, tools)
    finalize = create_finalize_node(llm)
    tool_node = create_tool_node_with_fallback(tools)

    workflow = StateGraph(AgentState)

    workflow.add_node("agent", agent)
    workflow.add_node("tools", tool_node)
    workflow.add_node("finalize", finalize)

    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", "end": "finalize"})
    workflow.add_conditional_edges(
        "tools", check_error_limit, {"agent": "agent", "finalize": "finalize"}
    )
    workflow.add_edge("finalize", END)

    memory = MemorySaver()

    return workflow.compile(checkpointer=memory)
