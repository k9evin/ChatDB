"""Agent nodes for the LangGraph workflow."""

import logging
from typing import Dict, Any, List
import json
import uuid
import ast
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode
from backend.agent.state import AgentState
from backend.agent.prompts import SYSTEM_PROMPT
from backend.config.settings import get_settings
from backend.database.connection import set_database_url_context

logger = logging.getLogger(__name__)

CHART_INTENT_KEYWORDS = (
    "图表",
    "画图",
    "绘图",
    "趋势",
    "可视化",
    "折线图",
    "柱状图",
    "饼图",
    "chart",
    "plot",
    "graph",
    "trend",
    "visualize",
    "visualization",
)


def _has_chart_intent(text: str | None) -> bool:
    if not text:
        return False
    t = text.lower()
    return any(k.lower() in t for k in CHART_INTENT_KEYWORDS)


def _clean_tool_call_syntax(content: str | None) -> str:
    """Remove tool call syntax from response content."""
    if not content:
        return ""

    import re

    content = re.sub(
        r"<tool_call[^>]*>.*?</tool_call>", "", content, flags=re.DOTALL | re.IGNORECASE
    )
    content = re.sub(
        r"<function\s*=\s*[^>]+>.*?</function>", "", content, flags=re.DOTALL | re.IGNORECASE
    )
    content = re.sub(
        r"<parameter\s*=\s*[^>]+>.*?</parameter>", "", content, flags=re.DOTALL | re.IGNORECASE
    )
    content = re.sub(
        r"<(?:tool_call|function|parameter|call)\s*=[^>]*>.*$",
        "",
        content,
        flags=re.DOTALL | re.IGNORECASE,
    )
    content = re.sub(
        r"<(?:tool_call|function|parameter|call)[^>]*>", "", content, flags=re.IGNORECASE
    )
    content = re.sub(r"</(?:tool_call|function|parameter|call)>", "", content, flags=re.IGNORECASE)
    content = re.sub(r"\[tool_call\].*$", "", content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r"Tool Call:.*$", "", content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r"\n\s*\n\s*\n", "\n\n", content)

    return content


def _extract_text_tool_call(content: str, allowed_tool_names: set[str]) -> tuple[str, dict] | None:
    """Parse textual tool calls from content. Returns (tool_name, args) or None."""
    import re

    if not content:
        return None

    m = re.search(r"<function\s*=\s*([a-zA-Z0-9_]+)\s*>", content, flags=re.IGNORECASE)
    if not m:
        return None
    tool_name = (m.group(1) or "").strip()
    if tool_name not in allowed_tool_names:
        return None

    args: dict[str, str] = {}
    cursor = m.end()

    param_pat = re.compile(r"<parameter\s*=\s*([a-zA-Z0-9_]+)\s*>", flags=re.IGNORECASE)
    tag_pat = re.compile(r"<\s*(tool_call|function|parameter)\b", flags=re.IGNORECASE)

    while True:
        pm = param_pat.search(content, cursor)
        if not pm:
            break
        key = (pm.group(1) or "").strip()
        val_start = pm.end()
        next_tag = tag_pat.search(content, val_start)
        val_end = next_tag.start() if next_tag else len(content)
        value = content[val_start:val_end].strip()
        if key:
            args[key] = value
        cursor = val_end

    return tool_name, args


def _extract_jsonish(content: Any) -> Any:
    """Extract Python object from ToolMessage content (dict/list/JSON string)."""
    if content is None:
        return None
    if isinstance(content, (dict, list)):
        return content
    if isinstance(content, str):
        s = content.strip()
        if not s:
            return None
        try:
            return json.loads(s)
        except Exception:
            pass
        try:
            return ast.literal_eval(s)
        except Exception:
            return None
    return None


def _last_human_text(messages: list) -> str | None:
    for m in reversed(messages or []):
        if isinstance(m, HumanMessage):
            return m.content
    return None


