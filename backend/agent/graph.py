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
    """
    Build the complete LangGraph workflow.

    Graph structure:

        START
          ↓
        [Agent] ←──────┐
          ↓             │
      {should_continue} │
          ↓             │
        [Tools] ────────┘
          ↓
      {check_error_limit}
          ↓
         END

    Flow explanation:
    1. Start with agent node (reasoning)
    2. If agent calls tools → go to tool node
    3. After tools execute → check error limit
    4. If errors < 3 → return to agent for retry
    5. If errors >= 3 or no tool calls → end
    """
    settings = get_settings()

    # Initialize LLM with OpenRouter
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

    # Collect all tools
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

    # Create nodes
    agent = create_agent_node(llm, tools)
    finalize = create_finalize_node(llm)
    tool_node = create_tool_node_with_fallback(tools)

    # Build graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("agent", agent)
    workflow.add_node("tools", tool_node)
    workflow.add_node("finalize", finalize)

    # Set entry point using START constant (official recommended way)
    workflow.add_edge(START, "agent")

    # Add conditional routing
    workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", "end": "finalize"})

    workflow.add_conditional_edges(
        "tools", check_error_limit, {"agent": "agent", "finalize": "finalize"}
    )

    # Finalize always ends using END constant (official recommended way)
    workflow.add_edge("finalize", END)

    # Add memory for conversation persistence
    memory = MemorySaver()

    return workflow.compile(checkpointer=memory)
