"""
Twilio WhatsApp Integration for Umesh Sweets Chatbot
Send/receive WhatsApp messages via Twilio
"""

import logging
from typing import Dict, Optional, List
from twilio.rest import Client
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TwilioWhatsApp:
    """Twilio WhatsApp service for sending notifications and messages"""
    
    def __init__(self, account_sid: str, auth_token: str, twilio_number: str):
        """
        Initialize Twilio WhatsApp service
        
        Args:
            account_sid: Twilio Account SID
            auth_token: Twilio Auth Token
            twilio_number: Twilio WhatsApp-enabled phone number (format: +1234567890)
        """
        try:
            self.client = Client(account_sid, auth_token)
            self.twilio_number = twilio_number
            logger.info(f"✓ Twilio WhatsApp service initialized")
            logger.info(f"  Twilio Number: {twilio_number}")
        except Exception as e:
            logger.error(f"✗ Failed to initialize Twilio: {e}")
            raise
    
    def send_message(self, to_number: str, message_body: str) -> Dict:
        """
        Send WhatsApp message via Twilio
        
        Args:
            to_number: Recipient phone number (format: +91XXXXXXXXXX)
            message_body: Message content
            
        Returns:
            Dict with message details
        """
        try:
            # Ensure phone number has + prefix
            if not to_number.startswith('+'):
                to_number = '+' + to_number
            
            message = self.client.messages.create(
                from_=f"whatsapp:{self.twilio_number}",
                to=f"whatsapp:{to_number}",
                body=message_body
            )
            
            logger.info(f"✓ Message sent to {to_number}: SID={message.sid}")
            
            return {
                "status": "sent",
                "message_id": message.sid,
                "to": to_number,
                "timestamp": datetime.now().isoformat(),
                "body": message_body
            }
        except Exception as e:
            logger.error(f"✗ Failed to send message to {to_number}: {e}")
            return {
                "status": "failed",
                "to": to_number,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def send_order_confirmation(self, phone_number: str, order_id: str, 
                               items: List[Dict], total: float) -> Dict:
        """
        Send order confirmation message
        
        Args:
            phone_number: Customer phone number
            order_id: Order ID
            items: List of ordered items
            total: Total amount
            
        Returns:
            Message delivery status
        """
        try:
            # Build message
            message_body = f"""🎉 ORDER CONFIRMED!

Order ID: {order_id}
Total: Rs {total:.2f}

📋 Items:
"""
            for item in items:
                message_body += f"  • {item['name']}: {item['quantity']}x Rs {item['price']}\n"
            
            message_body += f"""
✅ Your order has been confirmed.
Thank you for ordering from Umesh Sweets! 🙏

📍 Location: 1329, Ara - Sasaram Rd, Bikramganj
📞 Contact: +6203454484
"""
            
            return self.send_message(phone_number, message_body)
        except Exception as e:
            logger.error(f"Error sending order confirmation: {e}")
            return {"status": "failed", "error": str(e)}
    
    def send_delivery_notification(self, phone_number: str, order_id: str, 
                                  estimated_time: str) -> Dict:
        """
        Send delivery notification
        
        Args:
            phone_number: Customer phone number
            order_id: Order ID
            estimated_time: Estimated delivery time
            
        Returns:
            Message delivery status
        """
        try:
            message_body = f"""🚗 YOUR ORDER IS ON THE WAY!

Order ID: {order_id}
Estimated Delivery: {estimated_time}

Track your order or contact us at +6203454484

Thank you for your patience! 🙏
"""
            return self.send_message(phone_number, message_body)
        except Exception as e:
            logger.error(f"Error sending delivery notification: {e}")
            return {"status": "failed", "error": str(e)}
    
    def send_promotional_message(self, phone_number: str, message_body: str) -> Dict:
        """
        Send promotional/marketing message
        
        Args:
            phone_number: Customer phone number
            message_body: Promotional message content
            
        Returns:
            Message delivery status
        """
        try:
            return self.send_message(phone_number, message_body)
        except Exception as e:
            logger.error(f"Error sending promotional message: {e}")
            return {"status": "failed", "error": str(e)}
    
    def send_menu_preview(self, phone_number: str) -> Dict:
        """
        Send quick menu preview
        
        Args:
            phone_number: Customer phone number
            
        Returns:
            Message delivery status
        """
        try:
            message_body = """🍪 UMESH SWEETS MENU

🍬 SWEETS:
  1. Gulab Jamun - Rs 50
  2. Jalebi - Rs 40
  3. Barfi - Rs 80
  4. Rasgulla - Rs 60

🥘 NAMKEEN:
  7. Chhole Bhature - Rs 60
  8. Samosa - Rs 15
  9. Kachori - Rs 20
  10. Mathri - Rs 35

🥜 DRY FRUITS:
  13. Almonds (500g) - Rs 500
  14. Cashews (500g) - Rs 450

Reply with item number to order!
📍 Location: 1329, Ara - Sasaram Rd
📞 Contact: +6203454484
"""
            return self.send_message(phone_number, message_body)
        except Exception as e:
            logger.error(f"Error sending menu preview: {e}")
            return {"status": "failed", "error": str(e)}
    
    def send_feedback_request(self, phone_number: str, order_id: str) -> Dict:
        """
        Send feedback request after delivery
        
        Args:
            phone_number: Customer phone number
            order_id: Order ID
            
        Returns:
            Message delivery status
        """
        try:
            message_body = f"""👋 Thank you for your order!

Order ID: {order_id}

We'd love to hear your feedback! 
Please rate your experience or share any suggestions.

Reply with:
  ⭐⭐⭐⭐⭐ for excellent
  ⭐⭐⭐⭐ for good
  ⭐⭐⭐ for okay

Thank you! 🙏
"""
            return self.send_message(phone_number, message_body)
        except Exception as e:
            logger.error(f"Error sending feedback request: {e}")
            return {"status": "failed", "error": str(e)}
    
    def send_broadcast(self, phone_numbers: List[str], message_body: str) -> Dict:
        """
        Send bulk message to multiple customers
        
        Args:
            phone_numbers: List of phone numbers
            message_body: Message content
            
        Returns:
            Bulk send status
        """
        try:
            results = {
                "total": len(phone_numbers),
                "sent": 0,
                "failed": 0,
                "messages": []
            }
            
            for phone in phone_numbers:
                result = self.send_message(phone, message_body)
                results["messages"].append(result)
                
                if result["status"] == "sent":
                    results["sent"] += 1
                else:
                    results["failed"] += 1
            
            logger.info(f"Broadcast complete: {results['sent']}/{results['total']} sent")
            return results
        except Exception as e:
            logger.error(f"Error in broadcast: {e}")
            return {"status": "failed", "error": str(e)}
    
    def format_phone_for_twilio(self, phone_number: str) -> str:
        """
        Format phone number for Twilio
        
        Args:
            phone_number: Phone number (any format)
            
        Returns:
            Formatted phone number (+91XXXXXXXXXX)
        """
        # Remove any non-digit characters except +
        cleaned = '+' + ''.join(c for c in phone_number if c.isdigit())
        
        # Ensure it has country code (assume +91 for India if not present)
        if len(cleaned) < 12:  # +91XXXXXXXXXX = 13 chars
            if not cleaned.startswith('+91'):
                cleaned = '+91' + cleaned[-10:]
            else:
                cleaned = '+91' + cleaned[-10:]
        
        return cleaned


# Test and Demo
if __name__ == "__main__":
    from mongodb_database import MongoDatabase
    
    # Initialize Twilio
    ACCOUNT_SID = "AC02c43388674e1a6e2f47b5c3d818842fc"
    AUTH_TOKEN = "c6a3fc6945732de6b38b413fdec424770"
    TWILIO_NUMBER = "+14155238886"  # Twilio sandbox WhatsApp number
    
    print("Initializing Twilio WhatsApp Service...")
    whatsapp = TwilioWhatsApp(ACCOUNT_SID, AUTH_TOKEN, TWILIO_NUMBER)
    
    print("\n✓ Service Ready!")
    print(f"Account SID: {ACCOUNT_SID[:20]}...")
    print(f"Twilio WhatsApp Number: {TWILIO_NUMBER}")
    
    print("\nAvailable Methods:")
    print("  1. send_message(to_number, message_body)")
    print("  2. send_order_confirmation(phone, order_id, items, total)")
    print("  3. send_delivery_notification(phone, order_id, time)")
    print("  4. send_menu_preview(phone)")
    print("  5. send_feedback_request(phone, order_id)")
    print("  6. send_promotional_message(phone, message)")
    print("  7. send_broadcast(phone_list, message)")
    
    print("\n💡 Usage Example:")
    print("""
    # Send order confirmation
    result = whatsapp.send_order_confirmation(
        phone_number="+916203454484",
        order_id="ORD-001",
        items=[
            {"name": "Gulab Jamun", "quantity": 2, "price": 50}
        ],
        total=100.0
    )
    print(result)
    """)
