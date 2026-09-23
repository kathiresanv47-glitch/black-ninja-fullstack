from flask import Flask, render_template, request, redirect, url_for, jsonify
import mysql.connector
from datetime import datetime, timedelta
import threading
import time

app = Flask(__name__)


# =========================
# MySQL Database Connection
# =========================
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="black_ninja"
    )


# =========================
# Automatic Order Status
# =========================
def automatic_order_status(order_id):

    time.sleep(10 * 60)

    update_order_status(order_id, "Preparing")

    time.sleep(10 * 60)

    update_order_status(order_id, "Packed")

    time.sleep(10 * 60)

    update_order_status(order_id, "Out for Delivery")

    time.sleep(15 * 60)

    update_order_status(order_id, "Delivered")
# =========================
# Update Status in Database
# =========================
def update_order_status(order_id, status):

    db = get_db_connection()
    cursor = db.cursor()

    sql = """
        UPDATE orders
        SET order_status = %s
        WHERE id = %s
    """

    cursor.execute(sql, (status, order_id))

    db.commit()

    cursor.close()
    db.close()

    print(f"Order #{order_id} status changed to: {status}")


# =========================
# Home Page
# =========================
@app.route("/")
def home():
    return render_template("index.html")


# =========================
# Save Order
# =========================
@app.route("/save_order", methods=["POST"])
def save_order():

    try:

        name = request.form.get("name")
        phone = request.form.get("phone")
        address = request.form.get("address")

        regular_qty = request.form.get("regular_qty", 0)
        king_qty = request.form.get("king_qty", 0)
        maggi_qty = request.form.get("maggi_qty", 0)

        total = request.form.get("total", 0)
        payment = request.form.get("payment")

        order_status = "Order Placed"

        db = get_db_connection()
        cursor = db.cursor()

        sql = """
            INSERT INTO orders
            (
                customer_name,
                phone,
                address,
                regular_qty,
                king_qty,
                maggi_qty,
                total,
                payment_method,
                order_status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            name,
            phone,
            address,
            regular_qty,
            king_qty,
            maggi_qty,
            total,
            payment,
            order_status
        )

        cursor.execute(sql, values)

        db.commit()

        order_id = cursor.lastrowid

        cursor.close()
        db.close()

        print("----- NEW ORDER -----")
        print("Order ID:", order_id)
        print("Name:", name)
        print("Phone:", phone)
        print("Address:", address)
        print("Regular Shawarma:", regular_qty)
        print("King Plate:", king_qty)
        print("Maggi Soup:", maggi_qty)
        print("Total:", total)
        print("Payment:", payment)
        print("Status:", order_status)
        print("--------------------")

        # Automatic status tracking
        status_thread = threading.Thread(
            target=automatic_order_status,
            args=(order_id,)
        )

        status_thread.daemon = True
        status_thread.start()

        return redirect(
            url_for("track_order", order_id=order_id)
        )

    except Exception as e:

        print("================================")
        print("SAVE ORDER ERROR:")
        print(e)
        print("================================")

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

    # =====================================
    # Start Automatic Status Tracking
    # =====================================
    status_thread = threading.Thread(
        target=automatic_order_status,
        args=(order_id,)
    )

    status_thread.daemon = True
    status_thread.start()

    # Customer tracking page
    return redirect(
        url_for("track_order", order_id=order_id)
    )


# =========================
# Customer Order Tracking
# =========================
@app.route("/track/<int:order_id>")
def track_order(order_id):

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    sql = """
        SELECT *
        FROM orders
        WHERE id = %s
    """

    cursor.execute(sql, (order_id,))
    order = cursor.fetchone()

    cursor.close()
    db.close()

    if order is None:
        return "Order not found", 404

    return render_template(
        "track_order.html",
        order=order
    )


# =========================
# Live Order Status API
# =========================
@app.route("/order_status/<int:order_id>")
def order_status(order_id):

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    sql = """
        SELECT order_status
        FROM orders
        WHERE id = %s
    """

    cursor.execute(sql, (order_id,))
    order = cursor.fetchone()

    cursor.close()
    db.close()

    if order is None:
        return jsonify({
            "success": False,
            "message": "Order not found"
        }), 404

    return jsonify({
        "success": True,
        "status": order["order_status"]
    })


# =========================
# Owner - View All Orders
# =========================
@app.route("/owner/orders")
def owner_orders():

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    sql = """
        SELECT *
        FROM orders
        ORDER BY id DESC
    """

    cursor.execute(sql)
    orders = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "owner_orders.html",
        orders=orders
    )


# =========================
# Owner - Manual Update Status
# =========================
@app.route(
    "/owner/update_status/<int:order_id>",
    methods=["POST"]
)
def update_status(order_id):

    new_status = request.form.get("order_status")

    allowed_statuses = [
        "Order Placed",
        "Preparing",
        "Packed",
        "Out for Delivery",
        "Delivered",
        "Cancelled"
    ]

    if new_status not in allowed_statuses:
        return "Invalid status", 400

    db = get_db_connection()
    cursor = db.cursor()

    sql = """
        UPDATE orders
        SET order_status = %s
        WHERE id = %s
    """

    cursor.execute(
        sql,
        (new_status, order_id)
    )

    db.commit()

    cursor.close()
    db.close()

    return redirect(
        url_for("owner_orders")
    )


# =========================
# Run Flask Application
# =========================
if __name__ == "__main__":
    app.run(debug=True)