def _ai_called_tool(messages: list, tool_name: str) -> bool:
    for m in messages or []:
        if isinstance(m, AIMessage) and getattr(m, "tool_calls", None):
            for tc in m.tool_calls or []:
                if (tc.get("name") or "") == tool_name:
                    return True
    return False


def _last_tool_output(messages: list, tool_name: str) -> dict | None:
    """Find the latest ToolMessage output for a given tool."""
    msgs = messages or []
    for idx in range(len(msgs) - 1, -1, -1):
        m = msgs[idx]
        if isinstance(m, AIMessage) and getattr(m, "tool_calls", None):
            if any((tc.get("name") or "") == tool_name for tc in (m.tool_calls or [])):
                for j in range(idx + 1, len(msgs)):
                    tm = msgs[j]
                    if isinstance(tm, ToolMessage):
                        parsed = _extract_jsonish(tm.content)
                        if isinstance(parsed, dict):
                            return parsed
                return None
    return None


def _make_tool_call(name: str, args: dict) -> dict:
    return {
        "id": f"call_{uuid.uuid4().hex}",
        "name": name,
        "args": args,
        "type": "tool_call",
    }


def create_agent_node(llm: ChatOpenAI, tools: list):
    """Create the main agent node for reasoning and tool selection."""
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    agent = prompt | llm.bind_tools(tools)
    allowed_tool_names = {getattr(t, "name", "") for t in (tools or []) if getattr(t, "name", "")}

    def agent_node(state: AgentState, config: RunnableConfig) -> Dict[str, Any]:
        """Process state through agent."""
        database_url = state.get("database_url")
        if database_url:
            set_database_url_context(database_url)

        messages = state.get("messages", [])
        error_count = state.get("error_count", 0)
        logger.info(
            f"[AGENT NODE] Processing state - Messages: {len(messages)}, Error count: {error_count}"
        )

        if messages:
            last_messages = messages[-3:] if len(messages) >= 3 else messages
            for i, msg in enumerate(last_messages):
                msg_type = type(msg).__name__
                if isinstance(msg, HumanMessage):
                    logger.info(
                        f"[AGENT NODE] Message {i}: {msg_type} - Content: {msg.content[:100]}..."
                    )
                elif isinstance(msg, AIMessage):
                    tool_calls_count = len(msg.tool_calls) if msg.tool_calls else 0
                    logger.info(
                        f"[AGENT NODE] Message {i}: {msg_type} - Tool calls: {tool_calls_count}, Content: {msg.content[:100] if msg.content else 'None'}..."
                    )
                elif isinstance(msg, ToolMessage):
                    logger.info(
                        f"[AGENT NODE] Message {i}: {msg_type} - Tool call ID: {msg.tool_call_id}, Content length: {len(str(msg.content))}"
                    )

        result = agent.invoke(state, config)
        try:
            if not getattr(result, "tool_calls", None) and getattr(result, "content", None):
                parsed = _extract_text_tool_call(str(result.content), allowed_tool_names)
                if parsed:
                    tool_name, args = parsed
                    logger.info(
                        f"[AGENT NODE] Detected textual tool call leak; converting to structured tool call: {tool_name}"
                    )
                    forced = AIMessage(
                        content="",
                        tool_calls=[_make_tool_call(tool_name, args)],
                    )
                    return {"messages": [forced]}
        except Exception as e:
            logger.warning(f"[AGENT NODE] Text tool-call parsing skipped due to error: {repr(e)}")

        try:
            last_user = _last_human_text(messages)
            if _has_chart_intent(last_user):
                exec_out = _last_tool_output(messages, "execute_sql_query")
                rows = exec_out.get("rows") if isinstance(exec_out, dict) else None
                if isinstance(rows, list) and rows:
                    already_prepared = _ai_called_tool(messages, "prepare_chart_data")
                    if not already_prepared:
                        already_suggested = _ai_called_tool(messages, "suggest_chart_type")
                        if not already_suggested:
                            logger.info(
                                "[AGENT NODE] Chart intent detected; forcing suggest_chart_type tool call"
                            )
                            forced = AIMessage(
                                content="",
                                tool_calls=[
                                    _make_tool_call(
                                        "suggest_chart_type",
                                        {"data": rows, "query": last_user or ""},
                                    )
                                ],
                            )
                            return {"messages": [forced]}

                        suggest_out = _last_tool_output(messages, "suggest_chart_type")
                        if (
                            isinstance(suggest_out, dict)
                            and suggest_out.get("should_visualize")
                            and suggest_out.get("chart_type")
                            and suggest_out.get("chart_type") != "table"
                        ):
                            logger.info(
                                "[AGENT NODE] Chart intent detected; forcing prepare_chart_data tool call"
                            )
                            forced = AIMessage(
                                content="",
                                tool_calls=[
                                    _make_tool_call(
                                        "prepare_chart_data",
                                        {
                                            "data": (suggest_out.get("data") or rows),
                                            "chart_config": (suggest_out.get("chart_config") or {}),
                                            "chart_type": suggest_out.get("chart_type"),
                                        },
                                    )
                                ],
                            )
                            return {"messages": [forced]}
        except Exception as e:
            logger.warning(f"[AGENT NODE] Chart guardrail skipped due to error: {repr(e)}")

        tool_calls_count = len(result.tool_calls) if result.tool_calls else 0
        logger.info(
            f"[AGENT NODE] Agent response - Tool calls: {tool_calls_count}, Has content: {bool(result.content)}"
        )

        if result.tool_calls:
            for i, tc in enumerate(result.tool_calls):
                logger.info(
                    f"[AGENT NODE] Tool call {i+1}: {tc.get('name', 'unknown')} - Args: {tc.get('args', {})}"
                )

        if result.content:
            cleaned_content = _clean_tool_call_syntax(result.content).strip()
            if cleaned_content != result.content:
                logger.warning(
                    "[AGENT NODE] Detected tool call syntax in response content, cleaning it"
                )
                result.content = cleaned_content

            logger.info(f"[AGENT NODE] Agent content preview: {result.content[:200]}...")

        if not result.tool_calls and not result.content:
            logger.warning("[AGENT NODE] Empty response from agent, adding prompt")
            return {
                "messages": [result, HumanMessage(content="Please provide a substantive response.")]
            }

        return {"messages": [result]}

    return agent_node


