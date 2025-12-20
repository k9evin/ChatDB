"""Setup script to initialize the ChatDB backend."""

import os
import sys
import subprocess
from pathlib import Path


def check_uv_installed():
    """Check if uv is installed."""
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def create_env_file():
    """Create .env file from .env.example if it doesn't exist."""
    env_path = Path(__file__).parent / ".env"
    env_example_path = Path(__file__).parent / ".env.example"

    if env_path.exists():
        print(f"✓ .env file already exists at {env_path}")
        return

    if not env_example_path.exists():
        print("Creating .env.example file...")
        env_example_content = """# OpenRouter Configuration
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_MODEL=kwaipilot/kat-coder-pro:free
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Embedding Configuration
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_PROVIDER=openai

# Database Configuration
DATABASE_URL=sqlite:///./demo_database.db

# LangSmith (Optional)
LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=
LANGCHAIN_PROJECT=ChatDB-Agent

# Agent Configuration
MAX_RETRIES=3
TEMPERATURE=0.0
MAX_CONTEXT_LENGTH=128000

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=true
CORS_ORIGINS=https://chatdb-frontend.vercel.app,http://localhost:3000
"""
        env_example_path.write_text(env_example_content)

    print(f"Creating .env file from {env_example_path}...")
    env_content = env_example_path.read_text()
    env_path.write_text(env_content)
    print(f"✓ .env file created at {env_path}")
    print("⚠️  Please update OPENROUTER_API_KEY with your actual API key!")


def create_sample_database():
    """Create sample database."""
    try:
        from backend.database.sample_data import create_sample_database

        print("Creating sample database...")
        create_sample_database()
        print("✓ Sample database created successfully!")
    except Exception as e:
        print(f"⚠️  Error creating sample database: {e}")
        print("You can create it manually later by running:")
        print("  uv run python -m backend.database.sample_data")


if __name__ == "__main__":
    print("=" * 50)
    print("Setting up ChatDB backend...")
    print("=" * 50)
    print()

    # Check for uv
    if check_uv_installed():
        print("✓ uv is installed")
    else:
        print("⚠️  uv is not installed. Installing...")
        print("   Run: curl -LsSf https://astral.sh/uv/install.sh | sh")
        print("   Or: pip install uv")
        print()

    # Create .env file
    create_env_file()
    print()

    # Create sample database
    create_sample_database()
    print()

    print("=" * 50)
    print("Setup complete!")
    print("=" * 50)
    print()
    print("Next steps:")
    print("1. Update .env file with your OPENROUTER_API_KEY")
    if check_uv_installed():
        print("2. Install dependencies: uv sync")
        print("3. Start the server: uv run python -m backend.main")
    else:
        print("2. Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh")
        print("3. Install dependencies: uv sync")
        print("4. Start the server: uv run python -m backend.main")
