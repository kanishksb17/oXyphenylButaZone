import sqlite3
from datetime import datetime

class SQLiteDB:
    def __init__(self, db_path="app.db"):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        c = self.conn.cursor()
        # User table
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            password_hash TEXT NOT NULL
        )''')
        # Product table
        c.execute('''CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_email TEXT NOT NULL,
            title TEXT NOT NULL,
            desc TEXT,
            category TEXT,
            price REAL,
            image_url TEXT,
            FOREIGN KEY(owner_email) REFERENCES users(email)
        )''')
        # Cart table
        c.execute('''CREATE TABLE IF NOT EXISTS carts (
            user_email TEXT NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            PRIMARY KEY (user_email, product_id),
            FOREIGN KEY(user_email) REFERENCES users(email),
            FOREIGN KEY(product_id) REFERENCES products(id)
        )''')
        # Purchase table
        c.execute('''CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            product_id INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            product_snapshot TEXT,
            FOREIGN KEY(user_email) REFERENCES users(email),
            FOREIGN KEY(product_id) REFERENCES products(id)
        )''')
        self.conn.commit()

    # -- User methods --
    def add_user(self, email, username, password_hash):
        c = self.conn.cursor()
        try:
            c.execute("INSERT INTO users (email, username, password_hash) VALUES (?, ?, ?)",
                      (email, username, password_hash))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_user(self, email):
        c = self.conn.cursor()
        c.execute("SELECT email, username, password_hash FROM users WHERE email = ?", (email,))
        return c.fetchone()

    # -- Product methods --
    def add_product(self, owner_email, title, desc, category, price, image_url):
        c = self.conn.cursor()
        c.execute('''INSERT INTO products (owner_email, title, desc, category, price, image_url)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (owner_email, title, desc, category, price, image_url))
        self.conn.commit()
        return c.lastrowid

    def get_product(self, pid):
        c = self.conn.cursor()
        c.execute("SELECT * FROM products WHERE id = ?", (pid,))
        return c.fetchone()

    def list_products(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM products")
        return c.fetchall()

    # -- Cart methods --
    def add_to_cart(self, user_email, product_id, quantity=1):
        c = self.conn.cursor()
        c.execute('''INSERT INTO carts (user_email, product_id, quantity)
                     VALUES (?, ?, ?)
                     ON CONFLICT(user_email, product_id) DO UPDATE SET quantity=quantity+?''',
                  (user_email, product_id, quantity, quantity))
        self.conn.commit()

    def get_cart(self, user_email):
        c = self.conn.cursor()
        c.execute("SELECT product_id, quantity FROM carts WHERE user_email = ?", (user_email,))
        return c.fetchall()

    def remove_from_cart(self, user_email, product_id):
        c = self.conn.cursor()
        c.execute("DELETE FROM carts WHERE user_email = ? AND product_id = ?", (user_email, product_id))
        self.conn.commit()

    def clear_cart(self, user_email):
        c = self.conn.cursor()
        c.execute("DELETE FROM carts WHERE user_email = ?", (user_email,))
        self.conn.commit()

    # -- Purchase methods --
    def record_purchase(self, user_email, product_id):
        c = self.conn.cursor()
        # Take product snapshot as string
        product = self.get_product(product_id)
        product_snapshot = str(product)
        timestamp = datetime.now().isoformat()
        c.execute('''INSERT INTO purchases (user_email, product_id, timestamp, product_snapshot)
                     VALUES (?, ?, ?, ?)''',
                  (user_email, product_id, timestamp, product_snapshot))
        self.conn.commit()

    def get_purchase_history(self, user_email):
        c = self.conn.cursor()
        c.execute("SELECT product_snapshot, timestamp FROM purchases WHERE user_email = ?", (user_email,))
        return c.fetchall()

    def close(self):
        self.conn.close()