"""Conditional routing logic for the LangGraph workflow."""

import logging
from typing import Literal
from langchain_core.messages import AIMessage, ToolMessage
from backend.agent.state import AgentState

# Set up logger
logger = logging.getLogger(__name__)


def should_continue(state: AgentState) -> Literal["tools", "end"]:
    """Router: Decide if agent should call tools or end conversation."""
    messages = state["messages"]
    if not messages:
        logger.info("[ROUTER should_continue] No messages, routing to END")
        return "end"

    last_message = messages[-1]

    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        tool_names = [tc.get("name", "unknown") for tc in last_message.tool_calls]
        logger.info(
            f"[ROUTER should_continue] Agent wants to call tools: {tool_names}, routing to TOOLS"
        )
        return "tools"

    logger.info(
        f"[ROUTER should_continue] No tool calls, routing to END. Last message type: {type(last_message).__name__}"
    )
    if isinstance(last_message, AIMessage) and last_message.content:
        logger.info(
            f"[ROUTER should_continue] Final response preview: {last_message.content[:200]}..."
        )
    return "end"


def check_error_limit(state: AgentState) -> Literal["agent", "finalize", "end"]:
    """Router: Check if agent should continue or end after tool execution."""
    MAX_ERRORS = 3
    MAX_TOOL_ROUNDS = 10

    error_count = state.get("error_count", 0)
    messages = state.get("messages", [])
    tool_rounds = int(state.get("tool_rounds", 0) or 0)
    history = list(state.get("tool_call_history") or [])

    logger.info(
        f"[ROUTER check_error_limit] Error count: {error_count}/{MAX_ERRORS}, Messages: {len(messages)}"
    )
    if tool_rounds:
        logger.info(
            f"[ROUTER check_error_limit] Tool rounds so far: {tool_rounds}, History size: {len(history)}"
        )

    if error_count >= MAX_ERRORS:
        logger.warning(
            f"[ROUTER check_error_limit] Error limit reached ({error_count}), routing to END"
        )
        return "end"

    if tool_rounds >= MAX_TOOL_ROUNDS:
        logger.warning(
            f"[ROUTER check_error_limit] Tool rounds limit reached ({tool_rounds}), routing to FINALIZE"
        )
        return "finalize"

    if len(history) >= 2 and history[-1] == history[-2]:
        logger.warning(
            "[ROUTER check_error_limit] Detected repeated identical tool round signature, routing to FINALIZE"
        )
        return "finalize"
    if len(history) >= 6 and history[-6:-3] == history[-3:]:
        logger.warning(
            "[ROUTER check_error_limit] Detected repeated 3-round tool cycle, routing to FINALIZE"
        )
        return "finalize"

    if not messages:
        logger.info("[ROUTER check_error_limit] No messages, routing to END")
        return "end"

    last_message = messages[-1]
    last_msg_type = type(last_message).__name__

    if isinstance(last_message, ToolMessage):
        logger.info(
            f"[ROUTER check_error_limit] Last message is ToolMessage (ID: {last_message.tool_call_id}), routing to AGENT"
        )
        return "agent"

    if isinstance(last_message, AIMessage) and not last_message.tool_calls:
        logger.info(
            f"[ROUTER check_error_limit] Last message is AIMessage without tool_calls, routing to END"
        )
        return "end"

    logger.warning(
        f"[ROUTER check_error_limit] Unknown state - Last message type: {last_msg_type}, routing to END"
    )
    return "end"
