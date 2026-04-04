"""
Flask Application with WhatsApp Integration
Provides webhook endpoints for WhatsApp Business API
Supports both SQLite and MongoDB Atlas
Includes Twilio WhatsApp notifications
"""

from flask import Flask, request, jsonify
import logging
import os
from typing import Dict, Optional
from dotenv import load_dotenv
from chatbot import ChatbotEngine
from database import Database
from mongodb_database import MongoDatabase
from twilio_whatsapp import TwilioWhatsApp
import json

# Load environment variables
load_dotenv()

# ==================== CONFIGURATION ====================

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Initialize logging
logging.basicConfig(
    filename='flask_server.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== INITIALIZATION ====================

chatbot = None
db = None
whatsapp = None

def init_services():
    """Initialize chatbot and database (supports SQLite or MongoDB)"""
    global chatbot, db, whatsapp
    try:
        # Get database type from environment
        db_type = os.getenv('DATABASE_TYPE', 'sqlite').lower()
        
        if db_type == 'mongodb':
            # Initialize MongoDB with proper credential handling
            mongo_user = os.getenv('MONGODB_USERNAME')
            mongo_pass = os.getenv('MONGODB_PASSWORD')
            mongo_host = os.getenv('MONGODB_HOST')
            mongo_db = os.getenv('MONGODB_DATABASE', 'umesh_sweets')
            
            if not all([mongo_user, mongo_pass, mongo_host]):
                raise ValueError("Missing MongoDB credentials in environment variables")
            
            db = MongoDatabase(
                username=mongo_user,
                password=mongo_pass,
                host=mongo_host,
                database_name=mongo_db
            )
            logger.info("✓ Connected to MongoDB Atlas")
        else:
            # Initialize SQLite (default)
            db = Database()
            logger.info("✓ Connected to SQLite")
        
        chatbot = ChatbotEngine(db=db)
        logger.info("✓ ChatbotEngine initialized")
        
        # Load menu from JSON or insert sample menu
        try:
            with open('menu_data.json', 'r') as f:
                menu_data = json.load(f)
                db.insert_menu_items(menu_data)
                logger.info(f"✓ Loaded menu from JSON: {len(menu_data)} items")
        except FileNotFoundError:
            # Check if menu already exists in database
            existing_items = db.get_all_menu_items()
            if not existing_items:
                # Insert default menu if no existing menu
                default_menu = [
                    {"item_id": 1, "name": "Gulab Jamun", "price": 50, "category": "Sweets", "description": "Soft & syrupy"},
                    {"item_id": 2, "name": "Jalebi", "price": 40, "category": "Sweets", "description": "Crispy & sweet"},
                    {"item_id": 3, "name": "Barfi", "price": 80, "category": "Sweets", "description": "Traditional barfi"},
                    {"item_id": 4, "name": "Rasgulla", "price": 60, "category": "Sweets", "description": "Cottage cheese balls"},
                    {"item_id": 5, "name": "Laddu", "price": 70, "category": "Sweets", "description": "Round sweet"},
                    {"item_id": 6, "name": "Kaju Barfi", "price": 120, "category": "Sweets", "description": "Cashew barfi"},
                    {"item_id": 7, "name": "Chhole Bhature", "price": 60, "category": "Namkeen", "description": "Chickpeas with fried bread"},
                    {"item_id": 8, "name": "Samosa", "price": 15, "category": "Namkeen", "description": "Crispy pastry"},
                    {"item_id": 9, "name": "Kachori", "price": 20, "category": "Namkeen", "description": "Spicy fried pastry"},
                    {"item_id": 10, "name": "Mathri", "price": 35, "category": "Namkeen", "description": "Salted crackers"},
                    {"item_id": 11, "name": "Pakora", "price": 30, "category": "Namkeen", "description": "Fried fritters"},
                    {"item_id": 12, "name": "Aloo Tikki", "price": 25, "category": "Namkeen", "description": "Potato patty"},
                    {"item_id": 13, "name": "Almonds (500g)", "price": 500, "category": "Dry Fruits", "description": "Premium almonds"},
                    {"item_id": 14, "name": "Cashews (500g)", "price": 450, "category": "Dry Fruits", "description": "Premium cashews"},
                    {"item_id": 15, "name": "Mixed Dry Fruits", "price": 600, "category": "Dry Fruits", "description": "Assorted nuts"},
                ]
                db.insert_menu_items(default_menu)
                logger.info(f"✓ Inserted default menu: {len(default_menu)} items")
            else:
                logger.info(f"✓ Menu already exists in database: {len(existing_items)} items")
        
        # Initialize Twilio WhatsApp (if enabled)
        try:
            if os.getenv('ENABLE_TWILIO_NOTIFICATIONS', 'true').lower() == 'true':
                twilio_sid = os.getenv('TWILIO_ACCOUNT_SID')
                twilio_token = os.getenv('TWILIO_AUTH_TOKEN')
                twilio_number = os.getenv('TWILIO_WHATSAPP_NUMBER')
                
                if twilio_sid and twilio_token and twilio_number:
                    whatsapp = TwilioWhatsApp(twilio_sid, twilio_token, twilio_number)
                    logger.info("✓ Twilio WhatsApp initialized")
                    # Pass whatsapp instance to chatbot
                    chatbot.whatsapp = whatsapp
                else:
                    logger.warning("Twilio credentials missing - WhatsApp notifications disabled")
        except Exception as e:
            logger.warning(f"Failed to initialize Twilio: {e}")
        
        logger.info("Services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise


# ==================== WHATSAPP WEBHOOK ENDPOINTS ====================

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    """
    Webhook verification endpoint for WhatsApp
    WhatsApp sends a GET request with parameters to verify the webhook
    """
    verify_token = "your_verify_token_here"  # Change this to your token
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if token == verify_token:
        logger.info(f"Webhook verified successfully")
        return challenge, 200
    else:
        logger.warning(f"Invalid verification token: {token}")
        return "Invalid verify token", 403


@app.route('/webhook', methods=['POST'])
def handle_whatsapp_message():
    """
    Main webhook endpoint for WhatsApp messages
    Receives messages from WhatsApp Business API
    """
    try:
        data = request.get_json()
        
        # WhatsApp webhook structure
        # {
        #   "entry": [{
        #     "changes": [{
        #       "value": {
        #         "messages": [{
        #           "from": "1234567890",
        #           "text": {"body": "Hello"},
        #           "type": "text"
        #         }]
        #       }
        #     }]
        #   }]
        # }
        
        if data.get("object") != "whatsapp_business_account":
            return jsonify({"status": "ok"}), 200
        
        # Extract message
        entry = data.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])
        
        for change in changes:
            value = change.get("value", {})
            messages = value.get("messages", [])
            
            for msg in messages:
                phone_number = msg.get("from")
                message_type = msg.get("type")
                
                # Handle text messages
                if message_type == "text":
                    user_message = msg.get("text", {}).get("body", "").strip()
                    
                    if user_message:
                        logger.info(f"Message from {phone_number}: {user_message}")
                        
                        # Get chatbot response
                        response = chatbot.handle_user_message(phone_number, user_message)
                        
                        # Log interaction
                        db.log_action(phone_number, "message_received", user_message)
                        
                        # Send response back to WhatsApp
                        send_whatsapp_message(phone_number, response)
        
        return jsonify({"status": "ok"}), 200
    
    except Exception as e:
        logger.error(f"Error handling WhatsApp message: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


def send_whatsapp_message(phone_number: str, message: str):
    """
    Send message back to WhatsApp user
    
    Replace these with actual WhatsApp Business API credentials:
    - WHATSAPP_API_URL: Your WhatsApp Business API URL
    - WHATSAPP_TOKEN: Your API access token
    - WHATSAPP_PHONE_ID: Your phone number ID
    """
    try:
        # This is a placeholder - implement actual WhatsApp API call
        # Example using requests library:
        # 
        # import requests
        # url = f"{WHATSAPP_API_URL}/messages"
        # headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
        # payload = {
        #     "messaging_product": "whatsapp",
        #     "to": phone_number,
        #     "type": "text",
        #     "text": {"body": message}
        # }
        # response = requests.post(url, json=payload, headers=headers)
        
        logger.info(f"Message sent to {phone_number}: {message[:50]}...")
        db.log_action(phone_number, "message_sent", message[:100])
    
    except Exception as e:
        logger.error(f"Failed to send WhatsApp message: {e}")


# ==================== REST API ENDPOINTS ====================

@app.route('/api/menu', methods=['GET'])
def get_menu():
    """Get all menu items"""
    try:
        items = db.get_all_menu_items()
        return jsonify({
            "status": "success",
            "data": items,
            "count": len(items)
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/menu/<int:item_id>', methods=['GET'])
def get_menu_item(item_id):
    """Get single menu item"""
    try:
        item = db.get_menu_item_by_id(item_id)
        if item:
            return jsonify({
                "status": "success",
                "data": item
            }), 200
        return jsonify({"status": "error", "message": "Item not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/menu/category/<category>', methods=['GET'])
def get_menu_by_category(category):
    """Get menu items by category"""
    try:
        items = db.get_menu_by_category(category)
        return jsonify({
            "status": "success",
            "data": items,
            "category": category,
            "count": len(items)
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/orders/<phone_number>', methods=['GET'])
def get_user_orders(phone_number):
    """Get user's order history"""
    try:
        orders = db.get_user_orders(phone_number)
        return jsonify({
            "status": "success",
            "data": orders,
            "count": len(orders)
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    """Get order details with items"""
    try:
        order = db.get_order(order_id)
        if not order:
            return jsonify({"status": "error", "message": "Order not found"}), 404
        
        items = db.get_order_items(order_id)
        return jsonify({
            "status": "success",
            "order": order,
            "items": items
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ==================== ADMIN ENDPOINTS ====================

@app.route('/api/admin/analytics', methods=['GET'])
def get_analytics():
    """Get business analytics (admin only)"""
    try:
        total_revenue = db.get_total_revenue()
        total_orders = db.get_order_count()
        top_items = db.get_top_items(limit=5)
        
        return jsonify({
            "status": "success",
            "data": {
                "total_revenue": total_revenue,
                "total_orders": total_orders,
                "top_items": top_items
            }
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/admin/audit-log', methods=['GET'])
def get_audit_log():
    """Get audit log (admin only)"""
    try:
        phone = request.args.get('phone')
        action = request.args.get('action')
        limit = int(request.args.get('limit', 100))
        
        logs = db.get_audit_log(phone_number=phone, action=action, limit=limit)
        return jsonify({
            "status": "success",
            "data": logs,
            "count": len(logs)
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ==================== TWILIO WHATSAPP NOTIFICATIONS ====================

@app.route('/api/notifications/send', methods=['POST'])
def send_whatsapp_notification():
    """Send WhatsApp notification via Twilio"""
    try:
        if not whatsapp:
            return jsonify({"status": "error", "message": "Twilio not configured"}), 400
        
        data = request.json
        phone_number = data.get('phone')
        message_body = data.get('message')
        
        if not phone_number or not message_body:
            return jsonify({"status": "error", "message": "Missing phone or message"}), 400
        
        result = whatsapp.send_message(phone_number, message_body)
        
        return jsonify({
            "status": "success",
            "data": result
        }), 200
    except Exception as e:
        logger.error(f"Error sending notification: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/notifications/order-confirmation', methods=['POST'])
def send_order_confirmation_sms():
    """Send order confirmation via WhatsApp"""
    try:
        if not whatsapp:
            return jsonify({"status": "error", "message": "Twilio not configured"}), 400
        
        data = request.json
        phone_number = data.get('phone')
        order_id = data.get('order_id')
        items = data.get('items', [])
        total = data.get('total', 0)
        
        if not phone_number or not order_id:
            return jsonify({"status": "error", "message": "Missing required fields"}), 400
        
        result = whatsapp.send_order_confirmation(phone_number, order_id, items, total)
        
        return jsonify({
            "status": "success",
            "data": result
        }), 200
    except Exception as e:
        logger.error(f"Error sending order confirmation: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/notifications/delivery', methods=['POST'])
def send_delivery_notification():
    """Send delivery notification via WhatsApp"""
    try:
        if not whatsapp:
            return jsonify({"status": "error", "message": "Twilio not configured"}), 400
        
        data = request.json
        phone_number = data.get('phone')
        order_id = data.get('order_id')
        estimated_time = data.get('estimated_time', '30 minutes')
        
        if not phone_number or not order_id:
            return jsonify({"status": "error", "message": "Missing required fields"}), 400
        
        result = whatsapp.send_delivery_notification(phone_number, order_id, estimated_time)
        
        return jsonify({
            "status": "success",
            "data": result
        }), 200
    except Exception as e:
        logger.error(f"Error sending delivery notification: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/notifications/menu', methods=['POST'])
def send_menu_preview():
    """Send menu preview via WhatsApp"""
    try:
        if not whatsapp:
            return jsonify({"status": "error", "message": "Twilio not configured"}), 400
        
        data = request.json
        phone_number = data.get('phone')
        
        if not phone_number:
            return jsonify({"status": "error", "message": "Missing phone number"}), 400
        
        result = whatsapp.send_menu_preview(phone_number)
        
        return jsonify({
            "status": "success",
            "data": result
        }), 200
    except Exception as e:
        logger.error(f"Error sending menu preview: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/notifications/feedback', methods=['POST'])
def send_feedback_request():
    """Send feedback request via WhatsApp"""
    try:
        if not whatsapp:
            return jsonify({"status": "error", "message": "Twilio not configured"}), 400
        
        data = request.json
        phone_number = data.get('phone')
        order_id = data.get('order_id')
        
        if not phone_number or not order_id:
            return jsonify({"status": "error", "message": "Missing required fields"}), 400
        
        result = whatsapp.send_feedback_request(phone_number, order_id)
        
        return jsonify({
            "status": "success",
            "data": result
        }), 200
    except Exception as e:
        logger.error(f"Error sending feedback request: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# ==================== HEALTH CHECK ====================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Umesh Sweets Chatbot",
        "version": "2.0"
    }), 200


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({"status": "error", "message": "Endpoint not found"}), 404


@app.errorhandler(500)
def server_error(error):
    logger.error(f"Server error: {error}")
    return jsonify({"status": "error", "message": "Internal server error"}), 500


# ==================== INITIALIZATION & STARTUP ====================

if __name__ == "__main__":
    init_services()
    
    print("="*70)
    print("UMESH SWEETS - FLASK CHATBOT SERVER")
    print("="*70)
    print("\nEndpoints:")
    print("  Webhook: POST /webhook")
    print("  Verify:  GET /webhook?hub.verify_token=xxx&hub.challenge=xxx")
    print()
    print("  Menu API:")
    print("    GET /api/menu")
    print("    GET /api/menu/<item_id>")
    print("    GET /api/menu/category/<category>")
    print()
    print("  Orders API:")
    print("    GET /api/orders/<phone_number>")
    print("    GET /api/orders/<order_id>")
    print()
    print("  Admin:")
    print("    GET /api/admin/analytics")
    print("    GET /api/admin/audit-log")
    print()
    print("  Health: GET /health")
    print()
    print("Starting server on http://localhost:5000")
    print("="*70 + "\n")
    
    # Run Flask app
    # Note: debug=False for Windows compatibility (avoids socket reload issues)
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
