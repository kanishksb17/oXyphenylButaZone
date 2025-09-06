import sqlite3

# Function to fetch a single product by ID
def get_product_details(product_id):
    conn = sqlite3.connect('eco_finds.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id=?", (product_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        product = {
            "id": row[0],
            "title": row[1],
            "category": row[2],
            "price": row[3],
            "image": row[4],
            "description": f"This is a detailed description for {row[1]}."
        }
        return product
    else:
        return None

# Example usage
if __name__ == "__main__":
    product_id = 3  # For example
    details = get_product_details(product_id)
    if details:
        print(details)
    else:
        print("Product not found.")
