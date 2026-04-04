import json
import random

categories = ["Fast Food", "Pizza", "Indian", "Chinese", "Beverages", "Desserts"]

menu = []

for i in range(1, 1001):  # 1000 items
    item = {
        "id": f"item_{i:04}",
        "name": f"Food Item {i}",
        "category": random.choice(categories),
        "price": random.randint(50, 500),
        "discount": random.choice([0, 5, 10, 15]),
        "available": True,
        "rating": round(random.uniform(3.0, 5.0), 1),
        "prep_time": f"{random.randint(5,30)} min",
        "image": f"https://example.com/item{i}.jpg",
        "description": f"Tasty food item number {i}",
        "variants": [
            {"size": "Regular", "price": random.randint(50, 300)},
            {"size": "Large", "price": random.randint(100, 500)}
        ]
    }
    menu.append(item)


data = {
    "restaurant": {
        "id": "rest_001",
        "name": "Pankaj Food Hub",
        "location": "Delhi",
        "maps_link": "https://maps.app.goo.gl/2ggoR5Nz4WYR4ARp6",
        "rating": 4.3,
        "total_reviews": 120,
        "opening_hours": "10:00 AM - 11:00 PM",
        "contact": "+91XXXXXXXXXX",
        "currency": "INR",
        "tax_percent": 5,
        "delivery": True
    },
    "categories": categories,
    "menu": menu,
    "reviews": []
}

with open("restaurant_1000.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("✅ 1000 items JSON generated!")