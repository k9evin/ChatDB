"""Data visualization and chart generation tools."""

import logging
from langchain_core.tools import tool
from typing import Dict, Any, List, Optional
import json

logger = logging.getLogger(__name__)


def _infer_vl_type(field_name: str, sample_value: Any) -> str:
    """Infer a Vega-Lite type from field name + a sample value."""
    name = (field_name or "").lower()
    if any(k in name for k in ["date", "time", "created", "updated", "year", "month"]):
        return "temporal"
    # Very conservative: treat numeric as quantitative.
    if isinstance(sample_value, (int, float)):
        return "quantitative"
    return "nominal"


def _build_vega_lite_spec(
    chart_type: str, data: List[Dict[str, Any]], chart_config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Build a Vega-Lite spec from chart_type + chart_config.
    This is deterministic and avoids requiring the model to generate code.
    """
    x_key = (chart_config or {}).get("x_key")
    y_key = (chart_config or {}).get("y_key")
    title = (chart_config or {}).get("title") or "Chart"

    sample = data[0] if data else {}

    # Pie: our transformed data uses name/value by default.
    if chart_type == "pie":
        return {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "description": title,
            "title": title,
            "data": {"values": data},
            "mark": {"type": "arc", "tooltip": True},
            "encoding": {
                "theta": {"field": "value", "type": "quantitative"},
                "color": {"field": "name", "type": "nominal"},
                "tooltip": [
                    {"field": "name", "type": "nominal"},
                    {"field": "value", "type": "quantitative"},
                ],
            },
            "view": {"stroke": None},
        }

    # Fallback: if we don't have x/y keys, just show a table-like mark.
    if not x_key or not y_key:
        return {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "description": title,
            "title": title,
            "data": {"values": data},
            "mark": {"type": "point"},
        }

    x_type = _infer_vl_type(x_key, sample.get(x_key))
    y_type = _infer_vl_type(y_key, sample.get(y_key))

    mark_type = "bar"
    if chart_type == "line":
        mark_type = "line"
    elif chart_type == "area":
        mark_type = "area"
    elif chart_type == "scatter":
        mark_type = "point"

    base = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "description": title,
        "title": title,
        "data": {"values": data},
        "mark": {"type": mark_type, "tooltip": True},
        "encoding": {
            "x": {
                "field": x_key,
                "type": x_type,
                "title": (chart_config or {}).get("x_label") or x_key,
            },
            "y": {
                "field": y_key,
                "type": y_type,
                "title": (chart_config or {}).get("y_label") or y_key,
            },
            "tooltip": [
                {"field": x_key, "type": x_type},
                {"field": y_key, "type": y_type},
            ],
        },
    }

    # For line/area, a bit nicer: temporal x sorted.
    if mark_type in ("line", "area") and x_type == "temporal":
        base["encoding"]["x"]["axis"] = {"labelAngle": -45}
        base["encoding"]["x"]["sort"] = "ascending"

    return base


@tool
def suggest_chart_type(data: List[Dict[str, Any]], query: str = "") -> Dict[str, Any]:
    """
    Analyze query results and suggest appropriate chart type and configuration.

    This tool analyzes the data structure and user query to determine:
    - Best chart type (bar, line, pie, area, etc.)
    - X and Y axis mappings
    - Data transformations needed
    - Chart configuration

    Args:
        data: List of dictionaries representing query results
        query: Original user query for context

    Returns:
        {
            "should_visualize": True/False,
            "chart_type": "bar" | "line" | "pie" | "area" | "scatter" | "table",
            "chart_config": {
                "x_key": "column_name",
                "y_key": "column_name",
                "data_key": "column_name",  # for pie charts
                "title": "Chart Title",
                "x_label": "X Axis Label",
                "y_label": "Y Axis Label"
            },
            "data": [...],  # transformed data if needed
            "reasoning": "Why this chart type was chosen"
        }
    """
    if not data or len(data) == 0:
        return {"should_visualize": False, "reasoning": "No data to visualize"}

    # Get column names
    columns = list(data[0].keys())
    num_rows = len(data)

    # Analyze query for chart hints
    query_lower = query.lower()
    has_chart_keywords = any(
        keyword in query_lower
        for keyword in [
            "chart",
            "graph",
            "plot",
            "visualize",
            "show",
            "display",
            "trend",
            "compare",
            "distribution",
            "over time",
            "by",
        ]
    )

    # Determine chart type based on data structure and query
    chart_type = "table"  # default
    chart_config = {}

    # Check for time series data
    time_columns = [
        col
        for col in columns
        if any(
            time_word in col.lower()
            for time_word in ["date", "time", "created", "updated", "year", "month"]
        )
    ]

    # Check for numeric columns
    numeric_columns = []
    for col in columns:
        try:
            # Check if column contains numeric data
            sample_values = [row.get(col) for row in data[:5] if row.get(col) is not None]
            if sample_values:
                # Try to convert to float
                float(sample_values[0])
                numeric_columns.append(col)
        except (ValueError, TypeError):
            pass

    # Check for categorical columns
    categorical_columns = [
        col for col in columns if col not in numeric_columns and col not in time_columns
    ]

    # Decision logic
    if time_columns and numeric_columns and num_rows > 1:
        # Time series data - use line or area chart
        chart_type = "line" if num_rows <= 20 else "area"
        chart_config = {
            "x_key": time_columns[0],
            "y_key": numeric_columns[0],
            "title": f"{numeric_columns[0]} over time",
            "x_label": time_columns[0],
            "y_label": numeric_columns[0],
        }
        if len(numeric_columns) > 1:
            chart_config["multiple_series"] = numeric_columns

    elif categorical_columns and numeric_columns:
        # Categorical vs numeric - use bar chart
        chart_type = "bar"
        chart_config = {
            "x_key": categorical_columns[0],
            "y_key": numeric_columns[0],
            "title": f"{numeric_columns[0]} by {categorical_columns[0]}",
            "x_label": categorical_columns[0],
            "y_label": numeric_columns[0],
        }

        # If only one numeric column and small dataset, consider pie chart
        if (
            len(numeric_columns) == 1
            and num_rows <= 10
            and ("distribution" in query_lower or "percentage" in query_lower)
        ):
            chart_type = "pie"
            chart_config["data_key"] = categorical_columns[0]
            chart_config["value_key"] = numeric_columns[0]

    elif len(numeric_columns) >= 2:
        # Multiple numeric columns - scatter or line
        chart_type = "scatter" if num_rows > 10 else "line"
        chart_config = {
            "x_key": numeric_columns[0],
            "y_key": numeric_columns[1],
            "title": f"{numeric_columns[1]} vs {numeric_columns[0]}",
            "x_label": numeric_columns[0],
            "y_label": numeric_columns[1],
        }

    elif len(columns) == 2 and numeric_columns:
        # Simple two-column data
        chart_type = "bar"
        chart_config = {
            "x_key": columns[0],
            "y_key": columns[1],
            "title": f"{columns[1]} by {columns[0]}",
            "x_label": columns[0],
            "y_label": columns[1],
        }

    # Check if visualization is appropriate
    should_visualize = (
        has_chart_keywords
        or (chart_type != "table" and num_rows > 1)
        or (time_columns and numeric_columns)
    )

    reasoning = f"Data has {num_rows} rows with {len(columns)} columns. "
    if time_columns:
        reasoning += f"Time series detected ({time_columns[0]}). "
    if numeric_columns:
        reasoning += f"Numeric data: {numeric_columns}. "
    reasoning += f"Suggested {chart_type} chart."

    # Embed chart_type inside chart_config too, because downstream tooling
    # (e.g. prepare_chart_data) may only receive chart_config.
    if chart_config is None:
        chart_config = {}
    chart_config = {**chart_config, "chart_type": chart_type}

    result = {
        "should_visualize": should_visualize,
        "chart_type": chart_type,
        "chart_config": chart_config,
        "data": data,
        "reasoning": reasoning,
    }
    logger.info(
        f"[TOOL suggest_chart_type] Called - should_visualize: {should_visualize}, chart_type: {chart_type}, data_rows: {len(data)}"
    )
    return result


@tool
def prepare_chart_data(
    data: List[Dict[str, Any]],
    chart_config: Dict[str, Any],
    chart_type: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Prepare and transform data for chart visualization.

    Args:
        data: Raw query results
        chart_config: Chart configuration from suggest_chart_type

    Returns:
        {
            "chart_type": "bar",
            "data": [...],  # transformed data
            "config": {...},  # chart configuration
            "labels": {...}  # axis labels
        }
    """
    # Backward/forward compatible chart_type resolution:
    # - prefer explicit chart_type arg
    # - fall back to chart_config["chart_type"] when provided by suggest_chart_type
    resolved_chart_type = (
        chart_type
        or (chart_config or {}).get("chart_type")
        or (chart_config or {}).get("type")
        or (chart_config or {}).get("chartType")
        or "table"
    )

    # Transform data based on chart type
    if resolved_chart_type == "pie":
        # Pie chart needs name-value pairs
        data_key = chart_config.get("data_key")
        value_key = chart_config.get("value_key")
        if data_key and value_key:
            transformed_data = [
                {
                    "name": str(row.get(data_key, "")),
                    "value": float(row.get(value_key, 0)) if row.get(value_key) is not None else 0,
                }
                for row in data
            ]
        else:
            transformed_data = data
    else:
        # For other chart types, use data as-is but ensure numeric values
        transformed_data = []
        for row in data:
            transformed_row = {}
            for key, value in row.items():
                # Try to convert to number if it's a numeric string
                if isinstance(value, str):
                    try:
                        if "." in value:
                            transformed_row[key] = float(value)
                        else:
                            transformed_row[key] = int(value)
                    except ValueError:
                        transformed_row[key] = value
                else:
                    transformed_row[key] = value
            transformed_data.append(transformed_row)

    vega_lite_spec = _build_vega_lite_spec(
        resolved_chart_type, transformed_data, chart_config or {}
    )

    result = {
        "chart_type": resolved_chart_type,
        "data": transformed_data,
        "config": chart_config,
        "labels": {
            "x": chart_config.get("x_label", chart_config.get("x_key", "")),
            "y": chart_config.get("y_label", chart_config.get("y_key", "")),
        },
        "vega_lite_spec": vega_lite_spec,
    }
    logger.info(
        f"[TOOL prepare_chart_data] Called - chart_type: {resolved_chart_type}, data_rows: {len(transformed_data)}"
    )
    return result
