"""
Test Twilio WhatsApp Integration
"""

import os
import requests
import json
from twilio_whatsapp import TwilioWhatsApp

BASE_URL = "http://localhost:5000"

print("="*70)
print("TWILIO WHATSAPP INTEGRATION TEST")
print("="*70 + "\n")

# Test 1: Initialize Twilio
print("1. Initialize Twilio WhatsApp Service")
print("-" * 70)
try:
    ACCOUNT_SID = os.environ["TWILIO_ACCOUNT_SID"]
    AUTH_TOKEN = os.environ["TWILIO_AUTH_TOKEN"]
    TWILIO_NUMBER = "+14155238886"  # Twilio Sandbox WhatsApp number
    
    whatsapp = TwilioWhatsApp(ACCOUNT_SID, AUTH_TOKEN, TWILIO_NUMBER)
    print("✓ Twilio initialized successfully\n")
except Exception as e:
    print(f"✗ Failed to initialize: {e}\n")
    exit(1)

# Test 2: Test simple message
print("2. Send Simple Test Message")
print("-" * 70)
try:
    # Your WhatsApp number (where you want to receive test)
    YOUR_PHONE = "+916203454484"  # Update with your WhatsApp number
    
    result = whatsapp.send_message(
        YOUR_PHONE,
        "👋 Nirmla SWEETS TEST MESSAGE\n\nHello! This is a test message from your chatbot.\n\nReply with 'hi' to start ordering! 🍪"
    )
    
    if result["status"] == "sent":
        print(f"✓ Message sent successfully!")
        print(f"  Message ID: {result['message_id']}")
        print(f"  To: {result['to']}\n")
    else:
        print(f"✗ Failed to send: {result.get('error', 'Unknown error')}\n")
except Exception as e:
    print(f"✗ Error: {e}\n")

# Test 3: Send Order Confirmation
print("3. Send Order Confirmation Message")
print("-" * 70)
try:
    items = [
        {"name": "Gulab Jamun", "quantity": 2, "price": 50},
        {"name": "Samosa", "quantity": 3, "price": 15}
    ]
    
    result = whatsapp.send_order_confirmation(
        YOUR_PHONE,
        "ORD-TEST-001",
        items,
        145.0
    )
    
    if result["status"] == "sent":
        print(f"✓ Order confirmation sent!")
        print(f"  Message ID: {result['message_id']}\n")
    else:
        print(f"✗ Failed: {result.get('error')}\n")
except Exception as e:
    print(f"✗ Error: {e}\n")

# Test 4: Send Menu Preview
print("4. Send Menu Preview")
print("-" * 70)
try:
    result = whatsapp.send_menu_preview(YOUR_PHONE)
    
    if result["status"] == "sent":
        print(f"✓ Menu preview sent!")
        print(f"  Message ID: {result['message_id']}\n")
    else:
        print(f"✗ Failed: {result.get('error')}\n")
except Exception as e:
    print(f"✗ Error: {e}\n")

# Test 5: Send Delivery Notification
print("5. Send Delivery Notification")
print("-" * 70)
try:
    result = whatsapp.send_delivery_notification(
        YOUR_PHONE,
        "ORD-TEST-001",
        "30 minutes"
    )
    
    if result["status"] == "sent":
        print(f"✓ Delivery notification sent!")
        print(f"  Message ID: {result['message_id']}\n")
    else:
        print(f"✗ Failed: {result.get('error')}\n")
except Exception as e:
    print(f"✗ Error: {e}\n")

# Test 6: Test Flask API Endpoints
print("6. Test Flask API Endpoints")
print("-" * 70)

try:
    # Test simple notification endpoint
    payload = {
        "phone": YOUR_PHONE,
        "message": "🎉 Special Offer! Buy 2 items, get 10% discount today! 🎁"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/notifications/send",
        json=payload
    )
    
    if response.status_code == 200:
        print(f"✓ API notification endpoint working!")
        print(f"  Status: {response.status_code}\n")
    else:
        print(f"✗ API error: {response.status_code}")
        print(f"  Response: {response.text}\n")
except Exception as e:
    print(f"✗ API test failed: {e}\n")

# Test 7: Phone Number Formatting
print("7. Test Phone Number Formatting")
print("-" * 70)
test_phones = [
    "916203454484",
    "+916203454484",
    "6203454484",
    "+91 6203454484"
]

for phone in test_phones:
    formatted = whatsapp.format_phone_for_twilio(phone)
    print(f"  {phone:20} → {formatted}")

print("\n" + "="*70)
print("✓ ALL TESTS COMPLETE")
print("="*70)

print("\n📝 Next Steps:")
print("1. Update YOUR_PHONE variable with your WhatsApp number")
print("2. Accept Twilio Sandbox invitation on WhatsApp (if not already done)")
print("3. Run this test again to send test messages")
print("4. Check your WhatsApp for incoming messages")
print("\n💡 Production Deployment:")
print("- Get WhatsApp Business Account from Meta")
print("- Replace Twilio Sandbox number with your business number")
print("- Update .env with production credentials")
print("- Deploy Flask server to production")
