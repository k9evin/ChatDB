from enum import Enum
import re
from typing import List, Dict, Optional, Any
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import logging
import json

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

try:
    nltk.data.find("tokenizers/punkt")
    nltk.data.find("corpora/stopwords")
    nltk.data.find("corpora/wordnet")
except LookupError:
    nltk.download("punkt")
    nltk.download("stopwords")
    nltk.download("wordnet")


class DatabaseType(str, Enum):
    MYSQL = "mysql"
    MONGODB = "mongodb"


class NLPProcessor:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words("english")) - {
            "by",
            "in",
            "with",
            "for",
            "to",
            "of",
            "on",
            "at",
            "where",
            "when",
            "each",
            "from",
            "over",
            "across",
            "top",
            "sum",
            "avg",
            "average",
            "count",
            "total",
            "group",
            "having",
            "select",
            "specific",
            "columns",
            "order",
            "limit",
            "filter",
        }
        self.current_query = ""

        self.query_patterns = {
            "group by with aggregation": {
                "patterns": [
                    r".*?(?:sum|total|average|avg|mean)\s+(?:of\s+)?(\w+).*?(?:by|per|for\s+each)\s+(\w+)",
                    r".*?(?:calculate|find|get|show).*?(?:sum|total|average|avg|mean)\s+(?:of\s+)?(\w+).*?(?:by|per|for\s+each)\s+(\w+)",
                ],
                "mysql_template": "SELECT {group_by}, {agg_func}({aggregate}) FROM {table} GROUP BY {group_by}",
                "mongodb_template": """[
                    { "$group": { 
                        "_id": "${group_by}",
                        "result": { "${agg_func}": "${aggregate}" }
                    }},
                    { "$project": {
                        "_id": 0,
                        "{group_by}": "$_id",
                        "result": 1
                    }}
                ]""",
            },
            "group by with count": {
                "patterns": [
                    r".*?(?:count|number\s+of|how\s+many)\s+(\w+).*?(?:by|per|for\s+each)\s+(\w+)",
                ],
                "mysql_template": "SELECT {group_by}, COUNT(*) as count FROM {table} GROUP BY {group_by}",
                "mongodb_template": """[
                    { "$group": { 
                        "_id": "${group_by}",
                        "count": { "$sum": 1 }
                    }},
                    { "$project": {
                        "_id": 0,
                        "{group_by}": "$_id",
                        "count": 1
                    }}
                ]""",
            },
            "order by with limit": {
                "patterns": [
                    r".*?(?:top|first)\s+(\d+).*?(?:by|sorted|ordered)\s+(?:by\s+)?(\w+)",
                    r".*?(?:order|sort)\s+(?:by\s+)?(\w+).*?(?:top|first|limit)\s+(\d+)",
                ],
                "mysql_template": "SELECT * FROM {table} ORDER BY {order_by} DESC LIMIT {limit}",
                "mongodb_template": """[
                    { "$sort": { "{order_by}": -1 }},
                    { "$limit": {limit} },
                    { "$project": {
                        "_id": 0
                    }}
                ]""",
            },
            "where clause": {
                "patterns": [
                    r".*?where\s+(\w+).*?(?:>|>=|<|<=|!=|=|<>)\s*(\d+)",
                    r".*?where\s+(\w+).*?(?:is|equals?|greater\s+than|less\s+than)\s*(\d+)",
                    r".*?with\s+(\w+).*?(?:>|>=|<|<=|!=|=|<>)\s*(\d+)",
                    r".*?with\s+(\w+).*?(?:is|equals?|greater\s+than|less\s+than)\s*(\d+)",
                ],
                "mysql_template": "SELECT * FROM {table} WHERE {column} {operator} {value}",
                "mongodb_template": """[
                    { "$match": { "{column}": { "${operator}": {value} }}},
                    { "$project": {
                        "_id": 0
                    }}
                ]""",
            },
            "having clause": {
                "patterns": [
                    r".*?(?:group|filter)\s+by\s+(\w+).*?(?:having|where).*?(?:total|sum|count)\s+(?:of\s+)?(\w+).*?(?:>|>=|<|<=|=)\s*(\d+)",
                    r".*?groups?\s+of\s+(\w+).*?(?:having|where).*?(?:total|sum|count)\s+(?:of\s+)?(\w+).*?(?:>|>=|<|<=|=)\s*(\d+)",
                ],
                "mysql_template": "SELECT {group_by}, SUM({aggregate}) as total FROM {table} GROUP BY {group_by} HAVING total {operator} {value}",
                "mongodb_template": """[
                    { "$group": { 
                        "_id": "${group_by}",
                        "total": { "$sum": "${aggregate}" }
                    }},
                    { "$match": {
                        "total": { "${operator}": {value} }
                    }},
                    { "$project": {
                        "_id": 0,
                        "{group_by}": "$_id",
                        "total": 1
                    }}
                ]""",
            },
            "select columns": {
                "patterns": [
                    r".*?(?:select|show|get|display).*?(?:columns?|fields?)?\s*(\w+(?:\s*,\s*\w+)*)",
                    r".*?(?:columns?|fields?)\s+(\w+(?:\s*,\s*\w+)*)",
                ],
                "mysql_template": "SELECT {columns} FROM {table}",
                "mongodb_template": """[
                    { "$project": {
                        "_id": 0,
                        {columns_projection}
                    }}
                ]""",
            },
        }

    def process_query(self, query: str) -> str:
        logger.info(f"Processing raw query: {query}")
        self.current_query = query
        tokens = word_tokenize(query.lower())
        processed_query = " ".join(
            [
                self.lemmatizer.lemmatize(token)
                for token in tokens
                if token not in self.stop_words
            ]
        )
        logger.info(f"Processed query: {processed_query}")
        return processed_query

    def match_query_pattern(self, processed_query: str) -> Optional[str]:
        logger.info(f"Attempting to match query: {processed_query}")
        for pattern_name, pattern_info in self.query_patterns.items():
            for pattern in pattern_info["patterns"]:
                logger.info(f"Trying pattern {pattern_name}: {pattern}")
                if re.search(pattern, processed_query, re.IGNORECASE):
                    logger.info(f"Matched pattern: {pattern_name}")
                    return pattern_name
        logger.warning("No matching pattern found")
        return None

    def extract_query_components(self, query: str, pattern_name: str) -> Dict[str, str]:
        logger.info(f"Extracting components for pattern {pattern_name} from query: {query}")

        if pattern_name not in self.query_patterns:
            logger.error(f"Unknown pattern: {pattern_name}")
            return {}

        for pattern_regex in self.query_patterns[pattern_name]["patterns"]:
            match = re.search(pattern_regex, query, re.IGNORECASE)
            if match:
                logger.info(f"Found match with pattern: {pattern_regex}")
                logger.debug(f"Match groups: {match.groups()}")

                try:
                    if pattern_name == "group by with aggregation":
                        agg_func = (
                            "sum"
                            if any(w in query.lower() for w in ["sum", "total"])
                            else "avg"
                        )
                        components = {
                            "aggregate": match.group(1),
                            "group_by": match.group(2),
                            "agg_func": agg_func,
                        }
                    elif pattern_name == "group by with count":
                        components = {
                            "aggregate": match.group(1),
                            "group_by": match.group(2),
                        }
                    elif pattern_name == "order by with limit":
                        components = {
                            "limit": match.group(1),
                            "order_by": match.group(2),
                        }
                    elif pattern_name == "where clause":
                        components = {
                            "column": match.group(1),
                            "operator": self._extract_operator(query),
                            "value": match.group(2),
                        }
                    elif pattern_name == "having clause":
                        components = {
                            "group_by": match.group(1),
                            "aggregate": match.group(2),
                            "operator": self._extract_operator(query),
                            "value": match.group(3),
                        }
                    elif pattern_name == "select columns":
                        columns = match.group(1).replace(" ", "").split(",")
                        components = {"columns": ", ".join(columns)}

                    logger.info(f"Extracted components: {components}")
                    return components

                except IndexError as e:
                    logger.error(f"Error extracting components: {e}")
                    continue

        logger.warning(f"No components could be extracted from query: {query}")
        return {}

    def validate_columns(self, columns: List[str], required_columns: List[str]) -> bool:
        return all(col in columns for col in required_columns)

    def generate_query(
        self,
        pattern: str,
        table_name: str,
        columns: List[str],
        db_type: str,
    ) -> str:
        logger.info(f"Generating query for pattern: {pattern}")

        if pattern not in self.query_patterns:
            error_msg = f"Unknown pattern: {pattern}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        components = self.extract_query_components(self.current_query, pattern)
        if not components:
            error_msg = "Could not extract query components"
            logger.error(error_msg)
            raise ValueError(error_msg)

        template = (
            self.query_patterns[pattern]["mysql_template"]
            if db_type == "mysql"
            else self.query_patterns[pattern]["mongodb_template"]
        )

        try:
            query = template.replace("{table}", table_name)

            if pattern == "group by with aggregation":
                query = query.replace("{aggregate}", components["aggregate"])
                query = query.replace("{group_by}", components["group_by"])
                query = query.replace("{agg_func}", components["agg_func"])
            elif pattern == "group by with count":
                query = query.replace("{aggregate}", components["aggregate"])
                query = query.replace("{group_by}", components["group_by"])
            elif pattern == "order by with limit":
                query = query.replace("{order_by}", components["order_by"])
                query = query.replace("{limit}", components["limit"])
            elif pattern == "where clause":
                query = query.replace("{column}", components["column"])
                query = query.replace("{operator}", components["operator"])
                query = query.replace("{value}", components["value"])
            elif pattern == "having clause":
                query = query.replace("{group_by}", components["group_by"])
                query = query.replace("{aggregate}", components["aggregate"])
                query = query.replace("{operator}", components["operator"])
                query = query.replace("{value}", components["value"])
            elif pattern == "select columns":
                if db_type == "mysql":
                    query = query.replace("{columns}", components["columns"])
                else:
                    columns_dict = {
                        col.strip(): 1 for col in components["columns"].split(",")
                    }
                    projection_str = ", ".join(f'"{k}": {v}' for k, v in columns_dict.items())
                    query = query.replace(
                        "{columns_projection}", projection_str
                    )

            logger.info(f"Generated query: {query}")
            return query

        except KeyError as e:
            error_msg = f"Missing component in template: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    def _extract_operator(self, operator_text: str) -> str:
        operator_map = {
            ">": ">",
            "greater than": ">",
            ">=": ">=",
            "greater than or equal to": ">=",
            "<": "<",
            "less than": "<",
            "<=": "<=",
            "less than or equal to": "<=",
            "=": "=",
            "equals": "=",
            "equal to": "=",
            "is": "=",
            "!=": "!=",
            "<>": "!=",
            "not equal to": "!=",
            "not equals": "!=",
        }

        operator_text = operator_text.lower()
        for key, value in operator_map.items():
            if key in operator_text:
                return value
        return "="
