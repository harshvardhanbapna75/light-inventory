from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)
DB_NAME = "inventry.db"


# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product TEXT,
            wattage TEXT,
            body_color TEXT,
            cup_type TEXT,
            light_color TEXT,
            stock INTEGER,
            UNIQUE(product, wattage, body_color, cup_type, light_color)
        )
    """)
    conn.commit()
    conn.close()


def get_stock(p, w, b, c, l):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        SELECT stock FROM inventory
        WHERE product=? AND wattage=? AND body_color=? AND cup_type=? AND light_color=?
    """, (p, w, b, c, l))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 0


def save_stock(p, w, b, c, l, s):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO inventory (product, wattage, body_color, cup_type, light_color, stock)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(product, wattage, body_color, cup_type, light_color)
        DO UPDATE SET stock=excluded.stock
    """, (p, w, b, c, l, s))
    conn.commit()
    conn.close()


# ---------- ROUTES ----------
@app.route("/")
def home():
    return render_template("search.html")


@app.route("/search", methods=["POST"])
def search():
    return render_template("wattage.html", product=request.form["product"])


@app.route("/wattage", methods=["POST"])
def wattage():
    return render_template(
        "color.html",
        product=request.form["product"],
        wattage=request.form["wattage"]
    )


@app.route("/color", methods=["POST"])
def color():
    return render_template(
        "cup.html",
        product=request.form["product"],
        wattage=request.form["wattage"],
        body_color=request.form["body_color"]
    )


@app.route("/cup", methods=["POST"])
def cup():
    return render_template(
        "light_color.html",
        product=request.form["product"],
        wattage=request.form["wattage"],
        body_color=request.form["body_color"],
        cup_type=request.form["cup_type"]
    )


@app.route("/summary", methods=["POST"])
def summary():
    product = request.form["product"]
    wattage = request.form["wattage"]
    body_color = request.form["body_color"]
    cup_type = request.form["cup_type"]
    light_color = request.form["light_color"]

    stock = get_stock(product, wattage, body_color, cup_type, light_color)

    return render_template(
        "summary.html",
        product=product,
        wattage=wattage,
        body_color=body_color,
        cup_type=cup_type,
        light_color=light_color,
        stock=stock
    )


@app.route("/save_stock", methods=["POST"])
def save_stock_route():
    save_stock(
        request.form["product"],
        request.form["wattage"],
        request.form["body_color"],
        request.form["cup_type"],
        request.form["light_color"],
        int(request.form["stock"])
    )
    return redirect("/")


init_db()

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

