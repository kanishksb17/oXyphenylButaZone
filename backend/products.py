products = [
    {"id": 1, "title": "Leather Jacket", "category": "Clothes", "price": 120, "image": "placeholder.jpg"},
    {"id": 2, "title": "Old Textbooks", "category": "Books", "price": 30, "image": "placeholder.jpg"},
]
def list_products():
    return products
def filter_by_category(category_name):
    return [p for p in products if p["category"].lower() == category_name.lower()]
def search_products(keyword):
    return [p for p in products if keyword.lower() in p["title"].lower()]
def filter_by_price(min_price, max_price):
    return [p for p in products if min_price <= p["price"] <= max_price]
