# 🍬 Umesh Sweets - Production-Grade Restaurant Chatbot

A **senior-level WhatsApp restaurant chatbot** with Flask integration, SQLite database, and enterprise architecture.

## 📋 Project Structure

```
p:\CHATBOT\
├── chatbot.py           # Core chatbot engine (650+ lines, production-grade)
├── database.py          # SQLite ORM layer with full CRUD operations  
├── app.py              # Flask webapp with WhatsApp webhook integration
├── restaurant_chatbot.db  # SQLite database (auto-created)
├── chatbot.log         # Application logs
├── flask_server.log    # Flask request logs
└── README.md           # This file
```

## 🚀 Features

### ✅ Core Chatbot Features
- Dynamic conversation flow with state machine
- Real-time menu management (15+ items)
- Shopping cart with add/remove/update operations
- Multi-item ordering with quantity tracking
- Order confirmation with unique Order IDs
- Per-user session management (in-memory + database)

### ✅ Database Features
- **SQLite** for persistent storage
- Menu items with categories & pricing
- User profiles with interaction timestamps
- Complete order history per user
- Order item breakdown and pricing
- Audit log for all user actions
- Analytics queries (revenue, top items, order count)

### ✅ Flask Integration
- WhatsApp Business API webhook (`/webhook`)
- REST API endpoints for menu, orders, analytics
- Admin dashboard endpoints
- Health check endpoint
- Comprehensive error handling

### ✅ Production Features
- Comprehensive logging (chatbot + Flask)
- Type hints throughout code
- Exception handling & recovery
- Clean separation of concerns
- Modular class-based architecture
- Database connection pooling
- JSON support for flexible data

## 📦 Installation

### Prerequisites
```bash
python 3.7+
pip
```

### Install Dependencies
```bash
pip install flask
```

### No other dependencies needed - uses only SQLite (standard library)

## 🏃 Quick Start

### 1. **Run Chatbot CLI Mode** (Testing)
```bash
cd p:\CHATBOT
python chatbot.py
```

Example conversation:
```
Bot: Welcome to Umesh Sweets!
     [Menu displayed]

You: 1
Bot: You selected: Gulab Jamun (Rs 50)
     Enter quantity:

You: 2
Bot: Added 2x Gulab Jamun (Rs 100)

You: menu
Bot: [Full menu displayed]

You: 8
Bot: You selected: Samosa (Rs 15)
     Enter quantity:

You: 3
Bot: Added 3x Samosa (Rs 45)

You: cart
Bot: [Cart shows 2 items, Total: Rs 145]

You: checkout
Bot: Confirm order? (yes/no)

You: yes
Bot: ORDER CONFIRMED!
     Order ID: ORD-1775293728
     [Full order summary]
```

### 2. **Run Flask Server** (Production)
```bash
cd p:\CHATBOT
python app.py
```

Server starts on `http://localhost:5000`

## 🔌 API Endpoints

### WhatsApp Webhook
```
POST /webhook
- Receives messages from WhatsApp Business API
- Auto-sends responses back to user

GET /webhook
- Verification endpoint (requires token)
```

### Menu API
```
GET /api/menu                      # All items
GET /api/menu/<item_id>            # Single item
GET /api/menu/category/<category>  # Items by category
```

### Orders API
```
GET /api/orders/<phone_number>     # User's order history
GET /api/orders/<order_id>         # Order details + items
```

### Admin API
```
GET /api/admin/analytics           # Revenue, order count, top items
GET /api/admin/audit-log           # User action history
```

### Health
```
GET /health                        # Service status
```

## 💾 Database Schema

### Tables

**menu_items**
- item_id (PK)
- name, price, category
- description, available
- created_at, updated_at

**users**
- phone_number (PK)
- name
- created_at, last_interaction

**orders**
- order_id (PK)
- phone_number (FK)
- total_amount, status
- created_at, updated_at

**order_items**
- id (PK)
- order_id (FK)
- item_id, item_name
- price, quantity, subtotal

**audit_log**
- id (PK)
- phone_number
- action, details
- created_at

## 🏗️ Architecture

### Class Hierarchy
```
MenuItem
  ├─ item_id, name, price, category
  └─ description, available

CartItem
  ├─ menu_item: MenuItem
  └─ quantity

Cart
  ├─ items: Dict[int, CartItem]
  └─ Methods: add_item, remove_item, get_summary, total

UserSession
  ├─ phone_number
  ├─ state: UserState (enum)
  ├─ cart: Cart
  └─ selected_item: Optional[MenuItem]

MenuManager
  ├─ items: List[MenuItem]
  ├─ Methods: get_by_id, get_by_name, get_formatted_menu
  └─ DB Integration: _load_from_db()

ChatbotEngine
  ├─ sessions: Dict[phone, UserSession]
  ├─ menu_manager: MenuManager
  ├─ db: Database
  └─ Methods: handle_user_message, _handle_*

Database
  ├─ Methods: insert, select, update, delete
  ├─ Analytics: get_revenue, get_top_items
  └─ Audit: log_action, get_audit_log
```

