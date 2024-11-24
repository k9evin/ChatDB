import random
from typing import List, Dict, Tuple, Optional
from enum import Enum


class DatabaseType(Enum):
    SQL = "sql"
    MONGODB = "mongodb"


class QueryGeneratorService:
    def __init__(self):
        self.query_patterns: List[Tuple[str, Dict[str, str]]] = [
            (
                "Total {quantity} by {category}",
                {
                    "sql": "SELECT {category}, SUM({quantity}) FROM {table} GROUP BY {category}",
                    "mongodb": """[
                        {{ "$group": {{ 
                            "_id": "${category}",
                            "total": {{ "$sum": "${quantity}" }}
                        }} }}
                    ]""",
                },
            ),
            (
                "Average {quantity} by {category}",
                {
                    "sql": "SELECT {category}, AVG({quantity}) FROM {table} GROUP BY {category}",
                    "mongodb": """[
                        {{ "$group": {{ 
                            "_id": "${category}",
                            "average": {{ "$avg": "${quantity}" }}
                        }} }}
                    ]""",
                },
            ),
            (
                "Count by {category}",
                {
                    "sql": "SELECT {category}, COUNT(*) as count FROM {table} GROUP BY {category}",
                    "mongodb": """[
                        {{ "$group": {{ 
                            "_id": "${category}",
                            "count": {{ "$sum": 1 }}
                        }} }}
                    ]""",
                },
            ),
            (
                "Top {n} {quantity}",
                {
                    "sql": "SELECT * FROM {table} ORDER BY {quantity} DESC LIMIT {n}",
                    "mongodb": """[
                        {{ "$sort": {{ "{quantity}": -1 }} }},
                        {{ "$limit": {n} }}
                    ]""",
                },
            ),
            (
                "Filter {column} {condition}",
                {
                    "sql": "SELECT * FROM {table} WHERE {column} {condition}",
                    "mongodb": """{{ "{column}": {condition} }}""",
                },
            ),
            (
                "Join {table1} with {table2}",
                {
                    "sql": """SELECT {select_cols} 
                             FROM {table1} 
                             INNER JOIN {table2} 
                             ON {table1}.{join_key1} = {table2}.{join_key2}""",
                    "mongodb": """[
                        {{ "$lookup": {{
                            "from": "{table2}",
                            "localField": "{join_key1}",
                            "foreignField": "{join_key2}",
                            "as": "{table2}_data"
                        }} }},
                        {{ "$unwind": "${table2}_data" }}
                    ]""",
                },
            ),
        ]

    def generate_sample_queries(
        self,
        table_name: str,
        columns: List[str],
        db_type: str = "sql",
        available_tables: Optional[Dict[str, List[str]]] = None,
    ) -> List[Dict[str, str]]:
        queries = []
        db_type_enum = (
            DatabaseType.SQL if db_type.lower() == "mysql" else DatabaseType.MONGODB
        )

        for pattern, query_templates in self.query_patterns:
            try:
                # Skip join pattern if we don't have enough tables
                if "join" in pattern.lower():
                    if not available_tables or len(available_tables) < 2:
                        continue

                query = self._fill_query_template(
                    query_templates[db_type_enum.value],
                    table_name,
                    columns,
                    db_type_enum,
                    available_tables,
                )
                nl_query = self._fill_nl_template(pattern, columns, available_tables)

                if query and nl_query:
                    queries.append(
                        {"natural_language": nl_query, f"{db_type}_query": query}
                    )
            except Exception as e:
                print(f"Error generating query for pattern {pattern}: {str(e)}")
                continue

        return queries[:5]  # Return only 5 sample queries

    def _get_column_types(self, columns: List[str]) -> Tuple[List[str], List[str]]:
        numeric_cols = [
            col
            for col in columns
            if any(
                suffix in col.lower()
                for suffix in ("amount", "qty", "price", "num", "count", "total")
            )
        ]
        categorical_cols = [col for col in columns if col not in numeric_cols]
        return numeric_cols, categorical_cols

    def _fill_query_template(
        self,
        template: str,
        table_name: str,
        columns: List[str],
        db_type: DatabaseType,
        available_tables: Optional[Dict[str, List[str]]] = None,
    ) -> Optional[str]:
        try:
            numeric_cols, categorical_cols = self._get_column_types(columns)

            if not numeric_cols:
                numeric_cols = columns
            if not categorical_cols:
                categorical_cols = columns

            # Handle join queries
            if "join" in template.lower() and available_tables:
                return self._generate_join_query(table_name, available_tables, db_type)

            # Store selected columns to ensure consistency
            self.selected_quantity = random.choice(numeric_cols)
            self.selected_category = random.choice(categorical_cols)
            self.selected_column = random.choice(columns)
            self.selected_n = random.randint(3, 10)
            self.selected_condition = self._generate_condition(
                self.selected_column, numeric_cols, db_type
            )

            return template.format(
                table=table_name,
                category=self.selected_category,
                quantity=self.selected_quantity,
                column=self.selected_column,
                condition=self.selected_condition,
                n=self.selected_n,
            )
        except Exception as e:
            print(f"Error in _fill_query_template: {str(e)}")
            return None

    def _fill_nl_template(
        self,
        template: str,
        columns: List[str],
        available_tables: Optional[Dict[str, List[str]]] = None,
    ) -> Optional[str]:
        try:
            # Handle join queries
            if "join" in template.lower() and available_tables:
                possible_tables = [t for t in available_tables.keys()]
                if len(possible_tables) >= 2:
                    table1 = possible_tables[0]
                    table2 = possible_tables[1]
                    return template.format(table1=table1, table2=table2)
                return None

            # Use the same selected columns from _fill_query_template
            return template.format(
                category=self.selected_category,
                quantity=self.selected_quantity,
                column=self.selected_column,
                n=self.selected_n,
                condition="equals sample_value",
            )
        except Exception as e:
            print(f"Error in _fill_nl_template: {str(e)}")
            return None

    def _generate_join_query(
        self, table1: str, available_tables: Dict[str, List[str]], db_type: DatabaseType
    ) -> Optional[str]:
        try:
            if len(available_tables) < 2:
                return None

            # Get a random second table different from the first
            possible_tables = [t for t in available_tables.keys() if t != table1]
            if not possible_tables:
                return None

            table2 = random.choice(possible_tables)

            # Find potential join keys
            table1_cols = available_tables[table1]
            table2_cols = available_tables[table2]

            join_candidates = self._find_join_candidates(table1_cols, table2_cols)
            if not join_candidates:
                return None

            join_key1, join_key2 = random.choice(join_candidates)

            if db_type == DatabaseType.SQL:
                select_cols = f"{table1}.*, {table2}.*"
                return self.query_patterns[-1][1]["sql"].format(
                    select_cols=select_cols,
                    table1=table1,
                    table2=table2,
                    join_key1=join_key1,
                    join_key2=join_key2,
                )
            else:  # MongoDB
                return self.query_patterns[-1][1]["mongodb"].format(
                    table2=table2, join_key1=join_key1, join_key2=join_key2
                )
        except Exception as e:
            print(f"Error in _generate_join_query: {str(e)}")
            return None

    def _find_join_candidates(
        self, cols1: List[str], cols2: List[str]
    ) -> List[Tuple[str, str]]:
        join_pairs = []
        common_id_suffixes = ["id", "_id", "key", "_key", "code", "_code"]

        for col1 in cols1:
            col1_lower = col1.lower()
            for col2 in cols2:
                col2_lower = col2.lower()

                # Check for exact matches
                if col1_lower == col2_lower:
                    join_pairs.append((col1, col2))
                    continue

                # Check for common ID patterns
                for suffix in common_id_suffixes:
                    if col1_lower.endswith(suffix) and col2_lower.endswith(suffix):
                        prefix1 = col1_lower[: -len(suffix)]
                        prefix2 = col2_lower[: -len(suffix)]
                        if prefix1 in prefix2 or prefix2 in prefix1:
                            join_pairs.append((col1, col2))
                            break

        return join_pairs

    def _generate_condition(
        self, column: str, numeric_cols: List[str], db_type: DatabaseType
    ) -> str:
        if column in numeric_cols:
            value = random.randint(1, 1000)
            operators = [">", "<", ">=", "<=", "="]
            op = random.choice(operators)

            if db_type == DatabaseType.MONGODB:
                mongo_ops = {
                    ">": "$gt",
                    "<": "$lt",
                    ">=": "$gte",
                    "<=": "$lte",
                    "=": "$eq",
                }
                return f'{{ "{mongo_ops[op]}": {value} }}'
            return f"{op} {value}"
        else:
            value = "'sample_value'"
            if db_type == DatabaseType.MONGODB:
                return value
            return f"= {value}"
