"""
Production-grade WhatsApp Restaurant Chatbot
Author: Senior Backend Developer
Features: Dynamic menu, cart management, order processing, session handling
"""

import json
import logging
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
    MENU = "menu"
    SELECTING_ITEM = "selecting_item"
    ENTERING_QUANTITY = "entering_quantity"
    ADD_MORE = "add_more"
    CHECKOUT = "checkout"
    ORDER_CONFIRMED = "order_confirmed"


class MenuItem:
    """Represents a menu item"""
    def __init__(self, item_id: int, name: str, price: float, 
                 category: str, description: str = "", available: bool = True):
        self.item_id = item_id
        self.name = name
        self.price = price
        self.category = category
        self.description = description
        self.available = available

    def to_dict(self):
        return {
            "id": self.item_id,
            "name": self.name,
            "price": self.price,
            "category": self.category,
            "description": self.description,
            "available": self.available
        }

    def __repr__(self):
        status = "Available" if self.available else "Out of Stock"
        return f"{self.item_id}. {self.name} - Rs {self.price} ({status})"


class CartItem:
    """Represents an item in user's cart"""
    def __init__(self, menu_item: MenuItem, quantity: int):
        self.menu_item = menu_item
        self.quantity = quantity

    @property
    def subtotal(self) -> float:
        return self.menu_item.price * self.quantity

    def to_dict(self):
        return {
            "item_id": self.menu_item.item_id,
            "name": self.menu_item.name,
            "price": self.menu_item.price,
            "quantity": self.quantity,
            "subtotal": self.subtotal
        }


class Cart:
    """Manages user's shopping cart"""
    def __init__(self):
        self.items: Dict[int, CartItem] = {}

    def add_item(self, menu_item: MenuItem, quantity: int) -> bool:
        """Add item to cart or update quantity if exists"""
        if quantity <= 0:
            return False
        
        if menu_item.item_id in self.items:
            self.items[menu_item.item_id].quantity += quantity
        else:
            self.items[menu_item.item_id] = CartItem(menu_item, quantity)
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
        
        summary = "CART SUMMARY:\n" + "="*60 + "\n"
        for cart_item in self.items.values():
            summary += f"{cart_item.menu_item.name}\n"
            summary += f"  {cart_item.quantity} x Rs {cart_item.menu_item.price} = Rs {cart_item.subtotal}\n"
        summary += "="*60 + "\n"
        summary += f"TOTAL: Rs {self.total:.2f}\n"
        return summary

    def clear(self):
        """Clear all items from cart"""
        self.items.clear()


class UserSession:
    """Manages individual user's session and state"""
    def __init__(self, phone_number: str):
        self.phone_number = phone_number
        self.state = UserState.WELCOME
        self.cart = Cart()
        self.selected_item: Optional[MenuItem] = None
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
            self.items.append(MenuItem(
                item_id=item_data["item_id"],
                name=item_data["name"],
                price=item_data["price"],
                category=item_data["category"],
                description=item_data.get("description", "")
            ))
        logging.info(f"Loaded {len(self.items)} items from database")

    def _load_menu(self):
        """Load menu from dynamic structure (easily extendable to DB/API)"""
        menu_data = [
            {"id": 1, "name": "Gulab Jamun", "price": 50, "category": "Sweets", "description": "Soft & syrupy"},
            {"id": 2, "name": "Jalebi", "price": 40, "category": "Sweets", "description": "Crispy & sweet"},
            {"id": 3, "name": "Barfi", "price": 80, "category": "Sweets", "description": "Traditional barfi"},
            {"id": 4, "name": "Rasgulla", "price": 60, "category": "Sweets", "description": "Cottage cheese balls"},
            {"id": 5, "name": "Laddu", "price": 70, "category": "Sweets", "description": "Round sweet"},
            {"id": 6, "name": "Kaju Barfi", "price": 120, "category": "Sweets", "description": "Cashew barfi"},
            {"id": 7, "name": "Chhole Bhature", "price": 60, "category": "Namkeen", "description": "Chickpeas with fried bread"},
            {"id": 8, "name": "Samosa", "price": 15, "category": "Namkeen", "description": "Crispy pastry"},
            {"id": 9, "name": "Kachori", "price": 20, "category": "Namkeen", "description": "Spicy fried pastry"},
            {"id": 10, "name": "Mathri", "price": 35, "category": "Namkeen", "description": "Salted crackers"},
            {"id": 11, "name": "Pakora", "price": 30, "category": "Namkeen", "description": "Fried fritters"},
            {"id": 12, "name": "Aloo Tikki", "price": 25, "category": "Namkeen", "description": "Potato patty"},
            {"id": 13, "name": "Almonds (500g)", "price": 500, "category": "Dry Fruits", "description": "Premium almonds"},
            {"id": 14, "name": "Cashews (500g)", "price": 450, "category": "Dry Fruits", "description": "Premium cashews"},
            {"id": 15, "name": "Mixed Dry Fruits", "price": 600, "category": "Dry Fruits", "description": "Assorted nuts"},
        ]
        
        for item_data in menu_data:
            self.items.append(MenuItem(
                item_id=item_data["id"],
                name=item_data["name"],
                price=item_data["price"],
                category=item_data["category"],
                description=item_data.get("description", "")
            ))

    def get_by_id(self, item_id: int) -> Optional[MenuItem]:
        """Get menu item by ID"""
        for item in self.items:
            if item.item_id == item_id:
                return item
        return None

    def get_by_name(self, name: str) -> Optional[MenuItem]:
        """Get menu item by name (case-insensitive)"""
        name_lower = name.lower().strip()
        for item in self.items:
            if item.name.lower() == name_lower:
                return item
        return None

    def get_available_items(self) -> List[MenuItem]:
        """Get all available menu items"""
        return [item for item in self.items if item.available]

    def get_by_category(self, category: str) -> List[MenuItem]:
        """Get menu items by category"""
        return [item for item in self.items if item.category.lower() == category.lower()]

    def get_formatted_menu(self, category: Optional[str] = None) -> str:
        """Get formatted menu display"""
        items = self.get_by_category(category) if category else self.get_available_items()
        
        if not items:
            return "No items available in this category."
        
        menu_display = "Nirmla SWEETS MENU\n" + "="*60 + "\n"
        
        categories = {}
        for item in items:
            if item.category not in categories:
                categories[item.category] = []
            categories[item.category].append(item)
        
        for cat, cat_items in categories.items():
            menu_display += f"\n{cat}:\n"
            for item in cat_items:
                menu_display += f"  {item.item_id}. {item.name} - Rs {item.price}\n"
                if item.description:
                    menu_display += f"     ({item.description})\n"
        
        menu_display += "\n" + "="*60 + "\n"
        menu_display += "Reply with item number or name to select.\n"
        return menu_display


