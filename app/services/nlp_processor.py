import random
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

nltk.download("punkt_tab")
nltk.download("stopwords")
nltk.download("wordnet")


class NLPProcessor:
    def __init__(self):
        self.stop_words = set(stopwords.words("english"))
        self.lemmatizer = WordNetLemmatizer()
        self.query_patterns = {
            "total_by": ["total", "sum", "by", "group"],
            "average_by": ["average", "mean", "by", "group"],
            "count_by": ["count", "number", "by", "group"],
            "top_n": ["top", "highest", "best"],
            "filter": ["where", "condition", "filter"],
        }

    def process_query(self, query):
        tokens = word_tokenize(query.lower())
        tokens = [
            self.lemmatizer.lemmatize(token)
            for token in tokens
            if token not in self.stop_words
        ]
        return tokens

    def match_query_pattern(self, processed_query):
        for pattern, keywords in self.query_patterns.items():
            if any(keyword in processed_query for keyword in keywords):
                return pattern
        return None

    def generate_sql_query(self, pattern, table_name, columns):
        numeric_cols = [
            col for col in columns if col.lower().endswith(("amount", "qty", "price"))
        ]
        categorical_cols = [col for col in columns if col not in numeric_cols]

        if pattern == "total_by":
            return f"SELECT {random.choice(categorical_cols)}, SUM({random.choice(numeric_cols)}) FROM {table_name} GROUP BY {random.choice(categorical_cols)}"
        elif pattern == "average_by":
            return f"SELECT {random.choice(categorical_cols)}, AVG({random.choice(numeric_cols)}) FROM {table_name} GROUP BY {random.choice(categorical_cols)}"
        elif pattern == "count_by":
            return f"SELECT {random.choice(categorical_cols)}, COUNT(*) FROM {table_name} GROUP BY {random.choice(categorical_cols)}"
        elif pattern == "top_n":
            return f"SELECT * FROM {table_name} ORDER BY {random.choice(numeric_cols)} DESC LIMIT 5"
        elif pattern == "filter":
            return f"SELECT * FROM {table_name} WHERE {random.choice(columns)} = 'some_value'"
        else:
            return None
