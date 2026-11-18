from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

import sys

import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret-key"


PRODUCT_FILE = "data/products.json"
ORDER_FILE = "data/orders.json"
USER_FILE = "data/users.json"


def load_users():
    with open(USER_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_users(users):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4)

def load_products():
    with open(PRODUCT_FILE, encoding="utf-8") as f:
        return json.load(f)


def load_orders():
    with open(ORDER_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_orders(orders):
    with open(ORDER_FILE, "w", encoding="utf-8") as f:
        json.dump(orders, f, indent=4)


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        users = load_users()

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = next(
            (
                user for user in users
                if user["username"] == username
            ),
            None
        )

        if existing_user:

            flash("Username already exists")

            return redirect(
                url_for("register")
            )

        users.append({
            "username": username,
            "email": email,
            "password": password
        })

        save_users(users)

        flash("Registration successful")

        return redirect(
            url_for("login")
        )

    return render_template(
        "register.html"
    )

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        users = load_users()
        

        user = next(
            (
                user for user in users
                if user["username"] == username
            ),
            None
        )

        if user["password"] == password:
            

            session["user"] = username

            flash("Logged in")

            return redirect(
                url_for("home")
            )

        flash("Invalid credentials")

    return render_template(
        "login.html"
    )

@app.route("/logout")
def logout():

    session.clear()

    flash("Logged out")

    return redirect(
        url_for("home")
    )

from functools import wraps


def login_required(func):

    @wraps(func)

    def wrapper(*args, **kwargs):

        if "user" not in session:

            return redirect(
                url_for("login")
            )

        return func(*args, **kwargs)

    return wrapper

@app.route("/")
def home():

    products = load_products()

    return render_template(
        "index.html",
        products=products
    )


@app.route("/product/<int:product_id>")
def product(product_id):

    products = load_products()

    product = next(
        (
            p for p in products
            if p["id"] == product_id
        ),
        None
    )

    return render_template(
        "product.html",
        product=product
    )


@app.route("/add-to-cart/<int:product_id>")
def add_to_cart(product_id):

    cart = session.get("cart", [])

    cart.append(product_id)

    session["cart"] = cart

    return redirect(url_for("cart"))


@app.route("/cart")
def cart():

    products = load_products()

    cart_ids = session.get("cart", [])

    items = [
        p for p in products
        if p["id"] in cart_ids
    ]

    total = sum(
        item["price"]
        for item in items
    )

    return render_template(
        "cart.html",
        items=items,
        total=total
    )

@app.route("/profile")
@login_required
def profile():

    username = session.get("user")

    users = load_users()

    user = next(
        (u for u in users if u["username"] == username),
        None
    )

    if user is None:
        flash("User not found")
        return redirect(url_for("logout"))

    return render_template(
        "profile.html",
        user=user
    )

@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():

    if request.method == "POST":

        orders = load_orders()

        products = load_products()

        cart_ids = session.get("cart", [])

        order_items = [
            p for p in products
            if p["id"] in cart_ids
        ]

        total = sum(
            item["price"]
            for item in order_items
        )

        order = {
            "customer": request.form["name"],
            "email": request.form["email"],
            "date": datetime.now().isoformat(),
            "items": order_items,
            "total": total
        }

        orders.append(order)

        save_orders(orders)

        session["cart"] = []

        return render_template(
            "success.html",
            order=order
        )

    return render_template(
        "checkout.html"
    )


@app.route("/admin/orders")
def orders():

    return render_template(
        "orders.html",
        orders=load_orders()
    )


if __name__ == "__main__":
    app.run(debug=True)