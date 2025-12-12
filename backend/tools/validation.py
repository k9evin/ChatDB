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
    """
    Validate SQL syntax and check for dangerous operations.

    Checks:
    1. Parse SQL using sqlparse
    2. Verify it's a SELECT query (no INSERT/UPDATE/DELETE/DROP)
    3. Check for dangerous keywords
    4. Validate basic structure

    Args:
        sql_query: SQL query string to validate

    Returns:
        {"valid": True, "message": "SQL syntax is valid"}
        OR
        {"valid": False, "error": "Dangerous operation: DROP not allowed"}
    """
    logger.info(f"[TOOL validate_sql_syntax] Called with query: {sql_query[:100]}...")
    try:
        # Parse SQL
        parsed = sqlparse.parse(sql_query)

        if not parsed:
            return {"valid": False, "error": "Invalid SQL: Could not parse query"}

        # Check for dangerous operations
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

        # Check if it's a SELECT query
        if not sql_upper.startswith("SELECT"):
            return {
                "valid": False,
                "error": "Only SELECT queries are allowed. This query does not start with SELECT.",
            }

        # Check for dangerous keywords
        for keyword in dangerous_keywords:
            # Use word boundaries to avoid false positives
            pattern = r"\b" + keyword + r"\b"
            if re.search(pattern, sql_upper):
                return {
                    "valid": False,
                    "error": f"Dangerous operation: {keyword} not allowed. Only SELECT queries are permitted.",
                }

        # Basic structure validation
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
    """
    Validate that all columns referenced in query exist in schema.

    Process:
    1. Extract column names from SQL query (use regex or sqlparse)
    2. Get actual columns from database schema
    3. Check for mismatches

    Args:
        sql_query: SQL query to validate
        table_name: Name of the table being queried

    Returns:
        {"valid": True, "message": "All columns exist"}
        OR
        {"valid": False, "error": "Invalid columns: ['revenu']. Available: ['revenue', 'amount', 'total']"}
    """
    logger.info(
        f"[TOOL validate_schema_attributes] Called with table: {table_name}, query: {sql_query[:100]}..."
    )
    try:
        db_manager = get_db_manager()
        inspector = db_manager.get_inspector()

        # Get actual columns from database
        columns = inspector.get_columns(table_name)
        actual_column_names = {col["name"].lower() for col in columns}

        # Extract columns from SELECT clause
        sql_upper = sql_query.upper()

        # Handle SELECT * case
        if "SELECT *" in sql_upper or "SELECT\t*" in sql_upper:
            return {"valid": True, "message": "SELECT * query - all columns will be returned"}

        # Extract columns from SELECT clause using regex
        # Match SELECT ... FROM pattern
        select_match = re.search(r"SELECT\s+(.*?)\s+FROM", sql_upper, re.IGNORECASE | re.DOTALL)
        if not select_match:
            return {"valid": False, "error": "Could not parse SELECT clause"}

        select_clause = select_match.group(1)

        # Split by comma and clean up
        column_candidates = [col.strip() for col in select_clause.split(",")]

        # Extract column names (handle aliases and functions)
        referenced_columns = []
        for candidate in column_candidates:
            # Remove function calls (e.g., COUNT(*), SUM(amount))
            candidate = re.sub(r"\w+\s*\([^)]*\)", "", candidate)
            # Remove aliases (e.g., "column AS alias" or "column alias")
            candidate = re.sub(r"\s+AS\s+\w+", "", candidate, flags=re.IGNORECASE)
            candidate = re.sub(r"\s+\w+$", "", candidate)  # Remove trailing alias
            # Remove quotes and whitespace
            candidate = candidate.strip().strip('"').strip("'").strip("`")
            # Skip if empty or is a number
            if candidate and not candidate.isdigit():
                referenced_columns.append(candidate.lower())

        # Check for invalid columns
        invalid_columns = []
        for col in referenced_columns:
            if col not in actual_column_names:
                invalid_columns.append(col)

        if invalid_columns:
            # Find similar column names (fuzzy matching for typos)
            suggestions = {}
            for invalid_col in invalid_columns:
                # Simple Levenshtein-like suggestions
                similar = []
                for actual_col in actual_column_names:
                    # Check if actual column contains invalid column or vice versa
                    if invalid_col in actual_col or actual_col in invalid_col:
                        similar.append(actual_col)
                    # Check for common typos (first 3-4 characters match)
                    elif len(invalid_col) >= 3 and len(actual_col) >= 3:
                        if invalid_col[:3] == actual_col[:3]:
                            similar.append(actual_col)

                if similar:
                    suggestions[invalid_col] = similar[:3]  # Top 3 suggestions

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