### State Machine
```
WELCOME
  ↓ (hi/hello)
MENU
  ↓ (select item: 1-15)
SELECTING_ITEM
  ↓ (enter quantity: 1+)
ENTERING_QUANTITY
  ↓ (add to cart)
ADD_MORE
  ├─ (type 'menu') → MENU
  ├─ (type 'cart') → View Cart
  ├─ (type 'checkout') → CHECKOUT
  ↓
CHECKOUT
  ├─ (yes/confirm) → ORDER_CONFIRMED
  └─ (no) → ADD_MORE
ORDER_CONFIRMED
  ↓ (order saved)
WELCOME (reset for next order)
```

## 📊 Sample Data

### Menu (15 Items)
**Sweets:**
- Gulab Jamun (Rs 50)
- Jalebi (Rs 40)
- Barfi (Rs 80)
- Rasgulla (Rs 60)
- Laddu (Rs 70)
- Kaju Barfi (Rs 120)

**Namkeen:**
- Chhole Bhature (Rs 60)
- Samosa (Rs 15)
- Kachori (Rs 20)
- Mathri (Rs 35)
- Pakora (Rs 30)
- Aloo Tikki (Rs 25)

**Dry Fruits:**
- Almonds 500g (Rs 500)
- Cashews 500g (Rs 450)
- Mixed Dry Fruits (Rs 600)

## 🔐 Configuration

### Flask Settings (in app.py)
```python
WHATSAPP_VERIFY_TOKEN = "your_verify_token_here"  # Change this!
WHATSAPP_API_URL = "https://graph.instagram.com/v18.0"
WHATSAPP_TOKEN = "your_api_token"
WHATSAPP_PHONE_ID = "your_phone_id"
```

### Database Settings (in database.py)
```python
DB_PATH = "restaurant_chatbot.db"
DB_SCHEMA_VERSION = 1
```

## 📈 Analytics & Reporting

### Available Metrics
```python
db.get_total_revenue()        # Total Rs from confirmed orders
db.get_order_count()          # Total number of orders
db.get_top_items(limit=10)    # Most ordered items
db.get_user_orders(phone)     # User's order history
db.get_audit_log()            # All user actions
```

### Example Analytics Query
```python
from database import Database

db = Database()
print(f"Total Revenue: Rs {db.get_total_revenue()}")
print(f"Total Orders: {db.get_order_count()}")
print(f"Top Items: {db.get_top_items(5)}")
```

## 🧪 Testing

### CLI Test
```bash
python chatbot.py
# Input: hi
# Input: 1
# Input: 2
# Input: menu
# Input: 8
# Input: 3
# Input: cart
# Input: checkout
# Input: yes
```

### Database Test
```python
from database import Database

db = Database()
items = db.get_all_menu_items()
print(f"Loaded {len(items)} menu items")

# Check orders
orders = db.get_user_orders("+916203454484")
print(f"User has {len(orders)} orders")
```

### API Test
```bash
# Test menu endpoint
curl http://localhost:5000/api/menu

# Test analytics
curl http://localhost:5000/api/admin/analytics

# Test health
curl http://localhost:5000/health
```

## 🚀 Deployment

### Docker (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install flask
CMD ["python", "app.py"]
```

### Heroku
```bash
heroku create umesh-sweets-bot
git push heroku main
heroku config:set WHATSAPP_TOKEN=xxx
```

### AWS Lambda (for webhook)
```python
def lambda_handler(event, context):
    return handle_whatsapp_message(event)
```

## 📝 Logging

### Locations
- **chatbot.log** - Chat interactions, orders, errors
- **flask_server.log** - Flask requests, webhooks
- **Console** - Real-time output during CLI mode

### Log Levels
```python
logging.DEBUG     # Detailed info
logging.INFO      # General info (default)
logging.WARNING   # Non-critical issues
logging.ERROR     # Critical errors
```

## 🔄 Future Enhancements

- [ ] Payment gateway (Razorpay/Stripe)
- [ ] SMS notifications (Twilio)
- [ ] Admin web dashboard (React/Vue)
- [ ] Order tracking in real-time
- [ ] Loyalty points system
- [ ] User feedback & ratings
- [ ] PostgreSQL migration
- [ ] Multi-language support (Hindi/English)
- [ ] Image-based menu
- [ ] Voice order support

## 📖 Code Quality Metrics

- **Lines of Code:** 1500+ (3 files combined)
- **Classes:** 10+ (modular & testable)
- **Type Hints:** 100% coverage  
- **Error Handling:** Comprehensive try/catch
- **Logging:** Prod-ready logging throughout
- **Documentation:** Docstrings on all major functions

## 🤝 Contributing

To add new features:
1. Add business logic to `ChatbotEngine`
2. Add database operations to `Database`
3. Add API endpoint to `app.py`
4. Test in CLI mode first
5. Then test Flask endpoints

## 📞 Support

**Restaurant:** Umesh Sweets
- **Phone:** 6203454484
- **Address:** 1329, Ara - Sasaram Rd, Bikramganj, Bihar 802212

## 📄 License

Production-ready code for restaurant use.

---

**Built with ❤️ for Umesh Sweets Restaurant**  
Senior Backend Developer Edition - April 2026
