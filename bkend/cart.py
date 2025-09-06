from typing import List, Dict, Optional
from product import get_product, Product

# In-memory storage for carts: user_email -> list of product IDs
carts: Dict[str, List[int]] = {}

# Add product to cart
def add_to_cart(user_email: str, product_id: int) -> bool:
    if get_product(product_id) is None:
        return False
    if user_email not in carts:
        carts[user_email] = []
    if product_id not in carts[user_email]:
        carts[user_email].append(product_id)
        return True
    return False  # Already in cart

# Remove product from cart
def remove_from_cart(user_email: str, product_id: int) -> bool:
    if user_email not in carts or product_id not in carts[user_email]:
        return False
    carts[user_email].remove(product_id)
    return True

# View cart contents (returns list of Product objects)
def view_cart(user_email: str) -> List[Product]:
    if user_email not in carts:
        return []
    return [get_product(pid) for pid in carts[user_email] if get_product(pid) is not None]

# Example usage
if __name__ == "__main__":
    # Assume some products exist with IDs 1 and 2, and user "alice@example.com"
    print(add_to_cart("alice@example.com", 1))  # True if added
    print(add_to_cart("alice@example.com", 2))  # True if added
    print(view_cart("alice@example.com"))  # List of Product objects
    print(remove_from_cart("alice@example.com", 2))  # True if removed
    print(view_cart("alice@example.com"))  # Should show only product with ID 1 