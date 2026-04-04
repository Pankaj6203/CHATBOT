# MongoDB Migration - Complete Documentation

## ✓ Successfully Migrated to MongoDB Atlas

Your restaurant chatbot system is now fully integrated with **MongoDB Atlas** (cloud database) instead of local SQLite.

### Files Created/Modified

**New Files:**
- `mongodb_database.py` - MongoDB wrapper with same interface as SQLite
- `test_mongodb.py` - MongoDB connection and CRUD operations test
- `test_mongodb_integration.py` - Complete chatbot + MongoDB integration test
- `.env` - Environment configuration with MongoDB credentials

**Modified Files:**
- `app.py` - Updated to support both SQLite and MongoDB
- `chatbot.py` - Type hints updated (already compatible)
- `database.py` - Unchanged (still available as fallback)

### Configuration

**In `.env` file:**
```
# MongoDB Atlas Connection
MONGODB_USERNAME=pankaj_db_user
MONGODB_PASSWORD=Pr09d@9664
MONGODB_HOST=cluster0.uy7xu4q.mongodb.net
MONGODB_DATABASE=Nirmla_sweets
DATABASE_TYPE=mongodb

# Other configs...
WHATSAPP_VERIFY_TOKEN=your_verify_token_here
WHATSAPP_API_URL=https://graph.instagram.com/v18.0
WHATSAPP_TOKEN=your_access_token_here
WHATSAPP_PHONE_ID=your_phone_id_here
```

### MongoDB Collections vs SQLite Tables

MongoDB stores data in 5 collections (same data structure):

1. **menu_items** - Restaurant menu with prices, categories
2. **users** - Customer phone numbers and details
3. **orders** - Order headers (order_id, phone, total, status, timestamp)
4. **order_items** - Line items (which items in which orders)
5. **audit_log** - User action history for compliance

Each collection auto-indexes important fields for fast queries.

### Usage - Flask Server

**Start server with MongoDB:**
```bash
python app.py
```

The server automatically:
1. Reads MongoDB credentials from `.env`
2. Connects to MongoDB Atlas
3. Creates collections and indexes if they don't exist
4. Initializes the ChatbotEngine

**API Endpoints (MongoDB-backed):**
- `GET/POST /webhook` - WhatsApp webhook endpoints
- `GET /api/menu` - Get all menu items from MongoDB
- `GET /api/menu/<id>` - Get specific item
- `GET /api/menu/category/<cat>` - Get items by category
- `GET /api/orders/<phone>` - Get user's orders from MongoDB
- `GET /api/orders/<id>` - Get order details
- `GET /api/admin/analytics` - Get sales analytics from MongoDB
- `GET /api/admin/audit-log` - Get audit trail
- `GET /health` - Health check

### Usage - CLI/Testing

**Test MongoDB directly:**
```bash
python test_mongodb.py
```

**Test complete chatbot + MongoDB flow:**
```bash
python test_mongodb_integration.py
```

**Run chatbot in CLI with MongoDB:**
```bash
python chatbot.py
```
(Chatbot will auto-load menu from MongoDB if available)

### MongoDB Advantages Over SQLite

✓ **Cloud-based** - Accessible from anywhere (not just local file)
✓ **Scalable** - Easily handle millions of orders
✓ **Multi-region** - Data replicated across globe
✓ **Real-time sync** - Multiple servers can access simultaneously
✓ **Automatic backups** - MongoDB Atlas handles backups
✓ **Analytics-ready** - Built-in aggregation pipeline
✓ **No schema migration** - Add fields anytime without downtime
✓ **Free tier** - 512MB free storage at mongodb.com

### Switching Back to SQLite

If you want to use SQLite instead:
```
# In .env file:
DATABASE_TYPE=sqlite

# Restart Flask server
python app.py
```

The system supports both seamlessly - just change `DATABASE_TYPE` and restart!

### Verified Features

