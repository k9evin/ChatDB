"""RAG implementation for semantic schema matching using vector embeddings."""

from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings
from typing import Dict, Any, List
from functools import lru_cache
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from backend.database.connection import get_db_manager
from backend.config.settings import get_settings


# Cache for table embeddings to avoid repeated API calls
_schema_embeddings_cache: Dict[str, Any] = {}


def _get_table_descriptions() -> Dict[str, str]:
    """
    Get descriptions for all tables in the format: "table_name: column1, column2, ..."
    
    Returns:
        Dictionary mapping table names to their descriptions
    """
    db_manager = get_db_manager()
    inspector = db_manager.get_inspector()
    tables = inspector.get_table_names()
    
    descriptions = {}
    for table in tables:
        columns = inspector.get_columns(table)
        column_names = [col["name"] for col in columns]
        descriptions[table] = f"{table}: {', '.join(column_names)}"
    
    return descriptions


def _get_cached_embeddings() -> tuple[List[np.ndarray], List[str]]:
    """
    Get cached table embeddings or create new ones.
    
    Returns:
        Tuple of (embeddings list, table names list)
    """
    cache_key = "all_tables"
    
    if cache_key not in _schema_embeddings_cache:
        settings = get_settings()
        
        # Initialize embeddings
        # Note: OpenAI embeddings work with OpenRouter API key
        embeddings_model = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openrouter_api_key,
            openai_api_base="https://openrouter.ai/api/v1" if settings.embedding_provider == "openrouter" else None
        )
        
        # Get table descriptions
        table_descriptions = _get_table_descriptions()
        table_names = list(table_descriptions.keys())
        descriptions = list(table_descriptions.values())
        
        # Create embeddings
        table_embeddings = embeddings_model.embed_documents(descriptions)
        
        # Store in cache
        _schema_embeddings_cache[cache_key] = {
            "embeddings": table_embeddings,
            "table_names": table_names,
            "descriptions": descriptions
        }
    
    cache_data = _schema_embeddings_cache[cache_key]
    return cache_data["embeddings"], cache_data["table_names"], cache_data["descriptions"]


@tool
def search_relevant_tables(query: str) -> Dict[str, Any]:
    """
    Use vector embeddings to find relevant tables based on user query.
    
    Process:
    1. Get all tables and build descriptions (table_name: column1, column2, ...)
    2. Create embeddings for table descriptions (cache results)
    3. Embed user query
    4. Calculate cosine similarity
    5. Return top 3 relevant tables with scores
    
    Args:
        query: User's natural language query
        
    Returns:
        {
            "relevant_tables": [
                {
                    "table": "orders",
                    "relevance_score": 0.87,
                    "description": "orders: order_id, customer_id, amount, order_date"
                },
                {
                    "table": "customers",
                    "relevance_score": 0.76,
                    "description": "customers: id, name, email, created_at"
                }
            ],
            "query": "show me customer orders from last month"
        }
    """
    try:
        settings = get_settings()
        
        # Get cached embeddings
        table_embeddings, table_names, descriptions = _get_cached_embeddings()
        
        if not table_embeddings:
            return {
                "relevant_tables": [],
                "query": query,
                "error": "No tables found in database"
            }
        
        # Initialize embeddings model
        # Note: OpenAI embeddings work with OpenRouter API key
        embeddings_model = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openrouter_api_key,
            openai_api_base="https://openrouter.ai/api/v1" if settings.embedding_provider == "openrouter" else None
        )
        
        # Embed user query
        query_embedding = embeddings_model.embed_query(query)
        
        # Calculate cosine similarity
        similarities = cosine_similarity(
            [query_embedding],
            table_embeddings
        )[0]
        
        # Get top 3 results with score > 0.3
        results = []
        for idx, score in enumerate(similarities):
            if score > 0.3:
                results.append({
                    "table": table_names[idx],
                    "relevance_score": float(score),
                    "description": descriptions[idx]
                })
        
        # Sort by relevance score (descending) and take top 3
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        top_results = results[:3]
        
        return {
            "relevant_tables": top_results,
            "query": query
        }
    except Exception as e:
        return {
            "relevant_tables": [],
            "query": query,
            "error": str(e)
        }

