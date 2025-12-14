





from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "cleanmate_secret_2025"

# ---------------- PRICING ----------------
PRICES = {
    "Home Cleaning": 25,
    "Office Cleaning": 40,
    "Deep Cleaning": 60,
    "Move-in / Move-out": 80
}

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect("cleanmate.db")
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            service TEXT,
            address TEXT,
            price INTEGER
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        )
    """)

    c.execute("SELECT * FROM admin")
    if not c.fetchone():
        c.execute(
            "INSERT INTO admin (username, password) VALUES (?, ?)",
            ("admin", "admin123")
        )

    conn.commit()
    conn.close()

init_db()

# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return render_template("index.html")

from urllib.parse import quote

@app.route("/book", methods=["GET", "POST"])
def book():
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        service = request.form["service"]
        address = request.form["address"]

        price = PRICES.get(service, 0)

        # Save to database
        conn = sqlite3.connect("cleanmate.db")
        c = conn.cursor()
        c.execute(
            "INSERT INTO bookings (name, phone, service, address, price) VALUES (?, ?, ?, ?, ?)",
            (name, phone, service, address, price)
        )
        conn.commit()
        conn.close()

        # WhatsApp notification
        admin_phone = "263714798067"  # 👈 CHANGE THIS
        message = f"""
🧼 *NEW CLEANMATE BOOKING*

👤 Name: {name}
📞 Phone: {phone}
🧹 Service: {service}
📍 Address: {address}
💰 Price: ${price}
"""
        whatsapp_url = f"https://wa.me/{admin_phone}?text={quote(message)}"

        return redirect(whatsapp_url)

    return render_template("book.html", prices=PRICES)

@app.route("/success")
def success():
    return render_template("success.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("cleanmate.db")
        c = conn.cursor()
        c.execute(
            "SELECT * FROM admin WHERE username=? AND password=?",
            (username, password)
        )
        admin = c.fetchone()
        conn.close()

        if admin:
            session["admin"] = True
            return redirect(url_for("admin"))
        else:
            error = "Invalid login details"

    return render_template("login.html", error=error)

@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect(url_for("login"))

    conn = sqlite3.connect("cleanmate.db")
    c = conn.cursor()
    c.execute("SELECT * FROM bookings ORDER BY id DESC")
    bookings = c.fetchall()
    conn.close()

    return render_template("admin.html", bookings=bookings)

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("login"))

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
