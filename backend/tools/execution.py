"""SQL query execution tool."""

import logging
from langchain_core.tools import tool
from typing import Dict, Any, List
from backend.database.connection import get_db_manager

logger = logging.getLogger(__name__)


@tool
def execute_sql_query(sql_query: str) -> Dict[str, Any]:
    """Execute validated SQL query and return results."""
    logger.info(f"[TOOL execute_sql_query] Called with query: {sql_query[:100]}...")
    try:
        db_manager = get_db_manager()
        rows = db_manager.execute_query(sql_query)

        result = {"success": True, "rows": rows, "row_count": len(rows), "sql_query": sql_query}
        logger.info(f"[TOOL execute_sql_query] Success - Returned {len(rows)} rows")
        return result
    except Exception as e:
        logger.error(f"[TOOL execute_sql_query] Error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "sql_query": sql_query,
            "rows": [],
            "row_count": 0,
        }
