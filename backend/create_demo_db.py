#!/usr/bin/env python3
"""Standalone script to create the demo database directly."""

import sys
import os
from sqlalchemy import create_engine, text

# Default database path - relative to backend directory
DEFAULT_DB_PATH = "demo_database.db"
DEFAULT_DB_URL = f"sqlite:///{DEFAULT_DB_PATH}"


def create_sample_database(database_url: str = None):
    """
    Create SQLite database with sample tables for demo.
    
    Tables:
    - customers: id, name, email, created_at
    - orders: order_id, customer_id, amount, order_date, status
    - products: product_id, name, category, price, stock
    - order_items: id, order_id, product_id, quantity, price
    """
    db_url = database_url or DEFAULT_DB_URL
    
    print(f"Creating sample database at: {db_url}")
    
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    
    with engine.begin() as conn:
        # Create customers table
        print("Creating customers table...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                created_at DATE NOT NULL
            )
        """))
        
        # Insert sample customers
        print("Inserting sample customers...")
        conn.execute(text("""
            INSERT OR REPLACE INTO customers (id, name, email, created_at) VALUES
            (1, 'Alice Johnson', 'alice@example.com', '2024-01-15'),
            (2, 'Bob Smith', 'bob@example.com', '2024-02-20'),
            (3, 'Carol White', 'carol@example.com', '2024-03-10'),
            (4, 'David Brown', 'david@example.com', '2024-04-05'),
            (5, 'Eva Davis', 'eva@example.com', '2024-05-12')
        """))
        
        # Create orders table with foreign key
        print("Creating orders table...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY,
                customer_id INTEGER NOT NULL,
                amount DECIMAL(10, 2) NOT NULL,
                order_date DATE NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        """))
        
        # Insert sample orders
        print("Inserting sample orders...")
        conn.execute(text("""
            INSERT OR REPLACE INTO orders (order_id, customer_id, amount, order_date, status) VALUES
            (101, 1, 150.00, '2024-11-01', 'completed'),
            (102, 2, 200.00, '2024-11-05', 'completed'),
            (103, 1, 75.50, '2024-11-10', 'pending'),
            (104, 3, 300.00, '2024-11-12', 'completed'),
            (105, 2, 125.75, '2024-11-15', 'completed'),
            (106, 4, 89.99, '2024-11-18', 'pending'),
            (107, 5, 250.00, '2024-11-20', 'completed')
        """))
        
        # Create products table
        print("Creating products table...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                stock INTEGER NOT NULL
            )
        """))
        
        # Insert sample products
        print("Inserting sample products...")
        conn.execute(text("""
            INSERT OR REPLACE INTO products (product_id, name, category, price, stock) VALUES
            (1, 'Laptop Pro', 'Electronics', 1299.99, 15),
            (2, 'Wireless Mouse', 'Electronics', 29.99, 50),
            (3, 'Office Chair', 'Furniture', 199.99, 20),
            (4, 'Desk Lamp', 'Furniture', 49.99, 30),
            (5, 'Notebook Set', 'Stationery', 19.99, 100),
            (6, 'Pen Set', 'Stationery', 9.99, 200)
        """))
        
        # Create order_items table
        print("Creating order_items table...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(order_id),
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            )
        """))
        
        # Insert sample order items
        print("Inserting sample order items...")
        conn.execute(text("""
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
        """))
    
    # Get absolute path for display
    abs_path = os.path.abspath(DEFAULT_DB_PATH)
    print(f"\n✅ Sample database created successfully!")
    print(f"   Location: {abs_path}")
    print(f"   Connection string: sqlite:///./demo_database.db")
    print(f"\n📊 Database contains:")
    print(f"   - customers table (5 records)")
    print(f"   - orders table (7 records)")
    print(f"   - products table (6 records)")
    print(f"   - order_items table (10 records)")
    
    return engine


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Create demo database for ChatDB")
    parser.add_argument(
        "--db-url",
        type=str,
        default=None,
        help="Database URL (default: sqlite:///./demo_database.db)"
    )
    
    args = parser.parse_args()
    
    try:
        create_sample_database(args.db_url)
        print("\n✨ You can now use this database in ChatDB!")
        print("   In the frontend, select 'Demo Database' from the Database Connection menu.")
    except Exception as e:
        print(f"\n❌ Error creating database: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

