"""Database connection manager using SQLAlchemy."""

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool
from typing import Optional
from functools import lru_cache
from contextvars import ContextVar
from backend.config.settings import get_settings

_db_url_context: ContextVar[Optional[str]] = ContextVar("db_url_context", default=None)
_engine_cache: dict[str, Engine] = {}


class DatabaseManager:
    def __init__(self, database_url: Optional[str] = None):
        settings = get_settings()
        self.database_url = database_url or _db_url_context.get() or settings.database_url
        self._engine: Optional[Engine] = None

    @property
    def engine(self) -> Engine:
        if self._engine is None:
            if self.database_url in _engine_cache:
                self._engine = _engine_cache[self.database_url]
            else:
                if self.database_url.startswith("sqlite"):
                    self._engine = create_engine(
                        self.database_url,
                        poolclass=StaticPool,
                        connect_args={"check_same_thread": False},
                        echo=False,
                        pool_pre_ping=True,
                    )
                else:
                    self._engine = create_engine(
                        self.database_url,
                        pool_pre_ping=True,
                        pool_size=10,
                        max_overflow=20,
                        echo=False,
                    )
                _engine_cache[self.database_url] = self._engine
        return self._engine

    def get_inspector(self):
        return inspect(self.engine)

    def execute_query(self, query: str, limit: Optional[int] = None):
        if limit:
            query_upper = query.upper().strip()
            if "LIMIT" not in query_upper:
                query = f"{query.rstrip(';')} LIMIT {limit}"

        with self.engine.connect() as conn:
            result = conn.execute(text(query))
            columns = result.keys()
            rows = result.fetchall()

            return [dict(zip(columns, row)) for row in rows]

    def close(self):
        if self._engine:
            self._engine.dispose()
            self._engine = None


def set_database_url_context(database_url: Optional[str]):
    _db_url_context.set(database_url)


def get_db_manager(database_url: Optional[str] = None) -> DatabaseManager:
    return DatabaseManager(database_url)
