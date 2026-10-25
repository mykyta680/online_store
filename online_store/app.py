from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)
DB_NAME = "store.db"


def get_db():
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def product_to_dict(product):
    return dict(product)


@app.route("/api/products", methods=["GET"])
def get_products():
    with get_db() as db:
        products = db.execute(
            "SELECT * FROM products ORDER BY id"
        ).fetchall()

    return jsonify([product_to_dict(p) for p in products])


@app.route("/api/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    with get_db() as db:
        product = db.execute(
            "SELECT * FROM products WHERE id = ?",
            (product_id,)
        ).fetchone()

    if product is None:
        return jsonify({"error": "Product not found"}), 404

    return jsonify(product_to_dict(product))


@app.route("/api/products", methods=["POST"])
def create_product():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "JSON object required"}), 400

    name = data.get("name")
    price = data.get("price")
    description = data.get("description", "")
    stock = data.get("stock", 0)

    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "Name is required"}), 400

    if not isinstance(description, str):
        return jsonify({"error": "Description must be text"}), 400

    if (
        isinstance(price, bool)
        or not isinstance(price, (int, float))
        or price < 0
    ):
        return jsonify({"error": "Invalid price"}), 400

    if (
        isinstance(stock, bool)
        or not isinstance(stock, int)
        or stock < 0
    ):
        return jsonify({"error": "Invalid stock"}), 400

    with get_db() as db:
        cursor = db.execute(
            """INSERT INTO products (name, description, price, stock)
               VALUES (?, ?, ?, ?)""",
            (name.strip(), description, price, stock)
        )
        product_id = cursor.lastrowid

    return jsonify({
        "message": "Product created",
        "id": product_id
    }), 201


@app.route("/api/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "JSON object required"}), 400

    name = data.get("name")
    price = data.get("price")
    description = data.get("description", "")
    stock = data.get("stock", 0)

    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "Name is required"}), 400

    if not isinstance(description, str):
        return jsonify({"error": "Description must be text"}), 400

    if (
        isinstance(price, bool)
        or not isinstance(price, (int, float))
        or price < 0
    ):
        return jsonify({"error": "Invalid price"}), 400

    if (
        isinstance(stock, bool)
        or not isinstance(stock, int)
        or stock < 0
    ):
        return jsonify({"error": "Invalid stock"}), 400

    with get_db() as db:
        cursor = db.execute(
            """UPDATE products
               SET name = ?, description = ?, price = ?, stock = ?
               WHERE id = ?""",
            (name.strip(), description, price, stock, product_id)
        )

        if cursor.rowcount == 0:
            return jsonify({"error": "Product not found"}), 404

    return jsonify({"message": "Product updated"})


@app.route("/api/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    with get_db() as db:
        cursor = db.execute(
            "DELETE FROM products WHERE id = ?",
            (product_id,)
        )

        if cursor.rowcount == 0:
            return jsonify({"error": "Product not found"}), 404

    return jsonify({"message": "Product deleted"})

@app.route("/")
def home():
    return render_template("index.html")
if __name__ == "__main__":
    app.run(debug=True)
