"""
SQLite Database Layer for Restaurant Chatbot
Provides ORM-like functionality for menu, orders, and users
"""

import sqlite3
import json
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# ==================== DATABASE CONFIGURATION ====================

DB_PATH = "restaurant_chatbot.db"
DB_SCHEMA_VERSION = 1

# ==================== DATABASE MODELS ====================

class Database:
    """Main database interface"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.init_db()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Access columns by name
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def init_db(self):
        """Initialize database with schema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Menu items table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS menu_items (
                    item_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    price REAL NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT,
                    available BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Users/sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    phone_number TEXT PRIMARY KEY,
                    name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Orders table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    order_id TEXT PRIMARY KEY,
                    phone_number TEXT NOT NULL,
                    total_amount REAL NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (phone_number) REFERENCES users(phone_number)
                )
            """)
            
            # Order items table (items in each order)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS order_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id TEXT NOT NULL,
                    item_id INTEGER NOT NULL,
                    item_name TEXT NOT NULL,
                    price REAL NOT NULL,
                    quantity INTEGER NOT NULL,
                    subtotal REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (order_id) REFERENCES orders(order_id),
                    FOREIGN KEY (item_id) REFERENCES menu_items(item_id)
                )
            """)
            
            # Audit log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone_number TEXT NOT NULL,
                    action TEXT NOT NULL,
                    details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            logger.info("Database initialized successfully")
    
    # ==================== MENU OPERATIONS ====================
    
    def insert_menu_items(self, items: List[Dict]) -> int:
        """Insert multiple menu items (bulk operation)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            inserted = 0
            
            for item in items:
                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO menu_items 
                        (item_id, name, price, category, description, available)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        item.get("id"),
                        item.get("name"),
                        item.get("price"),
                        item.get("category"),
                        item.get("description", ""),
                        item.get("available", True)
                    ))
                    if cursor.rowcount > 0:
                        inserted += 1
                except sqlite3.IntegrityError:
                    pass
            
            logger.info(f"Inserted {inserted} menu items")
            return inserted
    
    def get_all_menu_items(self) -> List[Dict]:
        """Fetch all available menu items"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM menu_items WHERE available = 1
                ORDER BY category, name
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_menu_by_category(self, category: str) -> List[Dict]:
        """Get menu items by category"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM menu_items 
                WHERE category = ? AND available = 1
                ORDER BY name
            """, (category,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_menu_item_by_id(self, item_id: int) -> Optional[Dict]:
        """Get single menu item by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM menu_items WHERE item_id = ?", (item_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_menu_item_by_name(self, name: str) -> Optional[Dict]:
        """Get menu item by name"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM menu_items WHERE name = ? AND available = 1", (name,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    # ==================== USER OPERATIONS ====================
    
    def create_or_update_user(self, phone_number: str, name: Optional[str] = None) -> bool:
        """Create new user or update last interaction"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO users (phone_number, name)
                VALUES (?, ?)
            """, (phone_number, name))
            
            cursor.execute("""
                UPDATE users 
                SET last_interaction = CURRENT_TIMESTAMP
                WHERE phone_number = ?
            """, (phone_number,))
            
            return cursor.rowcount > 0
    
    def get_user(self, phone_number: str) -> Optional[Dict]:
        """Get user by phone number"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE phone_number = ?", (phone_number,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    # ==================== ORDER OPERATIONS ====================
    
    def create_order(self, order_id: str, phone_number: str, total_amount: float) -> bool:
        """Create new order"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO orders (order_id, phone_number, total_amount, status)
                VALUES (?, ?, ?, 'confirmed')
            """, (order_id, phone_number, total_amount))
            return cursor.rowcount > 0
    
    def add_order_item(self, order_id: str, item_id: int, item_name: str, 
                      price: float, quantity: int, subtotal: float) -> bool:
        """Add item to order"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO order_items 
                (order_id, item_id, item_name, price, quantity, subtotal)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (order_id, item_id, item_name, price, quantity, subtotal))
            return cursor.rowcount > 0
    
    def get_order(self, order_id: str) -> Optional[Dict]:
        """Get order details"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_order_items(self, order_id: str) -> List[Dict]:
        """Get all items in an order"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM order_items WHERE order_id = ?
                ORDER BY created_at
            """, (order_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_user_orders(self, phone_number: str, limit: int = 10) -> List[Dict]:
        """Get recent orders for a user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM orders WHERE phone_number = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (phone_number, limit))
            return [dict(row) for row in cursor.fetchall()]
    
    def update_order_status(self, order_id: str, status: str) -> bool:
        """Update order status"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE orders 
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE order_id = ?
            """, (status, order_id))
            return cursor.rowcount > 0
    
    # ==================== AUDIT LOG ====================
    
    def log_action(self, phone_number: str, action: str, details: Optional[str] = None) -> bool:
        """Log user action"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO audit_log (phone_number, action, details)
                VALUES (?, ?, ?)
            """, (phone_number, action, details))
            return cursor.rowcount > 0
    
    def get_audit_log(self, phone_number: Optional[str] = None, 
                     action: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get audit log with optional filters"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM audit_log WHERE 1=1"
            params = []
            
            if phone_number:
                query += " AND phone_number = ?"
                params.append(phone_number)
            
            if action:
                query += " AND action = ?"
                params.append(action)
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    # ==================== ANALYTICS ====================
    
    def get_total_revenue(self, start_date: Optional[str] = None) -> float:
        """Get total revenue from confirmed orders"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT SUM(total_amount) as total FROM orders 
                WHERE status = 'confirmed'
            """
            params = []
            
            if start_date:
                query += " AND created_at >= ?"
                params.append(start_date)
            
            cursor.execute(query, params)
            result = cursor.fetchone()
            return float(result['total']) if result['total'] else 0.0
    
    def get_top_items(self, limit: int = 10) -> List[Dict]:
        """Get most ordered items"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT item_name, SUM(quantity) as total_ordered, 
                       COUNT(DISTINCT order_id) as order_count
                FROM order_items
                GROUP BY item_name
                ORDER BY total_ordered DESC
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_order_count(self) -> int:
        """Get total number of orders"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM orders WHERE status = 'confirmed'")
            return cursor.fetchone()['count']
