"""Database connection manager using SQLAlchemy."""

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool
from typing import Optional
from functools import lru_cache
from contextvars import ContextVar
from backend.config.settings import get_settings

# Context variable to store database URL for current request
_db_url_context: ContextVar[Optional[str]] = ContextVar('db_url_context', default=None)


class DatabaseManager:
    """Manages database connections and provides introspection utilities."""
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize database manager.
        
        Args:
            database_url: Database connection URL. If None, uses context or settings.
        """
        settings = get_settings()
        # Priority: provided URL > context URL > settings URL
        self.database_url = database_url or _db_url_context.get() or settings.database_url
        self._engine: Optional[Engine] = None
    
    @property
    def engine(self) -> Engine:
        """Get or create database engine."""
        if self._engine is None:
            # For SQLite, use StaticPool to allow multiple connections
            if self.database_url.startswith("sqlite"):
                self._engine = create_engine(
                    self.database_url,
                    poolclass=StaticPool,
                    connect_args={"check_same_thread": False},
                    echo=False
                )
            else:
                self._engine = create_engine(
                    self.database_url,
                    pool_pre_ping=True,
                    echo=False
                )
        return self._engine
    
    def get_inspector(self):
        """Get SQLAlchemy inspector for database introspection."""
        return inspect(self.engine)
    
    def execute_query(self, query: str, limit: Optional[int] = None):
        """
        Execute a SQL query and return results.
        
        Args:
            query: SQL query string
            limit: Optional limit for results
            
        Returns:
            List of dictionaries representing rows
        """
        if limit:
            # Add LIMIT if not already present
            query_upper = query.upper().strip()
            if "LIMIT" not in query_upper:
                query = f"{query.rstrip(';')} LIMIT {limit}"
        
        with self.engine.connect() as conn:
            result = conn.execute(text(query))
            columns = result.keys()
            rows = result.fetchall()
            
            return [dict(zip(columns, row)) for row in rows]
    
    def close(self):
        """Close database connection."""
        if self._engine:
            self._engine.dispose()
            self._engine = None


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def set_database_url_context(database_url: Optional[str]):
    """
    Set the database URL context for the current request.
    
    Args:
        database_url: Database connection URL to use
    """
    _db_url_context.set(database_url)


def get_db_manager(database_url: Optional[str] = None) -> DatabaseManager:
    """
    Get or create database manager instance.
    
    Args:
        database_url: Optional database URL override (takes priority over context)
        
    Returns:
        DatabaseManager instance
    """
    # If database_url is provided, use it directly
    # Otherwise, the DatabaseManager will check context and settings
    return DatabaseManager(database_url)

