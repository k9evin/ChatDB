from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker


class MySQLManager:
    def __init__(self, connection_string):
        self.engine = create_engine(connection_string)
        self.Session = sessionmaker(bind=self.engine)
        self.inspector = inspect(self.engine)

    def get_session(self):
        return self.Session()

    def get_tables(self):
        return self.inspector.get_table_names()

    def get_columns(self, table_name):
        return self.inspector.get_columns(table_name)

    def execute_query(self, query):
        with self.get_session() as session:
            result = session.execute(query)
            return [dict(row) for row in result]
