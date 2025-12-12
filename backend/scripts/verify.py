"""Verification script to test the entire ChatDB setup."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def check_imports():
    """Check if all required modules can be imported."""
    print("Checking imports...")
    errors = []
    
    try:
        import fastapi
        print("  ✓ fastapi")
    except ImportError as e:
        errors.append(f"  ✗ fastapi: {e}")
    
    try:
        import langchain
        print("  ✓ langchain")
    except ImportError as e:
        errors.append(f"  ✗ langchain: {e}")
    
    try:
        import langgraph
        print("  ✓ langgraph")
    except ImportError as e:
        errors.append(f"  ✗ langgraph: {e}")
    
    try:
        import sqlalchemy
        print("  ✓ sqlalchemy")
    except ImportError as e:
        errors.append(f"  ✗ sqlalchemy: {e}")
    
    try:
        import openai
        print("  ✓ openai")
    except ImportError as e:
        errors.append(f"  ✗ openai: {e}")
    
    try:
        import sklearn
        print("  ✓ scikit-learn")
    except ImportError as e:
        errors.append(f"  ✗ scikit-learn: {e}")
    
    try:
        import sqlparse
        print("  ✓ sqlparse")
    except ImportError as e:
        errors.append(f"  ✗ sqlparse: {e}")
    
    if errors:
        print("\nImport errors:")
        for error in errors:
            print(error)
        return False
    
    print("  ✓ All imports successful!")
    return True


def check_backend_modules():
    """Check if backend modules can be imported."""
    print("\nChecking backend modules...")
    errors = []
    
    try:
        from backend.config.settings import get_settings
        print("  ✓ backend.config.settings")
    except Exception as e:
        errors.append(f"  ✗ backend.config.settings: {e}")
    
    try:
        from backend.database.connection import get_db_manager
        print("  ✓ backend.database.connection")
    except Exception as e:
        errors.append(f"  ✗ backend.database.connection: {e}")
    
    try:
        from backend.agent.graph import create_agent_graph
        print("  ✓ backend.agent.graph")
    except Exception as e:
        errors.append(f"  ✗ backend.agent.graph: {e}")
    
    try:
        from backend.tools.database import get_all_tables
        print("  ✓ backend.tools.database")
    except Exception as e:
        errors.append(f"  ✗ backend.tools.database: {e}")
    
    try:
        from backend.tools.rag import search_relevant_tables
        print("  ✓ backend.tools.rag")
    except Exception as e:
        errors.append(f"  ✗ backend.tools.rag: {e}")
    
    try:
        from backend.tools.validation import validate_sql_syntax
        print("  ✓ backend.tools.validation")
    except Exception as e:
        errors.append(f"  ✗ backend.tools.validation: {e}")
    
    try:
        from backend.tools.execution import execute_sql_query
        print("  ✓ backend.tools.execution")
    except Exception as e:
        errors.append(f"  ✗ backend.tools.execution: {e}")
    
    if errors:
        print("\nBackend module errors:")
        for error in errors:
            print(error)
        return False
    
    print("  ✓ All backend modules imported successfully!")
    return True


def check_config():
    """Check configuration."""
    print("\nChecking configuration...")
    try:
        from backend.config.settings import get_settings
        settings = get_settings()
        
        if not settings.openrouter_api_key or settings.openrouter_api_key == "sk-or-v1-your-key-here":
            print("  ⚠️  OPENROUTER_API_KEY not set (using default)")
        else:
            print("  ✓ OPENROUTER_API_KEY is set")
        
        print(f"  ✓ Database URL: {settings.database_url}")
        print(f"  ✓ Model: {settings.openrouter_model}")
        
        return True
    except Exception as e:
        print(f"  ✗ Configuration error: {e}")
        return False


def check_database():
    """Check database connection."""
    print("\nChecking database...")
    try:
        from backend.database.connection import get_db_manager
        db_manager = get_db_manager()
        
        # Try to get tables
        inspector = db_manager.get_inspector()
        tables = inspector.get_table_names()
        
        if tables:
            print(f"  ✓ Database connected ({len(tables)} tables found)")
            print(f"    Tables: {', '.join(tables)}")
        else:
            print("  ⚠️  Database connected but no tables found")
            print("    Run: uv run python -m backend.database.sample_data")
        
        return True
    except Exception as e:
        print(f"  ✗ Database error: {e}")
        print("    Run: uv run python -m backend.database.sample_data")
        return False


def check_agent_graph():
    """Check if agent graph can be created."""
    print("\nChecking agent graph...")
    try:
        from backend.agent.graph import create_agent_graph
        graph = create_agent_graph()
        print("  ✓ Agent graph created successfully!")
        return True
    except Exception as e:
        print(f"  ✗ Agent graph error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("ChatDB Backend Verification")
    print("=" * 60)
    print()
    
    results = []
    
    results.append(("Imports", check_imports()))
    results.append(("Backend Modules", check_backend_modules()))
    results.append(("Configuration", check_config()))
    results.append(("Database", check_database()))
    results.append(("Agent Graph", check_agent_graph()))
    
    print()
    print("=" * 60)
    print("Verification Summary")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 All checks passed! The backend is ready to use.")
        print("\nStart the server with:")
        print("  uv run python -m backend.main")
    else:
        print("⚠️  Some checks failed. Please fix the errors above.")
        print("\nCommon fixes:")
        print("  1. Install dependencies: uv sync")
        print("  2. Create sample database: uv run python -m backend.database.sample_data")
        print("  3. Set OPENROUTER_API_KEY in .env file")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

