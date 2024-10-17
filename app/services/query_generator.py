import random


class QueryGeneratorService:
    def __init__(self):
        self.query_patterns = [
            (
                "total {quantity} by {category}",
                "SELECT {category}, SUM({quantity}) FROM {table} GROUP BY {category}",
            ),
            (
                "average {quantity} by {category}",
                "SELECT {category}, AVG({quantity}) FROM {table} GROUP BY {category}",
            ),
            (
                "count by {category}",
                "SELECT {category}, COUNT(*) FROM {table} GROUP BY {category}",
            ),
            (
                "top {n} {quantity}",
                "SELECT * FROM {table} ORDER BY {quantity} DESC LIMIT {n}",
            ),
            (
                "filter {column} {condition}",
                "SELECT * FROM {table} WHERE {column} {condition}",
            ),
        ]

    def generate_sample_queries(self, table_name, columns):
        queries = []
        for _ in range(5):  # Generate 5 sample queries
            pattern, query_template = random.choice(self.query_patterns)
            query = self._fill_query_template(query_template, table_name, columns)
            nl_query = self._fill_nl_template(pattern, columns)
            queries.append({"natural_language": nl_query, "sql_query": query})
        return queries

    def _fill_query_template(self, template, table_name, columns):
        numeric_cols = [
            col for col in columns if col.lower().endswith(("amount", "qty", "price"))
        ]
        categorical_cols = [col for col in columns if col not in numeric_cols]

        return template.format(
            table=table_name,
            category=(
                random.choice(categorical_cols)
                if categorical_cols
                else random.choice(columns)
            ),
            quantity=(
                random.choice(numeric_cols) if numeric_cols else random.choice(columns)
            ),
            column=random.choice(columns),
            condition="= 'some_value'",
            n=random.randint(3, 10),
        )

    def _fill_nl_template(self, template, columns):
        numeric_cols = [
            col for col in columns if col.lower().endswith(("amount", "qty", "price"))
        ]
        categorical_cols = [col for col in columns if col not in numeric_cols]

        return template.format(
            category=(
                random.choice(categorical_cols)
                if categorical_cols
                else random.choice(columns)
            ),
            quantity=(
                random.choice(numeric_cols) if numeric_cols else random.choice(columns)
            ),
            column=random.choice(columns),
            n=random.randint(3, 10),
            condition="some condition",
        )
