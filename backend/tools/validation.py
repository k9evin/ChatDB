"""Multi-layer SQL validation tools."""

import logging
from langchain_core.tools import tool
from typing import Dict, Any
import sqlparse
import re
from backend.database.connection import get_db_manager

logger = logging.getLogger(__name__)


@tool
def validate_sql_syntax(sql_query: str) -> Dict[str, Any]:
    """Validate SQL syntax and check for dangerous operations."""
    logger.info(f"[TOOL validate_sql_syntax] Called with query: {sql_query[:100]}...")
    try:
        parsed = sqlparse.parse(sql_query)

        if not parsed:
            return {"valid": False, "error": "Invalid SQL: Could not parse query"}

        dangerous_keywords = [
            "DROP",
            "DELETE",
            "TRUNCATE",
            "ALTER",
            "UPDATE",
            "INSERT",
            "CREATE",
            "GRANT",
            "REVOKE",
            "EXEC",
            "EXECUTE",
        ]

        sql_upper = sql_query.upper().strip()

        if not sql_upper.startswith("SELECT"):
            return {
                "valid": False,
                "error": "Only SELECT queries are allowed. This query does not start with SELECT.",
            }

        for keyword in dangerous_keywords:
            pattern = r"\b" + keyword + r"\b"
            if re.search(pattern, sql_upper):
                return {
                    "valid": False,
                    "error": f"Dangerous operation: {keyword} not allowed. Only SELECT queries are permitted.",
                }

        if "FROM" not in sql_upper:
            return {"valid": False, "error": "Invalid SQL: Missing FROM clause"}

        result = {"valid": True, "message": "SQL syntax is valid and safe"}
        logger.info(f"[TOOL validate_sql_syntax] Validation passed")
        return result
    except Exception as e:
        logger.error(f"[TOOL validate_sql_syntax] Validation error: {str(e)}")
        return {"valid": False, "error": f"SQL validation error: {str(e)}"}


@tool
def validate_schema_attributes(sql_query: str, table_name: str) -> Dict[str, Any]:
    """Validate that all columns referenced in query exist in schema."""
    logger.info(
        f"[TOOL validate_schema_attributes] Called with table: {table_name}, query: {sql_query[:100]}..."
    )
    try:
        db_manager = get_db_manager()
        inspector = db_manager.get_inspector()

        columns = inspector.get_columns(table_name)
        actual_column_names = {col["name"].lower() for col in columns}

        sql_upper = sql_query.upper()

        if "SELECT *" in sql_upper or "SELECT\t*" in sql_upper:
            return {"valid": True, "message": "SELECT * query - all columns will be returned"}

        select_match = re.search(r"SELECT\s+(.*?)\s+FROM", sql_upper, re.IGNORECASE | re.DOTALL)
        if not select_match:
            return {"valid": False, "error": "Could not parse SELECT clause"}

        select_clause = select_match.group(1)
        column_candidates = [col.strip() for col in select_clause.split(",")]

        referenced_columns = []
        for candidate in column_candidates:
            candidate = re.sub(r"\w+\s*\([^)]*\)", "", candidate)
            candidate = re.sub(r"\s+AS\s+\w+", "", candidate, flags=re.IGNORECASE)
            candidate = re.sub(r"\s+\w+$", "", candidate)
            candidate = candidate.strip().strip('"').strip("'").strip("`")
            if candidate and not candidate.isdigit():
                referenced_columns.append(candidate.lower())

        invalid_columns = []
        for col in referenced_columns:
            if col not in actual_column_names:
                invalid_columns.append(col)

        if invalid_columns:
            suggestions = {}
            for invalid_col in invalid_columns:
                similar = []
                for actual_col in actual_column_names:
                    if invalid_col in actual_col or actual_col in invalid_col:
                        similar.append(actual_col)
                    elif len(invalid_col) >= 3 and len(actual_col) >= 3:
                        if invalid_col[:3] == actual_col[:3]:
                            similar.append(actual_col)

                if similar:
                    suggestions[invalid_col] = similar[:3]

            error_msg = f"Invalid columns: {invalid_columns}. Available columns: {sorted(actual_column_names)}"
            if suggestions:
                error_msg += f"\nSuggestions: {suggestions}"

            return {"valid": False, "error": error_msg}

        result = {
            "valid": True,
            "message": "All columns exist in the schema",
            "referenced_columns": referenced_columns,
        }
        logger.info(f"[TOOL validate_schema_attributes] Validation passed for table {table_name}")
        return result
    except Exception as e:
        logger.error(
            f"[TOOL validate_schema_attributes] Validation error for table {table_name}: {str(e)}"
        )
        return {"valid": False, "error": f"Schema validation error: {str(e)}"}
