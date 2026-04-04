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
        {'_id': 5, 'name': 'Food'}
    ]
    client_db.categories.insert_many(categories)
    print('Categories inserted:', len(categories))
    
    items = [
        {'item_id': 101, 'name': 'Gulab Jamun', 'price': 50, 'category_id': 1, 'description': '2 Pcs Hot Gulab Jamun'},
        {'item_id': 102, 'name': 'Kaju Katli', 'price': 250, 'category_id': 1, 'description': '250g Premium'},
        {'item_id': 103, 'name': 'Rasgulla', 'price': 40, 'category_id': 1, 'description': '2 Pcs Sweet'},
        
        {'item_id': 201, 'name': 'Samosa', 'price': 20, 'category_id': 2, 'description': '1 Pc with Chutney'},
        {'item_id': 202, 'name': 'Kachori', 'price': 25, 'category_id': 2, 'description': '1 Pc Dal'},
        {'item_id': 203, 'name': 'Aloo Tikki', 'price': 25, 'category_id': 2, 'description': '1 Pc hot'},
        
        {'item_id': 301, 'name': 'Mix Mixture', 'price': 80, 'category_id': 3, 'description': '250g Pack'},
        {'item_id': 302, 'name': 'Bhujia', 'price': 90, 'category_id': 3, 'description': '250g Bikaneri'},
        
        {'item_id': 401, 'name': 'Almonds', 'price': 400, 'category_id': 4, 'description': '250g'},
        {'item_id': 402, 'name': 'Cashews', 'price': 450, 'category_id': 4, 'description': '250g'},
        
        {'item_id': 501, 'name': 'Chhole Bhature', 'price': 120, 'category_id': 5, 'description': '2 Pcs'},
        {'item_id': 502, 'name': 'Paneer Butter Masala', 'price': 220, 'category_id': 5, 'description': 'Half portion'},
        {'item_id': 503, 'name': 'Butter Naan', 'price': 45, 'category_id': 5, 'description': '1 Pc'},
        {'item_id': 504, 'name': 'Veg Thali', 'price': 280, 'category_id': 5, 'description': 'Meal'}
    ]
    client_db.menu_items.insert_many(items)
    print('Menu items normalized and inserted using Foreign Keys.')
