# app.py
import streamlit as st
import sqlite3
import hashlib
from datetime import datetime

DB_PATH = "eco_finds.db"

# ---------------------------
# Utilities: DB + Security
# ---------------------------
def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def run(query, params=(), fetchone=False, fetchall=False, commit=False):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(query, params)
    if commit:
        conn.commit()
    if fetchone:
        r = cur.fetchone()
        conn.close()
        return r
    if fetchall:
        r = cur.fetchall()
        conn.close()
        return r
    conn.close()
    return None

def hash_pwd(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def init_db():
    run("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        username TEXT
    )""", commit=True)

    run("""
    CREATE TABLE IF NOT EXISTS categories(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )""", commit=True)

    run("""
    CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        category TEXT NOT NULL,
        price REAL NOT NULL,
        image TEXT,
        created_at TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )""", commit=True)

    run("""
    CREATE TABLE IF NOT EXISTS cart(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL DEFAULT 1,
        UNIQUE(user_id, product_id)
    )""", commit=True)

    run("""
    CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        created_at TEXT NOT NULL
    )""", commit=True)

    run("""
    CREATE TABLE IF NOT EXISTS order_items(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        title TEXT,
        price REAL,
        quantity INTEGER NOT NULL
    )""", commit=True)

    # Seed categories
    default_cats = [
        "Clothes","Books","Electronics","Furniture","Accessories",
        "Sports Equipment","Home Decor","Beauty & Personal Care",
        "Toys & Games","Kitchenware"
    ]
    for c in default_cats:
        run("INSERT OR IGNORE INTO categories(name) VALUES(?)", (c,), commit=True)

    # Seed a few demo products for browsing (owned by no user until someone creates—use user_id 1 if exists)
    user1 = run("SELECT id FROM users WHERE id=1", fetchone=True)
    owner = user1[0] if user1 else None
    demo = [
        ("Leather Jacket","Gently used leather jacket.","Clothes",120.0,"placeholder.jpg"),
        ("Old Textbooks","Bundle of CS and Math books.","Books",30.0,"placeholder.jpg"),
        ("Wireless Earbuds","Working perfectly, lightly used.","Electronics",50.0,"placeholder.jpg"),
        ("Wooden Chair","Solid wood, minor scratches.","Furniture",80.0,"placeholder.jpg"),
        ("Yoga Mat","Like new.","Sports Equipment",20.0,"placeholder.jpg"),
    ]
    if owner:
        existing = run("SELECT COUNT(*) FROM products", fetchone=True)
        if existing and existing[0] == 0:
            now = datetime.utcnow().isoformat()
            for t,d,cat,p,img in demo:
                run("""INSERT INTO products(user_id,title,description,category,price,image,created_at)
                       VALUES(?,?,?,?,?,?,?)""",(owner,t,d,cat,p,img,now), commit=True)

# ---------------------------
# Auth helpers
# ---------------------------
def get_user_by_email(email):
    return run("SELECT id,email,password_hash,username FROM users WHERE email=?",(email,), fetchone=True)

def register_user(email, password, username=""):
    try:
        run("INSERT INTO users(email,password_hash,username) VALUES(?,?,?)",
            (email, hash_pwd(password), username), commit=True)
        return True, "Registered successfully."
    except sqlite3.IntegrityError:
        return False, "Email already exists."

def verify_login(email, password):
    u = get_user_by_email(email)
    if not u:
        return False, "No account found."
    if u[2] == hash_pwd(password):
        return True, u
    return False, "Incorrect password."

def update_profile(user_id, username=None, email=None, new_password=None):
    if username is not None:
        run("UPDATE users SET username=? WHERE id=?", (username, user_id), commit=True)
    if email is not None:
        # make sure unique
        exists = run("SELECT id FROM users WHERE email=? AND id<>?", (email, user_id), fetchone=True)
        if exists:
            return False, "Email already in use."
        run("UPDATE users SET email=? WHERE id=?", (email, user_id), commit=True)
    if new_password:
        run("UPDATE users SET password_hash=? WHERE id=?", (hash_pwd(new_password), user_id), commit=True)
    return True, "Profile updated."

# ---------------------------
# Product CRUD + Browse
# ---------------------------
def create_product(user_id, title, description, category, price, image="placeholder.jpg"):
    now = datetime.utcnow().isoformat()
    run("""INSERT INTO products(user_id,title,description,category,price,image,created_at)
           VALUES(?,?,?,?,?,?,?)""",
        (user_id,title,description,category,price,image,now), commit=True)

def get_my_products(user_id):
    rows = run("""SELECT id,title,description,category,price,image,created_at
                  FROM products WHERE user_id=? ORDER BY created_at DESC""",
               (user_id,), fetchall=True)
    return rows

def update_product(product_id, user_id, title, description, category, price, image):
    run("""UPDATE products SET title=?, description=?, category=?, price=?, image=?
           WHERE id=? AND user_id=?""",
        (title,description,category,price,image,product_id,user_id), commit=True)

def delete_product(product_id, user_id):
    run("DELETE FROM products WHERE id=? AND user_id=?", (product_id,user_id), commit=True)

def get_all_categories():
    rows = run("SELECT name FROM categories ORDER BY name", fetchall=True)
    return [r[0] for r in rows]

def browse_products(category=None, keyword=None, min_price=None, max_price=None, limit=100, offset=0):
    q = "SELECT id,title,description,category,price,image FROM products WHERE 1=1"
    params = []
    if category:
        q += " AND category=?"
        params.append(category)
    if keyword:
        q += " AND LOWER(title) LIKE ?"
        params.append("%"+keyword.lower()+"%")
    if min_price is not None:
        q += " AND price>=?"
        params.append(min_price)
    if max_price is not None:
        q += " AND price<=?"
        params.append(max_price)
    q += " ORDER BY id DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    return run(q, tuple(params), fetchall=True)

def get_product(product_id):
    return run("""SELECT id,user_id,title,description,category,price,image
                  FROM products WHERE id=?""",(product_id,), fetchone=True)

# ---------------------------
# Cart + Orders
# ---------------------------
def add_to_cart(user_id, product_id, qty=1):
    existing = run("SELECT id,quantity FROM cart WHERE user_id=? AND product_id=?",
                   (user_id, product_id), fetchone=True)
    if existing:
        new_q = existing[1] + qty
        run("UPDATE cart SET quantity=? WHERE id=?", (new_q, existing[0]), commit=True)
    else:
        run("INSERT INTO cart(user_id,product_id,quantity) VALUES(?,?,?)",
            (user_id, product_id, qty), commit=True)

def view_cart(user_id):
    return run("""SELECT c.product_id, p.title, p.price, c.quantity
                  FROM cart c JOIN products p ON c.product_id=p.id
                  WHERE c.user_id=?""",(user_id,), fetchall=True)

def update_cart_qty(user_id, product_id, qty):
    if qty <= 0:
        remove_from_cart(user_id, product_id)
    else:
        run("UPDATE cart SET quantity=? WHERE user_id=? AND product_id=?",
            (qty,user_id,product_id), commit=True)

def remove_from_cart(user_id, product_id):
    run("DELETE FROM cart WHERE user_id=? AND product_id=?",(user_id,product_id), commit=True)

def clear_cart(user_id):
    run("DELETE FROM cart WHERE user_id=?", (user_id,), commit=True)

def cart_total(user_id):
    items = view_cart(user_id)
    return sum(row[2]*row[3] for row in items) if items else 0.0

def checkout(user_id):
    items = view_cart(user_id)
    if not items:
        return False, "Cart is empty."
    now = datetime.utcnow().isoformat()
    run("INSERT INTO orders(user_id, created_at) VALUES(?,?)",(user_id, now), commit=True)
    order_id = run("SELECT last_insert_rowid()", fetchone=True)[0]
    for pid, title, price, qty in items:
        run("""INSERT INTO order_items(order_id,product_id,title,price,quantity)
               VALUES(?,?,?,?,?)""",(order_id, pid, title, price, qty), commit=True)
    clear_cart(user_id)
    return True, f"Order #{order_id} placed!"

def previous_purchases(user_id):
    return run("""SELECT o.id, o.created_at, SUM(oi.price*oi.quantity) as total
                  FROM orders o
                  JOIN order_items oi ON o.id=oi.order_id
                  WHERE o.user_id=?
                  GROUP BY o.id, o.created_at
                  ORDER BY o.id DESC""",(user_id,), fetchall=True)

def order_details(order_id):
    return run("""SELECT title, price, quantity FROM order_items
                  WHERE order_id=?""",(order_id,), fetchall=True)

# ---------------------------
# Streamlit UI
# ---------------------------
st.set_page_config(page_title="Eco-Finds", page_icon="🌱", layout="wide")
init_db()

if "user" not in st.session_state:
    st.session_state.user = None

# ---------- Auth Header ----------
col1, col2 = st.columns([1,3])
with col1:
    st.markdown("## 🌱 Eco-Finds")
with col2:
    if st.session_state.user:
        st.write(f"Logged in as **{st.session_state.user['username'] or st.session_state.user['email']}**")
        if st.button("Logout"):
            st.session_state.user = None
            st.rerun()

st.divider()

# ---------- Auth Forms (Login/Signup) ----------
def auth_block():
    tab_login, tab_signup = st.tabs(["Login", "Sign Up"])
    with tab_login:
        email = st.text_input("Email", key="login_email")
        pw = st.text_input("Password", type="password", key="login_pw")
        if st.button("Login"):
            ok, res = verify_login(email, pw)
            if ok:
                uid, em, _, uname = res
                st.session_state.user = {"id": uid, "email": em, "username": uname}
                st.success("Logged in!")
                st.rerun()
            else:
                st.error(res)
    with tab_signup:
        email = st.text_input("Email", key="signup_email")
        username = st.text_input("Username (can edit later)")
        pw = st.text_input("Password", type="password", key="signup_pw")
        pw2 = st.text_input("Confirm Password", type="password", key="signup_pw2")
        if st.button("Create account"):
            if pw != pw2:
                st.error("Passwords do not match.")
            elif not email or not pw:
                st.error("Email and password required.")
            else:
                ok, msg = register_user(email, pw, username)
                if ok:
                    st.success(msg + " Now login.")
                else:
                    st.error(msg)

# If not logged in, only show browsing + auth
if not st.session_state.user:
    left, right = st.columns([2,3])
    with left:
        st.subheader("Browse Listings")
        cats = ["All"] + get_all_categories()
        cat = st.selectbox("Category", cats)
        kw = st.text_input("Keyword (in title)")
        min_p, max_p = st.columns(2)
        with min_p:
            min_price = st.number_input("Min Price", min_value=0.0, value=0.0)
        with max_p:
            max_price = st.number_input("Max Price", min_value=0.0, value=100000.0)
        btn = st.button("Search")

        if btn:
            use_cat = None if cat=="All" else cat
            rows = browse_products(category=use_cat,
                                   keyword=kw or None,
                                   min_price=min_price,
                                   max_price=max_price)
        else:
            rows = browse_products(limit=30)

        for pid, title, desc, ccat, price, image in rows:
            with st.container(border=True):
                st.write(f"**{title}** — ₹{price} | *{ccat}*")
                st.caption(desc or "")
                st.image("https://via.placeholder.com/300x180?text=Image", width=300)
                st.write(f"Product ID: {pid}")

    with right:
        st.subheader("Login / Sign Up")
        auth_block()
    st.stop()

# ---------- Main App (Logged-in) ----------
page = st.sidebar.radio("Navigate", [
    "Dashboard",
    "Profile",
    "Browse",
    "My Listings (CRUD)",
    "Cart",
    "Previous Purchases"
])

user = st.session_state.user

# Dashboard
if page == "Dashboard":
    st.subheader("User Dashboard")
    st.info("You can edit all fields in your Profile, manage your Listings, browse products, add to cart, and checkout.")
    # Quick stats
    c1, c2, c3 = st.columns(3)
    with c1:
        count_my = run("SELECT COUNT(*) FROM products WHERE user_id=?", (user["id"],), fetchone=True)[0]
        st.metric("My Listings", count_my)
    with c2:
        cart_items = view_cart(user["id"])
        st.metric("Cart Items", sum(i[3] for i in cart_items) if cart_items else 0)
    with c3:
        orders_count = run("SELECT COUNT(*) FROM orders WHERE user_id=?", (user["id"],), fetchone=True)[0]
        st.metric("Orders", orders_count)

# Profile
elif page == "Profile":
    st.subheader("Edit Profile")
    urow = run("SELECT email,username FROM users WHERE id=?", (user["id"],), fetchone=True)
    email_cur, username_cur = urow
    with st.form("profile_form"):
        new_username = st.text_input("Username", value=username_cur or "")
        new_email = st.text_input("Email", value=email_cur)
        new_pw = st.text_input("New Password (optional)", type="password")
        submitted = st.form_submit_button("Save")
        if submitted:
            ok, msg = update_profile(user["id"],
                                     username=new_username,
                                     email=new_email,
                                     new_password=new_pw if new_pw else None)
            if ok:
                st.session_state.user["username"] = new_username
                st.session_state.user["email"] = new_email
                st.success(msg)
            else:
                st.error(msg)

# Browse (with add to cart + detail)
elif page == "Browse":
    st.subheader("Browse Listings")
    cols = st.columns([1,1,1,1])
    cats = ["All"] + get_all_categories()
    with cols[0]:
        cat = st.selectbox("Category", cats)
    with cols[1]:
        kw = st.text_input("Keyword in title")
    with cols[2]:
        min_price = st.number_input("Min Price", min_value=0.0, value=0.0)
    with cols[3]:
        max_price = st.number_input("Max Price", min_value=0.0, value=100000.0)
    if st.button("Search"):
        use_cat = None if cat=="All" else cat
        rows = browse_products(category=use_cat, keyword=kw or None,
                               min_price=min_price, max_price=max_price, limit=200)
    else:
        rows = browse_products(limit=50)

    for pid, title, desc, ccat, price, image in rows:
        with st.container(border=True):
            c1, c2 = st.columns([3,1])
            with c1:
                st.write(f"### {title}  —  ₹{price}")
                st.caption(f"Category: {ccat}")
                st.write(desc or "")
                if st.button(f"View Details #{pid}", key=f"detail_{pid}"):
                    p = get_product(pid)
                    if p:
                        _, owner_id, t, d, catx, pr, img = p
                        st.info(f"**{t}**\n\n{d or 'No description'}\n\nCategory: *{catx}* | Price: ₹{pr}")
                        st.image("https://via.placeholder.com/600x300?text=Image", width=500)
            with c2:
                qty = st.number_input(f"Qty #{pid}", min_value=1, value=1, key=f"qty_{pid}")
                if st.button(f"Add to Cart #{pid}", key=f"add_{pid}"):
                    add_to_cart(user["id"], pid, int(qty))
                    st.success("Added to cart.")

# My Listings (CRUD)
elif page == "My Listings (CRUD)":
    st.subheader("My Product Listings")
    st.markdown("#### Create a New Listing")
    cats = get_all_categories()
    with st.form("create_form", clear_on_submit=True):
        title = st.text_input("Title")
        description = st.text_area("Description")
        category = st.selectbox("Category", cats)
        price = st.number_input("Price (₹)", min_value=0.0, step=10.0)
        image = st.text_input("Image Placeholder (URL or text)", value="placeholder.jpg")
        submit = st.form_submit_button("Create")
        if submit:
            if not title or price <= 0:
                st.error("Title and positive price are required.")
            else:
                create_product(user["id"], title, description, category, price, image)
                st.success("Listing created!")

    st.markdown("#### Your Listings")
    rows = get_my_products(user["id"])
    if not rows:
        st.info("No listings yet.")
    for pid, title, desc, ccat, price, image, created_at in rows:
        with st.expander(f"{title} — ₹{price}  |  {ccat}"):
            st.caption(f"Created: {created_at}")
            ct1, ct2 = st.columns(2)
            with ct1:
                new_title = st.text_input("Title", value=title, key=f"t_{pid}")
                new_desc = st.text_area("Description", value=desc or "", key=f"d_{pid}")
                new_cat = st.selectbox("Category", cats, index=cats.index(ccat) if ccat in cats else 0, key=f"c_{pid}")
            with ct2:
                new_price = st.number_input("Price (₹)", min_value=0.0, value=float(price), key=f"p_{pid}")
                new_img = st.text_input("Image Placeholder", value=image or "placeholder.jpg", key=f"i_{pid}")
                if st.button("Save Changes", key=f"save_{pid}"):
                    update_product(pid, user["id"], new_title, new_desc, new_cat, float(new_price), new_img)
                    st.success("Updated.")
                    st.rerun()
                if st.button("Delete", key=f"del_{pid}"):
                    delete_product(pid, user["id"])
                    st.warning("Deleted.")
                    st.rerun()

# Cart
elif page == "Cart":
    st.subheader("Your Cart")
    items = view_cart(user["id"])
    if not items:
        st.info("Cart is empty.")
    else:
        total = 0.0
        for pid, title, price, qty in items:
            total += price*qty
            c1, c2, c3, c4 = st.columns([3,2,2,2])
            with c1:
                st.write(f"**{title}**")
            with c2:
                st.write(f"₹{price} x {qty} = ₹{price*qty:.2f}")
            with c3:
                nqty = st.number_input(f"Qty for {title}", min_value=0, value=int(qty), key=f"qty_cart_{pid}")
                if st.button(f"Update {title}", key=f"upd_{pid}"):
                    update_cart_qty(user["id"], pid, int(nqty))
                    st.success("Cart updated.")
                    st.rerun()
            with c4:
                if st.button(f"Remove {title}", key=f"rm_{pid}"):
                    remove_from_cart(user["id"], pid)
                    st.warning("Removed.")
                    st.rerun()
        st.markdown(f"### Total: ₹{total:.2f}")
        colA, colB = st.columns(2)
        with colA:
            if st.button("Checkout"):
                ok, msg = checkout(user["id"])
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
        with colB:
            if st.button("Clear Cart"):
                clear_cart(user["id"])
                st.warning("Cart cleared.")
                st.rerun()

# Previous Purchases
elif page == "Previous Purchases":
    st.subheader("Previous Purchases")
    orders = previous_purchases(user["id"])
    if not orders:
        st.info("No previous orders.")
    else:
        for oid, created_at, total in orders:
            with st.expander(f"Order #{oid} — ₹{total:.2f} — {created_at}"):
                items = order_details(oid)
                for t, price, qty in items:
                    st.write(f"- **{t}** — ₹{price} x {qty} = ₹{price*qty:.2f}")
