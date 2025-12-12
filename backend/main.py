"""Main entry point for the ChatDB backend."""

import uvicorn
from backend.api.main import app
from backend.config.settings import get_settings

if __name__ == "__main__":
    settings = get_settings()
    
    # Create sample database if it doesn't exist
    from backend.database.sample_data import create_sample_database
    try:
        create_sample_database()
    except Exception as e:
        print(f"Note: Could not create sample database: {e}")
    
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug,
        reload_dirs=["backend"],
    )

