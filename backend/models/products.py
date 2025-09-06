from typing import List, Dict, Optional

# Simple product data structure
class Product:
    def __init__(self, id: int, title: str, description: str, category: str, price: float, owner: str):
        self.id = id
        self.title = title
        self.description = description
        self.category = category
        self.price = price
        self.owner = owner
        self.image = "placeholder.png"

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "price": self.price,
            "owner": self.owner,
            "image": self.image
        }

# In-memory storage
products: Dict[int, Product] = {}
categories: List[str] = ['Electronics', 'Clothing', 'Books', 'Home', 'Other']
next_product_id = 1

# CREATE
def create_product(title: str, description: str, category: str, price: float, owner: str) -> Product:
    global next_product_id
    if category not in categories:
        raise ValueError("Invalid category")
    prod = Product(next_product_id, title, description, category, price, owner)
    products[next_product_id] = prod
    next_product_id += 1
    return prod

# READ ALL (optionally filtered)
def list_products(category: Optional[str] = None, search: Optional[str] = None) -> List[Product]:
    result = list(products.values())
    if category:
        result = [p for p in result if p.category == category]
    if search:
        result = [p for p in result if search.lower() in p.title.lower()]
    return result

# READ ONE
def get_product(product_id: int) -> Optional[Product]:
    return products.get(product_id)

# UPDATE
def update_product(product_id: int, title: str, description: str, category: str, price: float, owner: str) -> Optional[Product]:
    prod = products.get(product_id)
    if not prod or prod.owner != owner:
        return None
    if category not in categories:
        raise ValueError("Invalid category")
    prod.title = title
    prod.description = description
    prod.category = category
    prod.price = price
    return prod

# DELETE
def delete_product(product_id: int, owner: str) -> bool:
    prod = products.get(product_id)
    if not prod or prod.owner != owner:
        return False
    del products[product_id]
    return True

# Example usage
if __name__ == "__main__":
    # Create a product
    p1 = create_product("Eco Water Bottle", "Reusable bottle", "Home", 249.0, "alice@example.com")
    p2 = create_product("Organic T-shirt", "Made from organic cotton", "Clothing", 599.0, "bob@example.com")
    # List all
    print([p.to_dict() for p in list_products()])
    # Filter
    print([p.to_dict() for p in list_products(category="Home")])
    # Search
    print([p.to_dict() for p in list_products(search="T-shirt")])
    # Update
    update_product(p1.id, "Eco Bottle", "Reusable updated bottle", "Home", 299.0, "alice@example.com")
    print(get_product(p1.id).to_dict())
    # Delete
    delete_product(p2.id, "bob@example.com")
    print([p.to_dict() for p in list_products()])