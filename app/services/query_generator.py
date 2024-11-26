from typing import List, Dict, Tuple, Optional
from enum import Enum
import random
import logging


class DatabaseType(Enum):
    SQL = "sql"
    MONGODB = "mongodb"


class QueryGeneratorService:
    def __init__(self, mysql_manager=None, mongo_manager=None):
        self.mysql_manager = mysql_manager
        self.mongo_manager = mongo_manager
        self.query_patterns: List[Tuple[str, Dict[str, str]]] = [
            (
                "Calculate the total {quantity} grouped by {category}",
                {
                    "sql": "SELECT {category}, SUM({quantity}) FROM {table} GROUP BY {category}",
                    "mongodb": """[
                        {{ "$group": {{ 
                            "_id": "${category}",
                            "total": {{ "$sum": "${quantity}" }}
                        }} }},
                        {{ "$project": {{
                            "_id": 0,
                            "{category}": "$_id",
                            "total": 1
                        }} }}
                    ]""",
                },
            ),
            (
                "Find the average {quantity} for each {category}",
                {
                    "sql": "SELECT {category}, AVG({quantity}) FROM {table} GROUP BY {category}",
                    "mongodb": """[
                        {{ "$group": {{ 
                            "_id": "${category}",
                            "average": {{ "$avg": "${quantity}" }}
                        }} }},
                        {{ "$project": {{
                            "_id": 0,
                            "{category}": "$_id",
                            "average": 1
                        }} }}
                    ]""",
                },
            ),
            (
                "Count the number of records for each {category}",
                {
                    "sql": "SELECT {category}, COUNT(*) as count FROM {table} GROUP BY {category}",
                    "mongodb": """[
                        {{ "$group": {{ 
                            "_id": "${category}",
                            "count": {{ "$sum": 1 }}
                        }} }},
                        {{ "$project": {{
                            "_id": 0,
                            "{category}": "$_id",
                            "count": 1
                        }} }}
                    ]""",
                },
            ),
            (
                "Show the top {n} records sorted by {quantity} in descending order",
                {
                    "sql": "SELECT * FROM {table} ORDER BY {quantity} DESC LIMIT {n}",
                    "mongodb": """[
                        {{ "$sort": {{ "{quantity}": -1 }} }},
                        {{ "$limit": {n} }},
                        {{ "$project": {{
                            "_id": 0
                        }} }}
                    ]""",
                },
            ),
            (
                "Filter records where {quantity} is {condition}",
                {
                    "sql": "SELECT * FROM {table} WHERE {quantity} {condition}",
                    "mongodb": """[
                        {{ "$match": {{ "{quantity}": {condition} }} }},
                        {{ "$project": {{
                            "_id": 0
                        }} }}
                    ]""",
                },
            ),
            (
                "Group by {category} and filter groups where {quantity} meets {condition}",
                {
                    "sql": """SELECT {category}, SUM({quantity}) as total FROM {table} GROUP BY {category} HAVING total {condition}""",
                    "mongodb": """[
                        {{ "$group": {{ 
                            "_id": "${category}",
                            "total": {{ "$sum": "${quantity}" }}
                        }} }},
                        {{ "$match": {{
                            "total": {condition}
                        }} }},
                        {{ "$project": {{
                            "_id": 0,
                            "{category}": "$_id",
                            "total": 1
                        }} }}
                    ]""",
                },
            ),
            (
                "Select specific columns {columns} from {table}",
                {
                    "sql": "SELECT {columns} FROM {table}",
                    "mongodb": """[
                        {{ "$project": {{ 
                            "_id": 0,
                            {columns_projection}
                        }} }}
                    ]""",
                },
            ),
        ]

    def generate_sample_queries(
        self,
        table_name: str,
        columns: List[str],
        db_type: str = "sql",
        database_name: str = None,
        available_tables: Optional[Dict[str, List[str]]] = None,
        construct: Optional[str] = None,
    ):
        logger = logging.getLogger(__name__)
        logger.info(f"Generating sample queries for table: {table_name}")
        logger.info(
            f"Input parameters - columns: {columns}, db_type: {db_type}, database_name: {database_name}, construct: {construct}"
        )

        queries = []
        db_type_enum = (
            DatabaseType.SQL if db_type.lower() == "mysql" else DatabaseType.MONGODB
        )

        # Filter patterns based on construct if specified
        patterns = (
            self._filter_patterns_by_construct(construct)
            if construct
            else self.query_patterns
        )

        for pattern, query_templates in patterns:
            try:
                logger.info(f"Processing pattern: {pattern}")

                query = self._fill_query_template(
                    query_templates[db_type_enum.value],
                    table_name,
                    columns,
                    db_type_enum,
                    database_name,
                    available_tables,
                )
                nl_query = self._fill_nl_template(
                    pattern, columns, table_name, available_tables
                )

                if query and nl_query:
                    queries.append(
                        {"natural_language": nl_query, f"{db_type}_query": query}
                    )
                else:
                    logger.warning(
                        f"Failed to generate query or nl_query for pattern: {pattern}"
                    )

            except Exception as e:
                logger.error(
                    f"Error generating query for pattern {pattern}: {str(e)}",
                    exc_info=True,
                )
                continue

        return queries

    def _filter_patterns_by_construct(
        self, construct: str
    ) -> List[Tuple[str, Dict[str, str]]]:
        if not construct or construct.lower() == "all":
            return self.query_patterns

        construct = construct.lower()

        # Map constructs to their corresponding patterns
        construct_patterns = {
            "group by with aggregation": [
                "Calculate the total {quantity} grouped by {category}",
                "Find the average {quantity} for each {category}",
            ],
            "group by with count": [
                "Count the number of records for each {category}",
            ],
            "order by with limit": [
                "Show the top {n} records sorted by {quantity} in descending order",
            ],
            "where clause": [
                "Filter records where {quantity} is {condition}",
            ],
            "having clause": [
                "Group by {category} and filter groups where {quantity} meets {condition}",
            ],
            "select columns": [
                "Select specific columns {columns} from {table}",
            ],
        }

        if construct not in construct_patterns:
            logger = logging.getLogger(__name__)
            logger.warning(f"Unknown construct: {construct}, returning all patterns")
            return self.query_patterns

        # Get the matching pattern descriptions
        matching_descriptions = construct_patterns[construct]

        # Filter query patterns based on matching descriptions
        filtered_patterns = [
            (desc, temp)
            for desc, temp in self.query_patterns
            if desc in matching_descriptions
        ]

        logger = logging.getLogger(__name__)
        logger.info(
            f"Filtered patterns for construct '{construct}': {[p[0] for p in filtered_patterns]}"
        )

        return filtered_patterns

    def _get_column_types(
        self, columns: List[str], table_name: str, database_name: str
    ) -> Tuple[List[str], List[str]]:
        logger = logging.getLogger(__name__)

        try:
            if hasattr(self, "mysql_manager"):
                numeric_types = {"int", "decimal", "float", "double", "numeric"}
                column_info = self.mysql_manager.get_columns(table_name, database_name)

                numeric_cols = []
                categorical_cols = []

                for col in column_info:
                    col_type = str(col["type"]).lower()
                    if any(num_type in col_type for num_type in numeric_types):
                        numeric_cols.append(col["name"])
                    else:
                        categorical_cols.append(col["name"])

            elif hasattr(self, "mongo_manager"):

                sample_data = self.mongo_manager.get_sample_data(
                    table_name, database_name
                )
                if sample_data:
                    numeric_cols = []
                    categorical_cols = []

                    # Use the first document to infer types
                    first_doc = sample_data[0]
                    for col in columns:
                        if col in first_doc:
                            value = first_doc[col]
                            if isinstance(value, (int, float)):
                                numeric_cols.append(col)
                            else:
                                categorical_cols.append(col)
                else:
                    logger.warning("No sample data available for type inference")
                    return columns, columns
            else:
                logger.warning("No database manager available for type inference")
                return columns, columns

            return numeric_cols, categorical_cols

        except Exception as e:
            logger.error(f"Error in column type inference: {str(e)}", exc_info=True)
            # Fallback to treating all columns as both numeric and categorical
            return columns, columns

    def _fill_query_template(
        self,
        template: str,
        table_name: str,
        columns: List[str],
        db_type: DatabaseType,
        database_name: str,
        available_tables: Optional[Dict[str, List[str]]] = None,
    ) -> Optional[str]:
        try:
            logger = logging.getLogger(__name__)
            numeric_cols, categorical_cols = self._get_column_types(
                columns, table_name, database_name
            )
            logger.info(
                f"Numeric columns: {numeric_cols}, Categorical columns: {categorical_cols}"
            )

            if not numeric_cols:
                numeric_cols = columns
            if not categorical_cols:
                categorical_cols = columns

            # Handle specific columns selection pattern
            if "{columns}" in template or "{columns_projection}" in template:
                selected_columns = random.sample(
                    columns, min(random.randint(2, 4), len(columns))
                )
                if db_type == DatabaseType.SQL:
                    columns_str = ", ".join(selected_columns)
                    self.selected_columns = selected_columns
                    return template.format(table=table_name, columns=columns_str)
                else:  # MongoDB
                    columns_projection = ", ".join(
                        f'"{col}": 1' for col in selected_columns
                    )
                    self.selected_columns = selected_columns
                    return template.format(columns_projection=columns_projection)

            # Handle other patterns
            self.selected_quantity = random.choice(numeric_cols)
            self.selected_category = random.choice(categorical_cols)
            self.selected_n = random.randint(3, 10)
            self.selected_condition = self._generate_condition(
                self.selected_quantity, numeric_cols, db_type
            )
            self.selected_having_condition = self._generate_having_condition(
                self.selected_quantity, db_type
            )

            return template.format(
                table=table_name,
                category=self.selected_category,
                quantity=self.selected_quantity,
                condition=self.selected_condition,
                n=self.selected_n,
                having_condition=self.selected_having_condition,
            )
        except Exception as e:
            logger.error(f"Error in _fill_query_template: {str(e)}", exc_info=True)
            return None

    def _fill_nl_template(
        self,
        template: str,
        columns: List[str],
        table_name: str,
        available_tables: Optional[Dict[str, List[str]]] = None,
    ) -> Optional[str]:
        try:
            logger = logging.getLogger(__name__)

            # Handle specific columns selection pattern
            if "{columns}" in template:
                if hasattr(self, "selected_columns"):
                    columns_str = ", ".join(self.selected_columns)
                    return template.format(
                        table=table_name,
                        columns=columns_str,
                    )
                logger.warning(
                    "No selected columns found for columns selection pattern"
                )
                return None

            # Format MongoDB condition for natural language display
            condition = self.selected_condition
            if isinstance(condition, str) and condition.startswith("{"):
                try:
                    # Extract operator and value from MongoDB condition
                    import json

                    condition_dict = json.loads(condition.replace("'", '"'))
                    operator = list(condition_dict.values())[
                        0
                    ]  # Get first operator (e.g., "$lt")
                    value = list(operator.values())[0]  # Get the value

                    # Convert MongoDB operators to readable format
                    operator_map = {
                        "$lt": "less than",
                        "$lte": "less than or equal to",
                        "$gt": "greater than",
                        "$gte": "greater than or equal to",
                        "$eq": "equal to",
                        "$ne": "not equal to",
                    }
                    operator_key = list(operator.keys())[
                        0
                    ]  # Get the operator key (e.g., "$lt")
                    readable_operator = operator_map.get(operator_key, "equals")
                    condition = f"{readable_operator} {value}"
                except (
                    json.JSONDecodeError,
                    IndexError,
                    KeyError,
                    AttributeError,
                ) as e:
                    logger.warning(f"Failed to parse MongoDB condition: {e}")
                    # Fall back to original condition if parsing fails
                    pass

            # Use generated conditions and placeholders consistently
            return template.format(
                category=self.selected_category,
                quantity=self.selected_quantity,
                n=self.selected_n,
                condition=condition,
            )
        except Exception as e:
            logger.error(f"Error in _fill_nl_template: {str(e)}", exc_info=True)
            return None

    def _generate_condition(
        self, column: str, numeric_cols: List[str], db_type: DatabaseType
    ) -> str:
        if column in numeric_cols:
            value = random.randint(1, 100)
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
            value = random.randint(40, 50)
            if db_type == DatabaseType.MONGODB:
                return value
            return f"= {value}"

    def _generate_having_condition(self, column: str, db_type: DatabaseType) -> str:
        value = random.randint(10, 200)
        operators = [">", "<", ">=", "<="]
        op = random.choice(operators)

        if db_type == DatabaseType.MONGODB:
            mongo_ops = {
                ">": "$gt",
                "<": "$lt",
                ">=": "$gte",
                "<=": "$lte",
            }
            return f'{{ "{mongo_ops[op]}": {value} }}'
        return f"{op} {value}"
