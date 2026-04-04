import sys
from dotenv import load_dotenv
import os
load_dotenv()
from mongodb_database import MongoDatabase

mongo_user = os.getenv('MONGODB_USERNAME')
mongo_pass = os.getenv('MONGODB_PASSWORD')
mongo_host = os.getenv('MONGODB_HOST')
mongo_db = os.getenv('MONGODB_DATABASE', 'Nirmla_sweets')

if mongo_user and mongo_pass and mongo_host:
    db = MongoDatabase(username=mongo_user, password=mongo_pass, host=mongo_host, database_name=mongo_db)
    client_db = db.db
    
    print('Clearing old data...')
    client_db.categories.drop()
    client_db.menu_items.drop()
    
    categories = [
        {'_id': 1, 'name': 'Sweets'},
        {'_id': 2, 'name': 'Snacks'},
        {'_id': 3, 'name': 'Namkeen'},
        {'_id': 4, 'name': 'Dry Fruits'},
        {'_id': 5, 'name': 'Food'},
        {'_id': 6, 'name': 'Beverages'},
        {'_id': 7, 'name': 'Chaat Corner'},
        {'_id': 8, 'name': 'Bakery'}
    ]
    client_db.categories.insert_many(categories)
    print('Categories inserted:', len(categories))
    
    items = [
        # 1: Sweets
        {'item_id': 101, 'name': 'Gulab Jamun', 'price': 50, 'category_id': 1, 'description': '2 Pcs Hot Gulab Jamun'},
        {'item_id': 102, 'name': 'Kaju Katli', 'price': 250, 'category_id': 1, 'description': '250g Premium Kaju Katli'},
        {'item_id': 103, 'name': 'Rasgulla', 'price': 50, 'category_id': 1, 'description': '2 Pcs Sweet Bengali Rasgulla'},
        {'item_id': 104, 'name': 'Jalebi', 'price': 80, 'category_id': 1, 'description': '100g Crispy Jalebi in Desi Ghee'},
        {'item_id': 105, 'name': 'Motichoor Ladoo', 'price': 150, 'category_id': 1, 'description': '250g Pure Ghee Ladoo'},
        {'item_id': 106, 'name': 'Besan Ladoo', 'price': 140, 'category_id': 1, 'description': '250g Desi Ghee Besan Ladoo'},
        {'item_id': 107, 'name': 'Milk Cake', 'price': 180, 'category_id': 1, 'description': '250g Fresh Milk Cake'},
        {'item_id': 108, 'name': 'Kalakand', 'price': 190, 'category_id': 1, 'description': '250g Rich Kalakand'},
        {'item_id': 109, 'name': 'Rabri', 'price': 60, 'category_id': 1, 'description': '1 Bowl Special Rabri'},
        {'item_id': 110, 'name': 'Rasmalai', 'price': 70, 'category_id': 1, 'description': '2 Pcs Spongy Rasmalai'},
        {'item_id': 111, 'name': 'Soan Papdi', 'price': 120, 'category_id': 1, 'description': '250g Flaky Sweet'},
        {'item_id': 112, 'name': 'Peda', 'price': 160, 'category_id': 1, 'description': '250g Mathura Peda'},
        {'item_id': 113, 'name': 'Malpua', 'price': 170, 'category_id': 1, 'description': '250g Traditional Malpua'},
        {'item_id': 114, 'name': 'Cham Cham', 'price': 65, 'category_id': 1, 'description': '2 Pcs Bengali Cham Cham'},
        
        # 2: Snacks
        {'item_id': 201, 'name': 'Samosa', 'price': 20, 'category_id': 2, 'description': '1 Pc with Meethi/Teekhi Chutney'},
        {'item_id': 202, 'name': 'Kachori', 'price': 25, 'category_id': 2, 'description': '1 Pc Khasta Dal Kachori'},
        {'item_id': 203, 'name': 'Aloo Tikki', 'price': 40, 'category_id': 2, 'description': '2 Pcs Hot and Crispy Tikki'},
        {'item_id': 204, 'name': 'Paneer Pakoda', 'price': 35, 'category_id': 2, 'description': '1 Pc Fresh Paneer Pakoda'},
        {'item_id': 205, 'name': 'Bread Pakoda', 'price': 30, 'category_id': 2, 'description': '1 Pc Stuffed Bread Pakoda'},
        {'item_id': 206, 'name': 'Mix Veg Pakoda', 'price': 50, 'category_id': 2, 'description': '1 Plate Mixed Fritters'},
        {'item_id': 207, 'name': 'Dhokla', 'price': 60, 'category_id': 2, 'description': '1 Plate Gujarati Khaman Dhokla'},
        {'item_id': 208, 'name': 'Khandvi', 'price': 70, 'category_id': 2, 'description': '1 Plate Fresh Khandvi'},
        
        # 3: Namkeen
        {'item_id': 301, 'name': 'Mix Mixture', 'price': 80, 'category_id': 3, 'description': '250g Special Mix'},
        {'item_id': 302, 'name': 'Bikaneri Bhujia', 'price': 90, 'category_id': 3, 'description': '250g Authentic Taste'},
        {'item_id': 303, 'name': 'Ratlami Sev', 'price': 95, 'category_id': 3, 'description': '250g Spicy Sev'},
        {'item_id': 304, 'name': 'Khatta Meetha', 'price': 85, 'category_id': 3, 'description': '250g Sweet & Sour Mix'},
        {'item_id': 305, 'name': 'Moong Dal', 'price': 100, 'category_id': 3, 'description': '250g Fried Moong Dal'},
        {'item_id': 306, 'name': 'Tasty Nuts', 'price': 110, 'category_id': 3, 'description': '250g Spicy Coated Peanuts'},
        {'item_id': 307, 'name': 'Aloo Bhujia', 'price': 85, 'category_id': 3, 'description': '250g Crispy Potato Sev'},
        {'item_id': 308, 'name': 'Navratan Mix', 'price': 105, 'category_id': 3, 'description': '250g Premium Mix'},
        {'item_id': 309, 'name': 'Diet Mixture', 'price': 90, 'category_id': 3, 'description': '250g Roasted Namkeen'},
        
        # 4: Dry Fruits
        {'item_id': 401, 'name': 'Almonds (Badaam)', 'price': 400, 'category_id': 4, 'description': '250g Premium Quality'},
        {'item_id': 402, 'name': 'Cashews (Kaju)', 'price': 450, 'category_id': 4, 'description': '250g Premium Whole'},
        {'item_id': 403, 'name': 'Pistachios (Pista)', 'price': 500, 'category_id': 4, 'description': '250g Salted/Plain'},
        {'item_id': 404, 'name': 'Walnuts (Akhrot)', 'price': 350, 'category_id': 4, 'description': '250g Without Shell'},
        {'item_id': 405, 'name': 'Raisins (Kishmish)', 'price': 200, 'category_id': 4, 'description': '250g Sweet Raisins'},
        {'item_id': 406, 'name': 'Anjeer', 'price': 600, 'category_id': 4, 'description': '250g Premium Afghan Anjeer'},
        {'item_id': 407, 'name': 'Mixed Dry Fruits', 'price': 650, 'category_id': 4, 'description': '250g Gift Mix Box'},
        
        # 5: Food (Meals)
        {'item_id': 501, 'name': 'Chhole Bhature', 'price': 120, 'category_id': 5, 'description': '2 Pcs Bhature with Chhole'},
        {'item_id': 502, 'name': 'Paneer Butter Masala', 'price': 220, 'category_id': 5, 'description': 'Half portion (Serves 2)'},
        {'item_id': 503, 'name': 'Butter Naan', 'price': 45, 'category_id': 5, 'description': '1 Pc Hot Butter Naan'},
        {'item_id': 504, 'name': 'Special Veg Thali', 'price': 280, 'category_id': 5, 'description': 'Dal, Paneer, Mix Veg, Rice, Raita, 2 Roti, Sweet'},
        {'item_id': 505, 'name': 'Mini Thali', 'price': 160, 'category_id': 5, 'description': 'Dal, Rice, Mix Veg, 2 Roti'},
        {'item_id': 506, 'name': 'Pav Bhaji', 'price': 110, 'category_id': 5, 'description': '2 Pcs Butter Pav with Bhaji'},
        {'item_id': 507, 'name': 'Rajma Chawal', 'price': 130, 'category_id': 5, 'description': '1 Plate Rajma with Basmati Rice'},
        {'item_id': 508, 'name': 'Dal Makhani', 'price': 180, 'category_id': 5, 'description': 'Half portion Rich Creamy Dal'},
        {'item_id': 509, 'name': 'Jeera Rice', 'price': 90, 'category_id': 5, 'description': '1 Plate Basmati Jeera Rice'},
        {'item_id': 510, 'name': 'Tandoori Roti', 'price': 20, 'category_id': 5, 'description': '1 Pc Hot Tandoori Roti'},
        
        # 6: Beverages
        {'item_id': 601, 'name': 'Sweet Lassi', 'price': 60, 'category_id': 6, 'description': '1 Large Glass Thick Lassi'},
        {'item_id': 602, 'name': 'Masala Chaas', 'price': 40, 'category_id': 6, 'description': '1 Glass Spiced Buttermilk'},
        {'item_id': 603, 'name': 'Badam Milk', 'price': 70, 'category_id': 6, 'description': '1 Chilled Bottle'},
        {'item_id': 604, 'name': 'Cold Coffee', 'price': 65, 'category_id': 6, 'description': '1 Glass Cold Coffee'},
        {'item_id': 605, 'name': 'Rooh Afza', 'price': 50, 'category_id': 6, 'description': '1 Glass Special Rooh Afza Drink'},
        {'item_id': 606, 'name': 'Mineral Water', 'price': 20, 'category_id': 6, 'description': '1 Litre Bottle'},
        
        # 7: Chaat Corner
        {'item_id': 701, 'name': 'Pani Puri (Golgappa)', 'price': 40, 'category_id': 7, 'description': '6 Pcs Suji/Atta Puri'},
        {'item_id': 702, 'name': 'Dahi Bhalla', 'price': 70, 'category_id': 7, 'description': '1 Plate Sweet Curd Bhalla'},
        {'item_id': 703, 'name': 'Papdi Chaat', 'price': 65, 'category_id': 7, 'description': '1 Plate Crispy Papdi Mix'},
        {'item_id': 704, 'name': 'Raj Kachori', 'price': 80, 'category_id': 7, 'description': '1 Large Stuffed Kachori with Dahi'},
        {'item_id': 705, 'name': 'Bhel Puri', 'price': 60, 'category_id': 7, 'description': '1 Plate Mumbai Style Bhel'},
        {'item_id': 706, 'name': 'Aloo Chaat', 'price': 55, 'category_id': 7, 'description': '1 Plate Fried Potato Chaat'},
        
        # 8: Bakery
        {'item_id': 801, 'name': 'Pineapple Pastry', 'price': 60, 'category_id': 8, 'description': '1 Pc Fresh Cream Pastry'},
        {'item_id': 802, 'name': 'Black Forest Pastry', 'price': 70, 'category_id': 8, 'description': '1 Pc Chocolate Pastry'},
        {'item_id': 803, 'name': 'Truffle Cake (1/2 kg)', 'price': 450, 'category_id': 8, 'description': 'Eggless Chocolate Truffle Cake'},
        {'item_id': 804, 'name': 'Butter Cookies', 'price': 150, 'category_id': 8, 'description': '250g Box Premium Biscuits'},
        {'item_id': 805, 'name': 'Atta Biscuits', 'price': 120, 'category_id': 8, 'description': '250g Healthy Atta Cookies'},
        {'item_id': 806, 'name': 'Rusk (Toast)', 'price': 80, 'category_id': 8, 'description': '1 Packet Crunchy Premium Rusk'}
    ]
    client_db.menu_items.insert_many(items)
    print(f'Done! Successfully seeded {len(categories)} categories and {len(items)} menu items.')
else:
    print('Missing DB credentials')
