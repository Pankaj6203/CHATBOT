import re

with open('p:/CHATBOT/app.py', 'r', encoding='utf-8') as f:
    app_text = f.read()

new_webhook = '''@app.route('/webhook', methods=['POST'])
def handle_whatsapp_message():
    """
    Main webhook endpoint for WhatsApp messages
    Supports both Twilio and Meta WhatsApp APIs
    """
    try:
        # 1. Check for Twilio Format (Form Data)
        if 'From' in request.form and 'Body' in request.form:
            from_number = request.form.get('From', '')
            # Extract plain number e.g., "whatsapp:+918888888" -> "918888888"
            phone_number = from_number.replace('whatsapp:', '').replace('+', '')
            user_message = request.form.get('Body', '').strip()
            
            logger.info(f"Twilio Message from {phone_number}: {user_message}")
            
            # Get chatbot response
            response = chatbot.handle_user_message(phone_number, user_message)
            if db:
                db.log_action(phone_number, "message_received", user_message)
                db.log_action(phone_number, "message_sent", response[:100])
                
            # Send reply using Twilio TwiML (Direct response)
            # This is the easiest and most robust way to reply to a Twilio incoming message
            return f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{response}</Message></Response>', 200, {'Content-Type': 'application/xml'}

        # 2. Check for Meta/Facebook API Format (JSON Data)
        data = request.get_json(silent=True)
        if data and data.get("object") == "whatsapp_business_account":
            entry = data.get("entry", [{}])[0]
            changes = entry.get("changes", [{}])

            for change in changes:
                value = change.get("value", {})
                messages = value.get("messages", [])

                for msg in messages:
                    phone_number = msg.get("from")
                    message_type = msg.get("type")

                    if message_type == "text":
                        user_message = msg.get("text", {}).get("body", "").strip()
                        if user_message:
                            logger.info(f"Meta Message from {phone_number}: {user_message}")

                            # Get chatbot response
                            response = chatbot.handle_user_message(phone_number, user_message)

                            if db: db.log_action(phone_number, "message_received", user_message)

                            # Send response back via Meta Graph API
                            send_whatsapp_message(phone_number, response)

            return jsonify({"status": "ok"}), 200

        # If we reach here, format is unknown
        return jsonify({"status": "ignored"}), 200

    except Exception as e:
        logger.error(f"Error handling WhatsApp message: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

def send_whatsapp_message(phone_number: str, message: str):'''

app_text = re.sub(r"@app\.route\('/webhook', methods=\['POST'\]\).*?def send_whatsapp_message\(phone_number: str, message: str\):", new_webhook, app_text, flags=re.DOTALL)

with open('p:/CHATBOT/app.py', 'w', encoding='utf-8') as f:
    f.write(app_text)
