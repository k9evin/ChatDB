"""Create sample database with realistic data for demo purposes."""

from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
from typing import Optional
import os
from pathlib import Path
from backend.config.settings import get_settings


def create_sample_database(database_url: Optional[str] = None):
    """Create SQLite database with full sample tables for demo (22 tables)."""
    settings = get_settings()
    db_url = database_url or settings.database_url

    engine = create_engine(db_url, connect_args={"check_same_thread": False})

    # Try to load full database from SQL file
    sql_file = Path(__file__).parent / "full_database.sql"

    if sql_file.exists():
        # Load and execute full database SQL
        with open(sql_file, "r", encoding="utf-8") as f:
            sql_content = f.read()

        # Execute the SQL dump
        with engine.begin() as conn:
            # Disable foreign key checks temporarily
            conn.execute(text("PRAGMA foreign_keys=OFF"))

            # Split SQL into individual statements
            # SQLite dump format: statements end with semicolon
            # Remove transaction control statements
            sql_clean = (
                sql_content.replace("PRAGMA foreign_keys=OFF;", "")
                .replace("BEGIN TRANSACTION;", "")
                .replace("COMMIT;", "")
            )

            # Split by semicolon, but keep multi-line statements together
            statements = []
            current = []

            for line in sql_clean.split("\n"):
                stripped = line.strip()
                if not stripped:
                    continue

                current.append(stripped)
                # If line ends with semicolon, complete the statement
                if stripped.endswith(";"):
                    statement = " ".join(current).rstrip(";").strip()
                    if statement:
                        statements.append(statement)
                    current = []

            # Execute all statements
            for statement in statements:
                try:
                    conn.execute(text(statement))
                except Exception as e:
                    # Ignore errors for existing tables/data (expected when re-running)
                    error_str = str(e).lower()
                    if (
                        "already exists" not in error_str
                        and "unique constraint" not in error_str
                        and "no such table" not in error_str
                    ):
                        # Log unexpected errors for debugging
                        print(f"SQL execution warning: {e}")

            # Re-enable foreign key checks
            conn.execute(text("PRAGMA foreign_keys=ON"))

        print(f"Full sample database (22 tables) created successfully at {db_url}")
    else:
        # Fallback to simple database if SQL file not found
        print(f"Warning: full_database.sql not found, creating simple database")
        _create_simple_database(engine, db_url)

    return engine


def _create_simple_database(engine, db_url):
    """Fallback: Create simple database with 4 tables."""
    with engine.begin() as conn:
        # Create customers table
        conn.execute(
            text(
                """
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                created_at DATE NOT NULL
            )
        """
            )
        )

        # Insert sample customers
        conn.execute(
            text(
                """
            INSERT OR REPLACE INTO customers (id, name, email, created_at) VALUES
            (1, 'Alice Johnson', 'alice@example.com', '2024-01-15'),
            (2, 'Bob Smith', 'bob@example.com', '2024-02-20'),
            (3, 'Carol White', 'carol@example.com', '2024-03-10'),
            (4, 'David Brown', 'david@example.com', '2024-04-05'),
            (5, 'Eva Davis', 'eva@example.com', '2024-05-12')
        """
            )
        )

        # Create orders table with foreign key
        conn.execute(
            text(
                """
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY,
                customer_id INTEGER NOT NULL,
                amount DECIMAL(10, 2) NOT NULL,
                order_date DATE NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        """
            )
        )

        # Insert sample orders
        conn.execute(
            text(
                """
            INSERT OR REPLACE INTO orders (order_id, customer_id, amount, order_date, status) VALUES
            (101, 1, 150.00, '2024-11-01', 'completed'),
            (102, 2, 200.00, '2024-11-05', 'completed'),
            (103, 1, 75.50, '2024-11-10', 'pending'),
            (104, 3, 300.00, '2024-11-12', 'completed'),
            (105, 2, 125.75, '2024-11-15', 'completed'),
            (106, 4, 89.99, '2024-11-18', 'pending'),
            (107, 5, 250.00, '2024-11-20', 'completed')
        """
            )
        )

        # Create products table
        conn.execute(
            text(
                """
            CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                stock INTEGER NOT NULL
            )
        """
            )
        )

        # Insert sample products
        conn.execute(
            text(
                """
            INSERT OR REPLACE INTO products (product_id, name, category, price, stock) VALUES
            (1, 'Laptop Pro', 'Electronics', 1299.99, 15),
            (2, 'Wireless Mouse', 'Electronics', 29.99, 50),
            (3, 'Office Chair', 'Furniture', 199.99, 20),
            (4, 'Desk Lamp', 'Furniture', 49.99, 30),
            (5, 'Notebook Set', 'Stationery', 19.99, 100),
            (6, 'Pen Set', 'Stationery', 9.99, 200)
        """
            )
        )

        # Create order_items table
        conn.execute(
            text(
                """
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(order_id),
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            )
        """
            )
        )

        # Insert sample order items
        conn.execute(
            text(
                """
            INSERT OR REPLACE INTO order_items (id, order_id, product_id, quantity, price) VALUES
            (1, 101, 1, 1, 1299.99),
            (2, 101, 2, 2, 29.99),
            (3, 102, 3, 1, 199.99),
            (4, 103, 5, 3, 19.99),
            (5, 104, 1, 1, 1299.99),
            (6, 104, 4, 1, 49.99),
            (7, 105, 2, 4, 29.99),
            (8, 106, 6, 9, 9.99),
            (9, 107, 3, 1, 199.99),
            (10, 107, 4, 1, 49.99)
        """
            )
        )

    print(f"Simple sample database created successfully at {db_url}")


if __name__ == "__main__":
    create_sample_database()