def create_finalize_node(llm: ChatOpenAI):
    """Create a finalize node that never calls tools."""
    finalize_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                SYSTEM_PROMPT
                + "\n\nFINALIZE MODE:\n"
                + "- You MUST NOT call any tools.\n"
                + "- Use the tool results already in the conversation.\n"
                + "- Provide a complete user-facing answer now and STOP.\n",
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    final_chain = finalize_prompt | llm

    def finalize_node(state: AgentState, config: RunnableConfig) -> Dict[str, Any]:
        database_url = state.get("database_url")
        if database_url:
            set_database_url_context(database_url)

        result = final_chain.invoke(state, config)

        if isinstance(result, AIMessage) and result.content:
            cleaned_content = _clean_tool_call_syntax(result.content).strip()
            if cleaned_content != result.content:
                logger.warning(
                    "[FINALIZE NODE] Detected tool call syntax in response content, cleaning it"
                )
                result.content = cleaned_content

        if isinstance(result, AIMessage) and getattr(result, "tool_calls", None):
            logger.warning(
                "[FINALIZE NODE] Unexpected tool_calls in finalize output; forcing content-only follow-up"
            )
            follow_up = final_chain.invoke(
                {
                    **state,
                    "messages": state.get("messages", [])
                    + [
                        result,
                        HumanMessage(
                            content="Do not call tools. Respond with the final answer now."
                        ),
                    ],
                },
                config,
            )
            if isinstance(follow_up, AIMessage) and follow_up.content:
                cleaned_content = _clean_tool_call_syntax(follow_up.content).strip()
                if cleaned_content != follow_up.content:
                    logger.warning(
                        "[FINALIZE NODE] Detected tool call syntax in follow-up response, cleaning it"
                    )
                    follow_up.content = cleaned_content
            return {"messages": [follow_up]}

        return {"messages": [result]}

    return finalize_node


