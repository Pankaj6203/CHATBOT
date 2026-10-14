"""
MongoDB database layer for Nirmla Sweets restaurant chatbot
Uses MongoDB Atlas cloud database
"""

import logging
import os
from datetime import datetime
from typing import List, Dict, Optional, Any
from urllib.parse import quote_plus
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MongoDatabase:
    """MongoDB wrapper for restaurant chatbot data persistence"""
    
    def __init__(self, connection_string: str = None, username: str = None, password: str = None, 
                 database_name: str = "Nirmla_sweets", host: str = None):
        """
        Initialize MongoDB connection
        
        Args:
            connection_string: MongoDB Atlas connection string (will be used as-is)
            username: MongoDB username (if not in connection_string)
            password: MongoDB password (will be URL-encoded)
            database_name: Database name (default: Nirmla_sweets)
            host: MongoDB host/cluster URL
        """
        try:
            # If individual credentials are provided, build the connection string
            if username and password and host and not connection_string:
                encoded_user = quote_plus(username)
                encoded_pass = quote_plus(password)
                connection_string = f"mongodb+srv://{encoded_user}:{encoded_pass}@{host}/?appName=Cluster0"
            elif not connection_string:
                raise ValueError("Either connection_string or (username, password, host) must be provided")
            
            self.client = MongoClient(connection_string, serverSelectionTimeoutMS=20000)
            # Verify connection
            self.client.admin.command('ping')
            self.db = self.client[database_name]
            logger.info("✓ MongoDB connection successful")
            self._initialize_collections()
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"✗ MongoDB connection failed: {e}")
            raise
    
    def _initialize_collections(self):
        """Create collections and indexes if they don't exist"""
        collections = ['menu_items', 'users', 'orders', 'order_items', 'audit_log']
        
        for collection in collections:
            if collection not in self.db.list_collection_names():
                self.db.create_collection(collection)
                logger.info(f"Created collection: {collection}")
        
        # Create indexes for faster queries
        self.db.menu_items.create_index([("item_id", 1)], unique=True, sparse=True)
        self.db.users.create_index([("phone_number", 1)], unique=True)
        self.db.orders.create_index([("order_id", 1)], unique=True)
        self.db.orders.create_index([("phone_number", 1)])
        self.db.order_items.create_index([("order_id", 1)])
        self.db.audit_log.create_index([("phone_number", 1)])
        self.db.audit_log.create_index([("timestamp", -1)])
        
        logger.info("✓ Collections and indexes initialized")
    
    # ==================== MENU OPERATIONS ====================
    
    def insert_menu_items(self, items: List[Dict[str, Any]]) -> int:
        """Insert menu items into database"""
        try:
            # Insert items if they don't exist
            inserted = 0
            for item in items:
                result = self.db.menu_items.update_one(
                    {"item_id": item.get("id", item.get("item_id"))},
                    {"$set": item},
                    upsert=True
                )
                if result.upserted_id:
                    inserted += 1
            logger.info(f"Inserted {inserted} menu items")
            return inserted
        except Exception as e:
            logger.error(f"Error inserting menu items: {e}")
            raise
    
    def get_all_menu_items(self) -> List[Dict]:
        """Get all menu items joined with their categories"""
        try:
            pipeline = [
                {
                    "$lookup": {
                        "from": "categories",
                        "localField": "category_id",
                        "foreignField": "_id",
                        "as": "category_info"
                    }
                },
                {"$unwind": "$category_info"},
                {
                    "$addFields": {
                        "category": "$category_info.name"
                    }
                },
                {"$project": {"category_info": 0, "_id": 0}}
            ]
            items = list(self.db.menu_items.aggregate(pipeline))
            return items
        except Exception as e:
            logger.error(f"Error fetching menu items: {e}")
            return []
    
    def get_menu_item_by_id(self, item_id: int) -> Optional[Dict]:
        """Get menu item by ID"""
        try:
            item = self.db.menu_items.find_one({"item_id": item_id})
            if item:
                item.pop("_id", None)
            return item
        except Exception as e:
            logger.error(f"Error fetching menu item {item_id}: {e}")
            return None
    
    def get_menu_by_category(self, category: str) -> List[Dict]:
        """Get menu items by category"""
        try:
            items = list(self.db.menu_items.find({"category": category}))
            for item in items:
                item.pop("_id", None)
            return items
        except Exception as e:
            logger.error(f"Error fetching items by category: {e}")
            return []
    
    # ==================== USER OPERATIONS ====================
    
    def create_or_update_user(self, phone_number: str, name: str = None) -> Dict:
        """Create or update user"""
        try:
            result = self.db.users.update_one(
                {"phone_number": phone_number},
                {
                    "$set": {
                        "phone_number": phone_number,
                        "name": name or f"User {phone_number}",
                        "last_seen": datetime.now(),
                        "total_orders": 0
                    },
                    "$setOnInsert": {
                        "created_at": datetime.now(),
                        "status": "active"
                    }
                },
                upsert=True
            )
            user = self.db.users.find_one({"phone_number": phone_number})
            user.pop("_id", None)
            return user
        except Exception as e:
            logger.error(f"Error creating/updating user: {e}")
            raise
    
    def get_user(self, phone_number: str) -> Optional[Dict]:
        """Get user by phone number"""
        try:
            user = self.db.users.find_one({"phone_number": phone_number})
            if user:
                user.pop("_id", None)
            return user
        except Exception as e:
            logger.error(f"Error fetching user: {e}")
            return None
    
    # ==================== ORDER OPERATIONS ====================
    
    def create_order(self, order_id: str, phone_number: str, total_amount: float, status: str = "pending") -> Dict:
        """Create new order"""
        try:
            order = {
                "order_id": order_id,
                "phone_number": phone_number,
                "total_amount": total_amount,
                "status": status,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            self.db.orders.insert_one(order)
            order.pop("_id", None)
            logger.info(f"Order created: {order_id}")
            return order
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            raise
    
    def add_order_item(self, order_id: str, item_id: int, item_name: str, 
                      price: float, quantity: int, subtotal: float) -> Dict:
        """Add item to order"""
        try:
            item = {
                "order_id": order_id,
                "item_id": item_id,
                "item_name": item_name,
                "price": price,
                "quantity": quantity,
                "subtotal": subtotal,
                "added_at": datetime.now()
            }
            self.db.order_items.insert_one(item)
            item.pop("_id", None)
            return item
        except Exception as e:
            logger.error(f"Error adding order item: {e}")
            raise
    
    def get_order(self, order_id: str) -> Optional[Dict]:
        """Get order by ID"""
        try:
            order = self.db.orders.find_one({"order_id": order_id})
            if order:
                order.pop("_id", None)
            return order
        except Exception as e:
            logger.error(f"Error fetching order: {e}")
            return None
    
    def get_order_items(self, order_id: str) -> List[Dict]:
        """Get items in order"""
        try:
            items = list(self.db.order_items.find({"order_id": order_id}))
            for item in items:
                item.pop("_id", None)
            return items
        except Exception as e:
            logger.error(f"Error fetching order items: {e}")
            return []
    
    def get_user_orders(self, phone_number: str, limit: int = 10) -> List[Dict]:
        """Get all orders for a user"""
        try:
            orders = list(self.db.orders.find({"phone_number": phone_number}).sort("created_at", -1).limit(limit))
            for order in orders:
                order.pop("_id", None)
            return orders
        except Exception as e:
            logger.error(f"Error fetching user orders: {e}")
            return []
    
    def update_order_status(self, order_id: str, status: str) -> bool:
        """Update order status"""
        try:
            result = self.db.orders.update_one(
                {"order_id": order_id},
                {"$set": {"status": status, "updated_at": datetime.now()}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating order status: {e}")
            return False
    
    # ==================== AUDIT LOG OPERATIONS ====================
    
    def log_action(self, phone_number: str, action: str, details: str = "") -> None:
        """Log user action for audit trail"""
        try:
            log_entry = {
                "phone_number": phone_number,
                "action": action,
                "details": details,
                "timestamp": datetime.now()
            }
            self.db.audit_log.insert_one(log_entry)
        except Exception as e:
            logger.error(f"Error logging action: {e}")
    
    def get_audit_log(self, phone_number: str = None, limit: int = 50) -> List[Dict]:
        """Get audit log entries"""
        try:
            query = {"phone_number": phone_number} if phone_number else {}
            logs = list(self.db.audit_log.find(query).sort("timestamp", -1).limit(limit))
            for log in logs:
                log.pop("_id", None)
            return logs
        except Exception as e:
            logger.error(f"Error fetching audit log: {e}")
            return []
    
    # ==================== ANALYTICS OPERATIONS ====================
    
    def get_total_revenue(self, start_date=None, end_date=None) -> float:
        """Calculate total revenue"""
        try:
            query = {}
            if start_date or end_date:
                query["created_at"] = {}
                if start_date:
                    query["created_at"]["$gte"] = start_date
                if end_date:
                    query["created_at"]["$lte"] = end_date
            
            result = self.db.orders.aggregate([
                {"$match": query},
                {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
            ])
            
            result_list = list(result)
            return result_list[0]["total"] if result_list else 0
        except Exception as e:
            logger.error(f"Error calculating revenue: {e}")
            return 0
    
    def get_top_items(self, limit: int = 5) -> List[Dict]:
        """Get top selling items"""
        try:
            result = self.db.order_items.aggregate([
                {"$group": {
                    "_id": "$item_name",
                    "total_quantity": {"$sum": "$quantity"},
                    "total_revenue": {"$sum": "$subtotal"},
                    "item_id": {"$first": "$item_id"}
                }},
                {"$sort": {"total_quantity": -1}},
                {"$limit": limit}
            ])
            
            items = []
            for item in result:
                item.pop("_id", None)
                items.append(item)
            return items
        except Exception as e:
            logger.error(f"Error fetching top items: {e}")
            return []
    
    def get_order_count(self, status: str = None) -> int:
        """Get count of orders"""
        try:
            query = {"status": status} if status else {}
            return self.db.orders.count_documents(query)
        except Exception as e:
            logger.error(f"Error counting orders: {e}")
            return 0
    
    def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


if __name__ == "__main__":
    # Test connection
    CONNECTION_STRING = os.getenv("MONGODB_URI") or "mongodb+srv://{}:{}@{}/?appName=Cluster0".format(
        quote_plus(os.environ["MONGODB_USERNAME"]), quote_plus(os.environ["MONGODB_PASSWORD"]), os.environ["MONGODB_HOST"])
    
    try:
        db = MongoDatabase(CONNECTION_STRING)
        print("✓ MongoDB connected successfully!")
        
        # Test insert menu items
        sample_items = [
            {'item_id': 1, 'name': 'Gulab Jamun', 'price': 50, 'category': 'Sweets', 'description': 'Sweet milk solids'},
            {'item_id': 2, 'name': 'Jalebi', 'price': 40, 'category': 'Sweets', 'description': 'Crispy sweet'},
        ]
        db.insert_menu_items(sample_items)
        print(f"✓ Menu items: {len(db.get_all_menu_items())}")
        
        db.close()
    except Exception as e:
        print(f"✗ Error: {e}")
