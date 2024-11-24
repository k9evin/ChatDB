from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from typing import Optional, Dict, List
from sqlalchemy.engine import Engine
from urllib.parse import urlparse, urlunparse


class MySQLManager:
    def __init__(self, connection_string: str):
        # Parse the connection string
        parsed = urlparse(connection_string)
        # Store base connection without database
        self.base_connection_string = urlunparse(
            (parsed.scheme, parsed.netloc, '', '', '', '')
        )
        self.engines: Dict[str, Engine] = {}

    def get_engine(self, database_name: str) -> Engine:
        if not database_name:
            raise ValueError("Database name is required")
            
        if database_name not in self.engines:
            # Create a new connection string with the specified database
            db_connection_string = f"{self.base_connection_string}/{database_name}"
            self.engines[database_name] = create_engine(db_connection_string)
        
        return self.engines[database_name]

    def get_session(self, database_name: str):
        engine = self.get_engine(database_name)
        Session = sessionmaker(bind=engine)
        return Session()

    def get_tables(self, database_name: str) -> List[str]:
        engine = self.get_engine(database_name)
        inspector = inspect(engine)
        return inspector.get_table_names()

    def get_columns(self, table_name: str, database_name: str) -> List[Dict]:
        engine = self.get_engine(database_name)
        inspector = inspect(engine)
        return inspector.get_columns(table_name)

    def execute_query(self, query: str, database_name: str) -> List[Dict]:
        with self.get_session(database_name) as session:
            result = session.execute(query)
            return [dict(row) for row in result]

    def create_database_if_not_exists(self, database_name: str):
        """Create database if it doesn't exist"""
        engine = create_engine(self.base_connection_string)
        with engine.connect() as conn:
            conn.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