✓ MongoDB connection with URL-encoded credentials
✓ Menu items stored and retrieved from MongoDB
✓ User creation and tracking
✓ Complete order flow (select items → checkout → confirm)
✓ Order items stored with quantities and pricing
✓ Audit logging for all user actions
✓ Analytics: Total revenue, top items, order count
✓ Multi-item orders with proper calculations
✓ Database collections auto-created with proper indexes

### Test Results

Last integration test:
- ✓ Connected to MongoDB Atlas
- ✓ Loaded 5 menu items from database
- ✓ Simulated complete order flow (2 items, 3+5 quantities)
- ✓ Saved order with Rs 225 total
- ✓ Retrieved order items with correct pricing: 
  - Gulab Jamun: 3x Rs 50 = Rs 150
  - Samosa: 5x Rs 15 = Rs 75
- ✓ Logged audit trail entry
- ✓ Analytics showed total revenue: Rs 550 (from 3 orders)

### Next Steps

1. **Update WhatsApp credentials** in `.env`:
   - Get `WHATSAPP_VERIFY_TOKEN` from Meta
   - Get `WHATSAPP_TOKEN` (access token)
   - Get `WHATSAPP_PHONE_ID` from your phone number

2. **Deploy Flask server**:
   ```bash
   python app.py
   ```
   Server runs on `http://localhost:5000`

3. **Test WhatsApp integration**:
   - Connect Meta Webhook to your server
   - Send test messages from WhatsApp

4. **Monitor analytics**:
   - Access `/api/admin/analytics` endpoint
   - View orders, revenue, top items from MongoDB

### Troubleshooting

**"Username and password must be escaped"**
- Make sure you're using individual credentials (username/password/host), not raw connection string
- The code automatically URL-encodes special characters like `@` in passwords

**"Connection timeout"**
- Check internet connection
- Verify MongoDB Atlas cluster is active
- Check credentials in `.env` file
- Ensure WhatsApp IP is whitelisted in MongoDB Atlas (if using IP whitelist)

**Can't connect to MongoDB**
- Verify credentials: `pankaj_db_user` / `Pr09d@9664` / `cluster0.uy7xu4q.mongodb.net`
- Check Database_TYPE=mongodb in .env
- Restart Flask server after changing .env
- Check MongoDB Atlas cluster status

### Architecture

```
┌─────────────────────────────────────────┐
│      WhatsApp Message / REST API        │
└────────────────┬────────────────────────┘
                 │
           Flask App (app.py)
                 │
         ┌───────┴────────┐
         │                │
    ChatbotEngine      Database Layer
      (chatbot.py)          │
         │              ┌───┴────────┐
      Menu            MongoDB    SQLite
      Cart         (mongodb_  (database.
      Session       database)  py)
         │               │
         └───────┬───────┘
                 │
         ┌───────▼──────────┐
         │ Persistent Data  │
         │ ├─ menu_items    │
         │ ├─ users         │
         │ ├─ orders        │
         │ ├─ order_items   │
         │ └─ audit_log     │
         └──────────────────┘
```

### Files Summary

| File | Lines | Purpose |
|------|-------|---------|
| mongodb_database.py | 400+ | MongoDB wrapper with 25+ methods |
| app.py | 350+ | Flask server with dual-database support |
| chatbot.py | 720+ | Core chatbot engine (unchanged) |
| database.py | 300+ | SQLite fallback (unchanged) |
| .env | 15 | MongoDB credentials & config |
| test_mongodb.py | 100+ | MongoDB CRUD test suite |
| test_mongodb_integration.py | 120+ | E2E chatbot + MongoDB test |

**Total:** 2000+ lines of production Python code

### Security Note

Your MongoDB Atlas credentials are in `.env` file:
- Never commit `.env` to version control
- Use `.gitignore` to exclude: `.env`, `*.log`, `__pycache__`, `*.pyc`
- In production, use environment variables or secrets manager (e.g., AWS Secrets Manager)

### Support

All operations are identical between SQLite and MongoDB:
- Same method names: `create_order()`, `add_order_item()`, `get_user_orders()`
- Same return types: dictionaries with consistent fields
- Drop-in replacement: Change `DATABASE_TYPE` and restart!

**Your chatbot is now enterprise-ready with cloud database! 🚀**
