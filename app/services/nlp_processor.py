from enum import Enum
import re
from typing import List, Dict, Optional, Any
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import logging

# Configure logging at the top of the file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')

class DatabaseType(str, Enum):
    MYSQL = "mysql"
    MONGODB = "mongodb"

class NLPProcessor:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        # Define stopwords but exclude important query words
        self.stop_words = set(stopwords.words('english')) - {
            'by', 'in', 'with', 'for', 'to', 'of', 'on', 'at', 
            'where', 'when', 'each', 'from', 'over', 'across'
        }
        self.current_query = ""  # Add this to store the current query
        
        # Define query patterns with their corresponding templates
        self.query_patterns = {
            "total_by": {
                "patterns": [
                    r"(?:find|get|show|display|calculate|what is)?\s*(?:the)?\s*(?:total|sum|aggregate)\s+(?:of\s+)?(\w+)\s+(?:by|per|for\s+each|grouped\s+by|across|over|based\s+on)\s+(\w+)",
                    r"(?:group|aggregate|break\s+down)\s+(\w+)\s+(?:total|sum)\s+(?:by|per|for\s+each|across|over)\s+(\w+)",
                    r"(?:total|sum)\s+(?:of\s+)?(\w+)\s+(?:by|per|across|over|grouped\s+by)\s+(\w+)",
                    r"(?:total|sum)\s+(\w+)\s+(?:in|for)\s+each\s+(\w+)",
                    r"(?:by|per|for|across|over)\s+(\w+)\s+(?:show|display|get)\s+(?:total|sum)\s+(?:of\s+)?(\w+)",
                ],
                "mysql_template": "SELECT {group_by}, SUM({aggregate}) FROM {table} GROUP BY {group_by}",
                "mongodb_template": '[{"$group": {"_id": "${group_by}", "total": {"$sum": "${aggregate}"}}}]'
            },
            "count_by": {
                "patterns": [
                    r"(?:count|number\s+of|total\s+number\s+of)\s+(\w+)\s+(?:by|per|for\s+each|grouped\s+by|across|over)\s+(\w+)",
                    r"(?:how\s+many)\s+(\w+)\s+(?:for\s+each|by|per|in\s+each|across|over)\s+(\w+)",
                    r"(?:distribution\s+of)\s+(\w+)\s+(?:by|across|over|per)\s+(\w+)",
                    r"(?:frequency\s+of)\s+(\w+)\s+(?:by|per|across)\s+(\w+)",
                    r"count\s+(\w+)\s+(?:in|by|per|for)\s+(\w+)",
                ],
                "mysql_template": "SELECT {group_by}, COUNT({aggregate}) as count FROM {table} GROUP BY {group_by}",
                "mongodb_template": '[{"$group": {"_id": "${group_by}", "count": {"$sum": 1}}}]'
            },
            "order_limit": {
                "patterns": [
                    r"(?:top|first|show\s+top|get\s+top)\s+(\d+)\s+(\w+)\s+(?:by|ordered\s+by|sorted\s+by|based\s+on)\s+(\w+)",
                    r"(?:find|get|show|display)\s+(\d+)\s+(?:highest|largest|biggest|most|maximum)\s+(\w+)",
                    r"(?:highest|largest|biggest|maximum)\s+(\d+)\s+(\w+)\s+(?:by|based\s+on)\s+(\w+)",
                    r"(?:limit)\s+(?:to\s+)?(\d+)\s+(?:highest|largest|biggest)\s+(\w+)",
                ],
                "mysql_template": "SELECT * FROM {table} ORDER BY {order_by} DESC LIMIT {limit}",
                "mongodb_template": '[{"$sort": {"{order_by}": -1}}, {"$limit": {limit}}]'
            },
            "where_clause": {
                "patterns": [
                    r"(?:find|get|show|display|select)\s+(\w+)\s+(?:where|when|with)\s+(\w+)\s+(?:is|equals|=|equal\s+to|matches)\s+(\w+)",
                    r"(?:find|get|show|display|select)\s+(\w+)\s+(?:for|with)\s+(\w+)\s+(?:is|equals|=|equal\s+to|matches)\s+(\w+)",
                    r"(?:where|when)\s+(\w+)\s+(?:is|equals|=|equal\s+to|matches)\s+(\w+)\s+(?:show|get|find|display)\s+(\w+)",
                    r"(?:filter)\s+(\w+)\s+(?:where|by|with)\s+(\w+)\s+(?:is|equals|=|equal\s+to|matches)\s+(\w+)",
                ],
                "mysql_template": "SELECT {select_column} FROM {table} WHERE {condition_column} = '{condition_value}'",
                "mongodb_template": '[{"$match": {"{condition_column}": "{condition_value}"}}]'
            }
        }

    def process_query(self, query: str) -> str:
        """Process the natural language query by removing stopwords (except important ones) and lemmatizing"""
        logger.info(f"Processing raw query: {query}")
        self.current_query = query  # Store the original query
        tokens = word_tokenize(query.lower())
        # Keep important words even if they're stopwords
        processed_query = ' '.join([
            self.lemmatizer.lemmatize(token) 
            for token in tokens 
            if token not in self.stop_words
        ])
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
        """Extract components from the query based on the pattern name"""
        logger.info(f"Extracting components for pattern {pattern_name} from query: {query}")
        
        if pattern_name not in self.query_patterns:
            logger.error(f"Unknown pattern: {pattern_name}")
            return {}

        for pattern_regex in self.query_patterns[pattern_name]["patterns"]:
            logger.debug(f"Trying regex pattern: {pattern_regex}")
            match = re.search(pattern_regex, query, re.IGNORECASE)
            if match:
                logger.info(f"Found match with pattern: {pattern_regex}")
                logger.debug(f"Match groups: {match.groups()}")
                
                try:
                    if pattern_name == "total_by":
                        components = {
                            "aggregate": match.group(1),
                            "group_by": match.group(2)
                        }
                    elif pattern_name == "count_by":
                        components = {
                            "aggregate": match.group(1),
                            "group_by": match.group(2)
                        }
                    elif pattern_name == "order_limit":
                        components = {
                            "limit": match.group(1),
                            "column": match.group(2),
                            "order_by": match.group(3) if len(match.groups()) > 2 else match.group(2)
                        }
                    elif pattern_name == "where_clause":
                        components = {
                            "select_column": match.group(1),
                            "condition_column": match.group(2),
                            "condition_value": match.group(3)
                        }
                    
                    logger.info(f"Extracted components: {components}")
                    return components
                    
                except IndexError as e:
                    logger.error(f"Error extracting components: {e}")
                    continue
        
        logger.warning(f"No components could be extracted from query: {query}")
        return {}

    def validate_columns(self, columns: List[str], required_columns: List[str]) -> bool:
        """Validate that all required columns exist in the table"""
        return all(col in columns for col in required_columns)

    def generate_query(
        self,
        pattern: str,
        table_name: str,
        columns: List[str],
        db_type: str,
        available_tables: Dict[str, List[str]]
    ) -> str:
        """Generate a database query based on the matched pattern and table schema"""
        logger.info(f"Generating query for pattern: {pattern}")
        
        if pattern not in self.query_patterns:
            error_msg = f"Unknown pattern: {pattern}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Extract components from the original query stored in the pattern
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
            # Replace placeholders with actual values
            query = template.replace("{table}", table_name)
            
            # Replace components based on pattern type
            if pattern == "total_by":
                query = query.replace("{aggregate}", components["aggregate"])
                query = query.replace("{group_by}", components["group_by"])
            elif pattern == "count_by":
                query = query.replace("{aggregate}", components["aggregate"])
                query = query.replace("{group_by}", components["group_by"])
            elif pattern == "order_limit":
                query = query.replace("{order_by}", components["order_by"])
                query = query.replace("{limit}", components["limit"])
            elif pattern == "where_clause":
                query = query.replace("{select_column}", components["select_column"])
                query = query.replace("{condition_column}", components["condition_column"])
                query = query.replace("{condition_value}", components["condition_value"])
            
            logger.info(f"Generated query: {query}")
            return query
            
        except KeyError as e:
            error_msg = f"Missing component in template: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
