import re

with open('p:/CHATBOT/chatbot.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace UserState Enum
new_states = '''class UserState(Enum):
    """Enumeration for conversation states"""
    WELCOME = "welcome"
    SELECTING_CATEGORY = "selecting_category"
    SELECTING_ITEM = "selecting_item"
    SELECTING_VARIANT = "selecting_variant"
    ENTERING_QUANTITY = "entering_quantity"
    ADD_MORE = "add_more"
    CHECKOUT = "checkout"
    ORDER_CONFIRMED = "order_confirmed"'''
text = re.sub(r'class UserState\(Enum\):\n\s*\"\"\"Enumeration for conversation states\"\"\"\n.*?\s+ORDER_CONFIRMED = \"order_confirmed\"', new_states, text, flags=re.DOTALL)

# Add variants and image_url to MenuItem
text = re.sub(r'def __init__\(self, item_id: int, name: str, price: float,\s*category: str, description: str = "", available: bool = True\):',
              'def __init__(self, item_id: int, name: str, price: float, category: str, description: str = "", available: bool = True, image_url: str = "", variants: list = None):', text)
text = text.replace('self.description = description\n        self.available = available', 'self.description = description\n        self.available = available\n        self.image_url = image_url\n        self.variants = variants or []')

# Inside MenuItem object to_dict
text = text.replace('"description": self.description,\n            "available": self.available', '"description": self.description,\n            "available": self.available,\n            "image_url": self.image_url,\n            "variants": self.variants')

# Update CartItem
new_cartitem = '''class CartItem:
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
        }'''
text = re.sub(r'class CartItem:.*?def to_dict\(self\):.*?}', new_cartitem, text, flags=re.DOTALL)

# In Cart class, change adding logic to include variant identification (using a string key)
text = text.replace('self.items: Dict[int, CartItem] = {}', 'self.items: Dict[str, CartItem] = {}')
new_add_item = '''def add_item(self, menu_item: MenuItem, quantity: int, variant: dict = None) -> bool:
        """Add item to cart or update quantity if exists"""
        if quantity <= 0:
            return False
        
        key = f"{menu_item.item_id}_{variant['name']}" if variant else str(menu_item.item_id)
        
        if key in self.items:
            self.items[key].quantity += quantity
        else:
            self.items[key] = CartItem(menu_item, quantity, variant)
        return True'''
text = re.sub(r'def add_item\(self, menu_item: MenuItem, quantity: int\) -> bool:.*?return True', new_add_item, text, flags=re.DOTALL)

# In UserSession, add category and variant selection memory
text = text.replace('self.selected_item: Optional[MenuItem] = None', 'self.selected_item: Optional[MenuItem] = None\n        self.selected_category: Optional[str] = None\n        self.selected_variant: Optional[dict] = None')

# Add number intent to parse_user_input
text = text.replace('def parse_user_input(self, text: str) -> Tuple[str, Any]:', 'def parse_user_input(self, text: str) -> Tuple[str, Any]:\n        if re.match(r"^\d+$", text.strip()): return "number", int(text.strip())')

with open('p:/CHATBOT/chatbot.py', 'w', encoding='utf-8') as f:
    f.write(text)
