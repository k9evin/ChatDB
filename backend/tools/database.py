"""Database introspection tools using SQLAlchemy."""

import logging
from langchain_core.tools import tool
from typing import Dict, Any, List
from backend.database.connection import get_db_manager

logger = logging.getLogger(__name__)


@tool
def get_all_tables() -> Dict[str, Any]:
    """Get all table names from the database."""
    logger.info("[TOOL get_all_tables] Called")
    try:
        db_manager = get_db_manager()
        inspector = db_manager.get_inspector()
        tables = inspector.get_table_names()

        result = {"tables": tables, "count": len(tables)}
        logger.info(f"[TOOL get_all_tables] Success - Found {len(tables)} tables: {tables}")
        return result
    except Exception as e:
        logger.error(f"[TOOL get_all_tables] Error: {str(e)}")
        return {"error": str(e), "tables": [], "count": 0}


@tool
def get_table_schema(table_name: str) -> Dict[str, Any]:
    """Get detailed schema for a specific table."""
    logger.info(f"[TOOL get_table_schema] Called with table_name: {table_name}")
    try:
        db_manager = get_db_manager()
        inspector = db_manager.get_inspector()

        columns = inspector.get_columns(table_name)
        column_info = []
        for col in columns:
            column_info.append(
                {
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col.get("nullable", True),
                    "default": str(col.get("default")) if col.get("default") is not None else None,
                }
            )

        pk_constraint = inspector.get_pk_constraint(table_name)
        primary_key = pk_constraint.get("constrained_columns", []) if pk_constraint else []

        foreign_keys = inspector.get_foreign_keys(table_name)
        fk_info = []
        for fk in foreign_keys:
            fk_info.append(
                {
                    "constrained_columns": fk.get("constrained_columns", []),
                    "referred_table": fk.get("referred_table"),
                    "referred_columns": fk.get("referred_columns", []),
                }
            )

        sample_data = []
        try:
            sample_rows = db_manager.execute_query(f"SELECT * FROM {table_name} LIMIT 3")
            sample_data = sample_rows[:3]
        except Exception as e:
            logger.warning(f"[TOOL get_table_schema] Could not get sample data: {str(e)}")
            sample_data = []

        result = {
            "table_name": table_name,
            "columns": column_info,
            "primary_key": primary_key,
            "foreign_keys": fk_info,
            "sample_data": sample_data,
        }
        logger.info(
            f"[TOOL get_table_schema] Success - Table: {table_name}, Columns: {len(column_info)}, PK: {primary_key}"
        )
        return result
    except Exception as e:
        logger.error(f"[TOOL get_table_schema] Error for table {table_name}: {str(e)}")
        return {"error": str(e), "table_name": table_name}
