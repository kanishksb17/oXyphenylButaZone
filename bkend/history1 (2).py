class PurchaseHistoryManager:
    def __init__(self):
        # Each purchase: {user_email, product_id, timestamp, product_snapshot}
        self.purchases = []

    def record_purchase(self, user_email, product, timestamp):
        """
        Records a purchase for the user.
        :param user_email: str - email of the purchaser
        :param product: dict - product info (must have at least 'id')
        :param timestamp: str/datetime - when the purchase happened
        """
        # Take a snapshot of the product at the time of purchase
        product_snapshot = product.copy()
        self.purchases.append({
            "user_email": user_email,
            "product_id": product.get("id"),
            "timestamp": timestamp,
            "product_snapshot": product_snapshot
        })
        return True

    def get_purchase_history(self, user_email):
        """
        Returns a list of purchases for the given user.
        Each item includes: product info at purchase time, timestamp
        """
        return [
            {
                "product": purchase["product_snapshot"],
                "timestamp": purchase["timestamp"]
            }
            for purchase in self.purchases
            if purchase["user_email"] == user_email
        ]