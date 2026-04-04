"""
Production-grade WhatsApp Restaurant Chatbot
Author: Senior Backend Developer
Features: Dynamic menu, cart management, order processing, session handling
"""

import json
import logging
import re
from typing import Dict, List, Optional, Tuple, Union, Any
from datetime import datetime
from enum import Enum

# ==================== CONFIGURATION ====================
logging.basicConfig(
    filename='chatbot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ==================== DATA STRUCTURES ====================

class UserState(Enum):
    """Enumeration for conversation states"""
    WELCOME = "welcome"
    SELECTING_CATEGORY = "selecting_category"
    SELECTING_ITEM = "selecting_item"
    SELECTING_VARIANT = "selecting_variant"
    ENTERING_QUANTITY = "entering_quantity"
    ADD_MORE = "add_more"
    CHECKOUT = "checkout"
    ORDER_CONFIRMED = "order_confirmed"


class MenuItem:
    """Represents a menu item"""
    def __init__(self, item_id: int, name: str, price: float, category: str, description: str = "", available: bool = True, image_url: str = "", variants: list = None):
        self.item_id = item_id
        self.name = name
        self.price = price
        self.category = category
        self.description = description
        self.available = available
        self.image_url = image_url
        self.variants = variants or []

    def to_dict(self):
        return {
            "id": self.item_id,
            "name": self.name,
            "price": self.price,
            "category": self.category,
            "description": self.description,
            "available": self.available,
            "image_url": self.image_url,
            "variants": self.variants
        }

    def __repr__(self):
        status = "Available" if self.available else "Out of Stock"
        return f"{self.item_id}. {self.name} - Rs {self.price} ({status})"


class CartItem:
    """Represents an item in user's cart"""
    def __init__(self, menu_item: MenuItem, quantity: int, variant: dict = None):
        self.menu_item = menu_item
        self.quantity = quantity
        self.variant = variant
        
        # Calculate price and name based on variant
        self.price = variant['price'] if variant else menu_item.price
        variant_suffix = f" ({variant['name']})" if variant else ""
        self.name = f"{menu_item.name}{variant_suffix}"

    @property
    def subtotal(self) -> float:
        return self.price * self.quantity

    def to_dict(self):
        return {
            "item_id": self.menu_item.item_id,
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity,
            "subtotal": self.subtotal
        }


class Cart:
    """Manages user's shopping cart"""
    def __init__(self):
        self.items: Dict[str, CartItem] = {}

    def add_item(self, menu_item: MenuItem, quantity: int, variant: dict = None) -> bool:
        """Add item to cart or update quantity if exists"""
        if quantity <= 0:
            return False
        
        key = f"{menu_item.item_id}_{variant['name']}" if variant else str(menu_item.item_id)
        
        if key in self.items:
            self.items[key].quantity += quantity
        else:
            self.items[key] = CartItem(menu_item, quantity, variant)
        return True

    def remove_item(self, item_id: int) -> bool:
        """Remove item from cart"""
        if item_id in self.items:
            del self.items[item_id]
            return True
        return False

    def update_quantity(self, item_id: int, quantity: int) -> bool:
        """Update quantity of existing cart item"""
        if item_id in self.items:
            if quantity <= 0:
                return self.remove_item(item_id)
            self.items[item_id].quantity = quantity
            return True
        return False

    @property
    def total(self) -> float:
        """Calculate total cart value"""
        return sum(item.subtotal for item in self.items.values())

    @property
    def item_count(self) -> int:
        """Get total number of items in cart"""
        return sum(item.quantity for item in self.items.values())

    def is_empty(self) -> bool:
        """Check if cart is empty"""
        return len(self.items) == 0

    def get_summary(self) -> str:
        """Get formatted cart summary"""
        if self.is_empty():
            return "Your cart is empty!"
        
        summary = "🛒 *CART SUMMARY:*\n" + "-"*20 + "\n"
        for cart_item in self.items.values():
            summary += f"*{cart_item.menu_item.name}*\n"
            summary += f"  _{cart_item.quantity}_ x Rs {cart_item.menu_item.price} = *Rs {cart_item.subtotal}*\n"
        summary += "-"*20 + "\n"
        summary += f"💰 *TOTAL: Rs {self.total:.2f}*\n"


class UserSession:
    """Manages individual user's session and state"""
    def __init__(self, phone_number: str):
        self.phone_number = phone_number
        self.state = UserState.WELCOME
        self.cart = Cart()
        self.selected_item: Optional[MenuItem] = None
        self.selected_category: Optional[str] = None
        self.selected_variant: Optional[dict] = None
        self.created_at = datetime.now()
        self.last_interaction = datetime.now()

    def update_activity(self):
        """Update last interaction timestamp"""
        self.last_interaction = datetime.now()

    def to_dict(self):
        return {
            "phone": self.phone_number,
            "state": self.state.value,
            "cart_items": len(self.cart.items),
            "created_at": self.created_at.isoformat(),
            "last_interaction": self.last_interaction.isoformat()
        }


class MenuManager:
    """Manages restaurant menu - easily extendable to DB/API"""
    def __init__(self, db=None):
        self.db = db
        self.items: List[MenuItem] = []

        # Try to load from database first
        if db:
            try:
                self._load_from_db()
            except Exception as e:
                logging.warning(f"Failed to load menu from DB: {e}")
                self._load_menu()
        else:
            self._load_menu()

    def _load_from_db(self):
        """Load menu from database"""
        db_items = self.db.get_all_menu_items()
        for item_data in db_items:
            # item_data['variants'] might be a JSON string or dict list, database.py now returns parsed JSON
            variants = item_data.get("variants", [])
            if isinstance(variants, str):
                import json
                try:
                    variants = json.loads(variants)
                except:
                    variants = []
            
            self.items.append(MenuItem(
                item_id=item_data["item_id"],
                name=item_data["name"],
                price=item_data["price"],
                category=item_data["category"],
                description=item_data.get("description", ""),
                image_url=item_data.get("image_url", ""),
                variants=variants
            ))
        logging.info(f"Loaded {len(self.items)} items from database")

    def _load_menu(self):
        """Load menu from dynamic structure (easily extendable to DB/API)"""
        import json
        try:
            with open("menu_data.json", "r", encoding="utf-8") as f:
                menu_data = json.load(f)
        except Exception as e:
            logging.error(f"Could not load menu_data.json: {e}")
            menu_data = []

        for item_data in menu_data:
            self.items.append(MenuItem(
                item_id=item_data["item_id"],
                name=item_data["name"],
                price=item_data["price"],
                category=item_data["category"],
                description=item_data.get("description", ""),
                image_url=item_data.get("image_url", ""),
                variants=item_data.get("variants", [])
            ))

    def get_categories(self) -> List[str]:
        """Get unique categories"""
        return sorted(list(set(item.category for item in self.items if item.available)))

    def get_by_category(self, category_idx_or_name: str) -> List[MenuItem]:
        """Get menu items by category name or index"""
        categories = self.get_categories()
        
        # Try as index
        try:
            idx = int(category_idx_or_name) - 1
            if 0 <= idx < len(categories):
                target_cat = categories[idx]
                return [i for i in self.items if i.category == target_cat and i.available]
        except ValueError:
            pass
            
        # Try as name
        target_cat = category_idx_or_name.lower()
        return [i for i in self.items if i.category.lower() == target_cat and i.available]

    def get_by_id(self, item_id: int) -> Optional[MenuItem]:
        """Get menu item by ID"""
        for item in self.items:
            if item.item_id == item_id:
                return item
        return None

    def get_formatted_categories(self) -> str:
        cats = self.get_categories()
        res = "Please select a category by replying with its number:\n\n"
        for i, cat in enumerate(cats, 1):
            res += f"{i}. {cat}\n"
        return res

    def get_formatted_menu_for_category(self, category_name: str) -> str:
        items = [i for i in self.items if i.category == category_name and i.available]
        if not items:
            return "No items in this category."
            
        res = f"--- {category_name} ---\nReply with the item number:\n\n"
        for item in items:
            res += f"{item.item_id}. {item.name}\n"
            if item.description:
                res += f"   {item.description}\n"
        return res
        
    def get_formatted_variants_for_item(self, item: MenuItem) -> str:
        if not item.variants:
            return f"Selected {item.name} at Rs {item.price}.\nPlease enter quantity:"
            
        res = f"Select size/variant for {item.name}:\n\n"
        for i, var in enumerate(item.variants, 1):
            res += f"{i}. {var['name']} - Rs {var['price']}\n"
        return res

class ChatbotEngine:
    """Main chatbot engine - orchestrates conversation flow"""

    def __init__(self, db=None):
        self.db = db
        self.menu_manager = MenuManager(db=db)
        self.sessions: Dict[str, UserSession] = {}
        logging.info("Chatbot initialized")

    def get_or_create_session(self, phone_number: str) -> UserSession:
        if phone_number not in self.sessions:
            self.sessions[phone_number] = UserSession(phone_number)
            if self.db:
                try:
                    self.db.create_or_update_user(phone_number)
                except Exception as e:
                    logging.warning(f"Failed to create user in DB: {e}")

        session = self.sessions[phone_number]
        session.update_activity()
        return session

    def parse_user_input(self, user_input: str) -> Tuple[str, Any]:
        user_input = user_input.lower().strip()
        
        if re.match(r"^\d+$", user_input):
            return "number", int(user_input)

        keywords = {
            "hi": "greeting", "hello": "greeting", "menu": "menu",
            "cart": "view_cart", "checkout": "checkout", "finish": "checkout",
            "yes": "confirm", "ok": "confirm", "confirm": "confirm",
            "no": "add_more", "more": "add_more",
            "back": "back"
        }

        for keyword, intent in keywords.items():
            if keyword == user_input:
                return intent, None

        return "text", user_input

    def handle_user_message(self, phone_number: str, user_message: str) -> str:
        session = self.get_or_create_session(phone_number)
        intent, value = self.parse_user_input(user_message)

        if intent in ["greeting", "menu"]:
            session.state = UserState.SELECTING_CATEGORY
            return self._handle_greeting(session)
            
        if intent == "view_cart":
            return self._handle_cart_view(session)
            
        if intent == "checkout":
            return self._handle_checkout(session)
            
        if intent == "back":
            session.state = UserState.SELECTING_CATEGORY
            return self.menu_manager.get_formatted_categories()

        # State machine
        if session.state == UserState.WELCOME or session.state == UserState.SELECTING_CATEGORY:
            if intent == "number" or intent == "text":
                return self._handle_category_selection(session, str(value or user_message))
                
        elif session.state == UserState.SELECTING_ITEM:
            if intent == "number":
                return self._handle_item_selection(session, value)
                
        elif session.state == UserState.SELECTING_VARIANT:
            if intent == "number":
                return self._handle_variant_selection(session, value)
                
        elif session.state == UserState.ENTERING_QUANTITY:
            if intent == "number":
                return self._handle_quantity(session, value)
                
        elif session.state == UserState.ADD_MORE:
            if intent == "confirm":
                return self._handle_checkout(session)
            elif intent == "add_more":
                session.state = UserState.SELECTING_CATEGORY
                return self.menu_manager.get_formatted_categories()
                
        elif session.state == UserState.CHECKOUT:
            if intent == "confirm":
                return self._handle_order_confirmation(session)
            elif intent == "add_more":
                session.state = UserState.SELECTING_CATEGORY
                return self.menu_manager.get_formatted_categories()

        return "I didn't quite get that. Type 'menu' to see options or 'cart' to view your bag."

    def _handle_greeting(self, session: UserSession) -> str:
        cats = self.menu_manager.get_formatted_categories()
        return f"Welcome to Nirmla Sweets!\n\n{cats}"

    def _handle_category_selection(self, session: UserSession, selection: str) -> str:
        items = self.menu_manager.get_by_category(selection)
        if not items:
            return "Invalid category. Please select a valid number from the list."
            
        session.selected_category = items[0].category
        session.state = UserState.SELECTING_ITEM
        return self.menu_manager.get_formatted_menu_for_category(session.selected_category) + "\n\nReply 'back' to go to categories."

    def _handle_item_selection(self, session: UserSession, item_id: int) -> str:
        item = self.menu_manager.get_by_id(item_id)
        if not item or item.category != session.selected_category:
            return "Invalid item number for this category. Please try again."
            
        session.selected_item = item
        
        if item.variants:
            session.state = UserState.SELECTING_VARIANT
            return self.menu_manager.get_formatted_variants_for_item(item) + "\n\nReply 'back' to go to categories."
        else:
            session.state = UserState.ENTERING_QUANTITY
            session.selected_variant = None
            return f"You selected {item.name}.\nPlease enter quantity (e.g., 1, 2, 3...)"

    def _handle_variant_selection(self, session: UserSession, variant_idx: int) -> str:
        item = session.selected_item
        if not item or not item.variants:
            session.state = UserState.SELECTING_CATEGORY
            return self.menu_manager.get_formatted_categories()
            
        if 1 <= variant_idx <= len(item.variants):
            session.selected_variant = item.variants[variant_idx - 1]
            session.state = UserState.ENTERING_QUANTITY
            return f"Selected: {item.name} ({session.selected_variant['name']})\nPlease enter quantity:"
            
        return "Invalid variant option. Please pick a number from the list above."

    def _handle_quantity(self, session: UserSession, quantity: int) -> str:
        if quantity <= 0:
            return "Please enter a valid quantity (1 or more)."
            
        item = session.selected_item
        variant = session.selected_variant
        
        success = session.cart.add_item(item, quantity, variant)
        if success:
            session.state = UserState.ADD_MORE
            session.selected_item = None
            session.selected_variant = None
            
            subtotal = (variant['price'] if variant else item.price) * quantity
            name = f"{item.name} ({variant['name']})" if variant else item.name
            
            return f"Added {quantity}x {name} (Rs {subtotal}) to cart.\n\nType 'yes' to checkout or 'no' to add more items."
            
        return "Failed to add to cart. Try again."

    def _handle_cart_view(self, session: UserSession) -> str:
        if session.cart.is_empty():
            return "Your cart is empty. Type 'menu' to start ordering."
        return session.cart.get_summary() + "\n\nType 'checkout' to finish or 'menu' to add more."

    def _handle_checkout(self, session: UserSession) -> str:
        if session.cart.is_empty():
            return "Your cart is empty. Type 'menu' to add items."
            
        session.state = UserState.CHECKOUT
        return session.cart.get_summary() + "\n\nPlease type 'confirm' to place your order or 'no' to add more items."

    def _handle_order_confirmation(self, session: UserSession) -> str:
        if session.cart.is_empty():
            return "Your cart is empty."
            
        total = session.cart.total
        
        # Save order to DB
        if self.db:
            try:
                order_items = []
                for item in session.cart.items.values():
                    order_items.append({
                        "item_id": item.menu_item.item_id,
                        "name": item.name,
                        "quantity": item.quantity,
                        "price": item.price,
                        "subtotal": item.subtotal
                    })
                order_id = self.db.create_order(session.phone_number, order_items, total)
                
                session.cart.clear()
                session.state = UserState.ORDER_CONFIRMED
                return f"Order placed successfully! Your order ID is #{order_id}.\nTotal amount: Rs {total}.\nWe will contact you shortly."
            except Exception as e:
                logging.error(f"Order creation failed: {e}")
                return "Sorry, there was an error placing your order. Please try again."
        
        # Fallback if no DB
        session.cart.clear()
        session.state = UserState.ORDER_CONFIRMED
        return f"Order confirmed!\nTotal amount: Rs {total}.\nThank you for choosing Nirmla Sweets!"