def create_tool_node_with_fallback(tools: list):
    """Create tool execution node with automatic error recovery."""
    from langchain_core.runnables import RunnableLambda

    def _tool_signature(tool_calls: List[dict]) -> str:
        """Create a stable signature for one tool round to detect repetition loops."""
        normalized = []
        for tc in tool_calls or []:
            name = tc.get("name", "unknown")
            args = tc.get("args", {})
            try:
                args_str = json.dumps(args, sort_keys=True, ensure_ascii=False)
            except TypeError:
                args_str = str(args)
            normalized.append(f"{name}:{args_str}")
        return "|".join(normalized) if normalized else ""

    def handle_tool_error(state: AgentState) -> Dict[str, Any]:
        """Handle tool execution errors."""
        error = state.get("error")
        messages = state.get("messages", [])

        if not messages:
            return {
                "messages": [],
                "error_count": state.get("error_count", 0) + 1,
            }

        last_message = messages[-1]

        if isinstance(last_message, AIMessage) and last_message.tool_calls:
            tool_messages = [
                ToolMessage(
                    content=f"Error: {repr(error)}\n\nPlease analyze this error and retry with corrections.",
                    tool_call_id=tc["id"],
                )
                for tc in last_message.tool_calls
            ]

            return {
                "messages": tool_messages,
                "error_count": state.get("error_count", 0) + 1,
            }

        return {
            "messages": [],
            "error_count": state.get("error_count", 0) + 1,
        }

    tool_node = ToolNode(tools)

    def tool_node_with_context(state: AgentState, config: RunnableConfig) -> Dict[str, Any]:
        """Wrapper to set database URL context before tool execution."""
        database_url = state.get("database_url")
        if database_url:
            set_database_url_context(database_url)

        messages = state.get("messages", [])
        if messages:
            last_message = messages[-1]
            if isinstance(last_message, AIMessage) and last_message.tool_calls:
                logger.info(f"[TOOL NODE] Executing {len(last_message.tool_calls)} tool(s)")
                for i, tc in enumerate(last_message.tool_calls):
                    tool_name = tc.get("name", "unknown")
                    tool_args = tc.get("args", {})
                    logger.info(f"[TOOL NODE] Tool {i+1}: {tool_name} with args: {tool_args}")

        result = tool_node.invoke(state, config)

        tool_rounds = int(state.get("tool_rounds", 0) or 0) + 1
        history = list(state.get("tool_call_history") or [])
        if messages:
            last_message = messages[-1]
            if isinstance(last_message, AIMessage) and last_message.tool_calls:
                sig = _tool_signature(last_message.tool_calls)
                if sig:
                    history.append(sig)

        if isinstance(result, dict) and "messages" in result:
            tool_messages = result["messages"]
            logger.info(
                f"[TOOL NODE] Tool execution completed - {len(tool_messages)} result message(s)"
            )
            for i, tm in enumerate(tool_messages):
                if isinstance(tm, ToolMessage):
                    content_preview = str(tm.content)[:200] if tm.content else "None"
                    logger.info(
                        f"[TOOL NODE] Tool result {i+1} (ID: {tm.tool_call_id}): {content_preview}..."
                    )
                    if "error" in str(tm.content).lower():
                        logger.warning(
                            f"[TOOL NODE] Tool result {i+1} contains error: {content_preview}"
                        )

        if isinstance(result, dict):
            return {
                **result,
                "tool_rounds": tool_rounds,
                "tool_call_history": history,
            }
        return {
            "messages": [],
            "tool_rounds": tool_rounds,
            "tool_call_history": history,
        }

    return RunnableLambda(tool_node_with_context).with_fallbacks(
        [RunnableLambda(handle_tool_error)], exception_key="error"
    )