class ChatbotEngine:
    """Main chatbot engine - orchestrates conversation flow"""
    
    def __init__(self, db=None):
        self.db = db
        self.menu_manager = MenuManager(db=db)
        self.sessions: Dict[str, UserSession] = {}
        logging.info("Chatbot initialized")

    def get_or_create_session(self, phone_number: str) -> UserSession:
        """Get existing session or create new one"""
        if phone_number not in self.sessions:
            self.sessions[phone_number] = UserSession(phone_number)
            logging.info(f"New session created for {phone_number}")
            
            # Create user in database if we have one
            if self.db:
                try:
                    self.db.create_or_update_user(phone_number)
                except Exception as e:
                    logging.warning(f"Failed to create user in DB: {e}")
        
        session = self.sessions[phone_number]
        session.update_activity()
        return session

    def parse_user_input(self, user_input: str) -> Tuple[str, Optional[int]]:
        """Parse user input and extract intent and value"""
        user_input = user_input.lower().strip()
        
        # Check if it's a number (menu item selection)
        try:
            item_id = int(user_input)
            return "item_selection", item_id
        except ValueError:
            pass
        
        # Check for keywords
        keywords = {
            "hi": "greeting", "hello": "greeting", "hola": "greeting", "hey": "greeting",
            "menu": "menu", "show menu": "menu",
            "cart": "view_cart", "view cart": "view_cart",
            "checkout": "checkout", "finish": "checkout", "order": "checkout",
            "yes": "confirm", "ok": "confirm", "confirm": "confirm",
            "no": "add_more", "more": "add_more",
            "quit": "exit", "bye": "exit", "goodbye": "exit",
        }
        
        for keyword, intent in keywords.items():
            if keyword in user_input:
                return intent, None
        
        # Try to match with menu item name
        for item in self.menu_manager.items:
            if item.name.lower() in user_input or user_input in item.name.lower():
                return "item_selection_by_name", item.item_id
        
        return "unknown", None

    def handle_user_message(self, phone_number: str, user_message: str) -> str:
        """Main entry point for processing user messages"""
        session = self.get_or_create_session(phone_number)
        intent, value = self.parse_user_input(user_message)
        
        logging.info(f"User {phone_number} - Intent: {intent}, State: {session.state.value}")
        
        # Handle quantity input if in quantity state
        if session.state == UserState.ENTERING_QUANTITY:
            try:
                quantity = int(user_message.strip())
                return self._handle_quantity_confirmation(session, quantity)
            except ValueError:
                pass
        
        if intent == "greeting" or session.state == UserState.WELCOME:
            return self._handle_greeting(session)
        elif intent == "menu":
            return self._handle_menu_request(session)
        elif intent in ("item_selection", "item_selection_by_name"):
            return self._handle_item_selection(session, value)
        elif intent == "view_cart":
            return self._handle_cart_view(session)
        elif intent == "add_more":
            return self._handle_add_more(session)
        elif intent == "checkout":
            return self._handle_checkout(session)
        elif intent == "confirm":
            return self._handle_order_confirmation(session)
        elif intent == "exit":
            return self._handle_exit(session)
        else:
            return "Sorry, I didn't understand. Type 'menu' to see items or 'help' for options."

    def _handle_greeting(self, session: UserSession) -> str:
        """Handle greeting"""
        session.state = UserState.MENU
        return (
            "Welcome to Nirmla Sweets!\n\n"
            "Location: 1329, Ara - Sasaram Rd, Bikramganj\n"
            "Phone: 6203454484\n\n"
            + self.menu_manager.get_formatted_menu()
        )

    def _handle_menu_request(self, session: UserSession) -> str:
        """Handle menu display request"""
        session.state = UserState.MENU
        return self.menu_manager.get_formatted_menu()

    def _handle_item_selection(self, session: UserSession, item_id: Optional[int]) -> str:
        """Handle item selection"""
        if item_id is None:
            return "Please provide a valid item number."
        
        item = self.menu_manager.get_by_id(item_id)
        if not item:
            return f"Item {item_id} not found. Type 'menu' to see available items."
        
        if not item.available:
            return f"{item.name} is out of stock. Select another item."
        
        session.selected_item = item
        session.state = UserState.ENTERING_QUANTITY
        return f"You selected: {item.name} (Rs {item.price})\n\nEnter quantity:"

    def _handle_quantity_confirmation(self, session: UserSession, quantity: int) -> str:
        """Handle quantity confirmation and add to cart"""
        if session.selected_item is None:
            return "No item selected. Type 'menu' to select an item."
        
        if quantity <= 0:
            return "Invalid quantity. Please enter a number greater than 0."
        
        session.cart.add_item(session.selected_item, quantity)
        subtotal = session.selected_item.price * quantity
        
        response = (
            f"Added {quantity}x {session.selected_item.name} (Rs {subtotal})\n\n"
            f"Options:\n"
            f"1. 'menu' - Add more items\n"
            f"2. 'cart' - View full cart\n"
            f"3. 'checkout' - Confirm order"
        )
        
        session.state = UserState.ADD_MORE
        session.selected_item = None
        return response

    def _handle_cart_view(self, session: UserSession) -> str:
        """Handle cart view request"""
        if session.cart.is_empty():
            return "Cart is empty. Type 'menu' to add items."
        
        return (
            session.cart.get_summary() +
            "\nOptions: 'menu' (add more) | 'checkout' (confirm)"
        )

    def _handle_add_more(self, session: UserSession) -> str:
        """Handle adding more items"""
        session.state = UserState.MENU
        return "Select more items:\n\n" + self.menu_manager.get_formatted_menu()

    def _handle_checkout(self, session: UserSession) -> str:
        """Handle checkout request"""
        if session.cart.is_empty():
            return "Cart is empty. Type 'menu' to add items."
        
        session.state = UserState.CHECKOUT
        return session.cart.get_summary() + "\nConfirm order? (yes/no)"

    def _handle_order_confirmation(self, session: UserSession) -> str:
        """Handle order confirmation"""
        if session.cart.is_empty():
            return "Cart is empty."
        
        order_id = f"ORD-{int(datetime.now().timestamp())}"
        total = session.cart.total
        
        response = (
            f"ORDER CONFIRMED!\n\n"
            f"Order ID: {order_id}\n"
            f"Total: Rs {total:.2f}\n\n"
            + session.cart.get_summary() +
            f"\nDelivery to: Bikramganj area\n"
            f"Call 6203454484 for updates\n\n"
            f"Thank you for ordering!"
        )
        
        logging.info(f"Order: {order_id}, Total: Rs {total}")
        
        # Save order to database if available
        if self.db:
            try:
                self.db.create_order(order_id, session.phone_number, total)
                for cart_item in session.cart.items.values():
                    self.db.add_order_item(
                        order_id,
                        cart_item.menu_item.item_id,
                        cart_item.menu_item.name,
                        cart_item.menu_item.price,
                        cart_item.quantity,
                        cart_item.subtotal
                    )
                self.db.log_action(session.phone_number, "order_placed", f"Order {order_id}: Rs {total}")
            except Exception as e:
                logging.warning(f"Failed to save order to DB: {e}")
        
        session.cart.clear()
        session.state = UserState.WELCOME
        
        return response

    def _handle_exit(self, session: UserSession) -> str:
        """Handle user exit"""
        session.state = UserState.WELCOME
        return "Thank you! Visit us again.\n\nPhone: 6203454484"


# ==================== MAIN INTERFACE ====================

def main():
    """Main function for testing chatbot"""
    try:
        from database import Database
        db = Database()
        chatbot = ChatbotEngine(db=db)
        db_msg = f"\nDatabase: {db.db_path}"
    except ImportError:
        chatbot = ChatbotEngine()
        db_msg = "\n(Running without database)"
    
    phone_number = "+916203454484"
    
    print("="*70)
    print("Nirmla SWEETS RESTAURANT CHATBOT")
    print("="*70)
    print(f"\nPhone: {phone_number}{db_msg}")
    print(f"Menu items: {len(chatbot.menu_manager.items)}")
    print("Type 'quit' to exit\n")
    
    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        
        if user_input.lower() == "quit":
            print("Goodbye!")
            break
        
        response = chatbot.handle_user_message(phone_number, user_input)
        print(f"\nBot: {response}\n")
        print("-"*70 + "\n")


if __name__ == "__main__":
    main()

