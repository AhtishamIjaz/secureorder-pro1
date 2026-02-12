import sqlite3
import os
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

DB_PATH = os.getenv("SQLITE_DB_PATH", "secure_orders.db")

# --- DATA CONTRACTS (Industrial Safety) ---
class OrderRequest(BaseModel):
    customer_id: int = Field(..., description="Unique ID of the customer")
    product_id: int = Field(..., description="ID of the product to buy")
    quantity: int = Field(..., gt=0, lt=50, description="Quantity (Max 50)")

class CancelRequest(BaseModel):
    order_id: int = Field(..., description="The ID of the order to cancel")
    reason: str = Field(..., min_length=10, description="Reason for cancellation")

# --- DATABASE LOGIC ---
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # Allows accessing columns by name
    return conn

def init_robust_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Products Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE,
            price REAL,
            stock INTEGER,
            category TEXT
        )
    """)
    
    # 2. Orders Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            product_id INTEGER,
            status TEXT, 
            order_date TIMESTAMP,
            delivery_date TIMESTAMP,
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    """)

    # Seed Industrial Data
    products = [
        (1, 'Quantum CPU', 1200.00, 45, 'Hardware'),
        (2, 'Neural Link v2', 850.50, 10, 'Neural-Interfaces'),
        (3, 'Security Token', 45.00, 200, 'Security')
    ]
    cursor.executemany("INSERT OR IGNORE INTO products VALUES (?,?,?,?,?)", products)
    conn.commit()
    conn.close()