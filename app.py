
import os
import json
import secrets
import urllib.request
import urllib.error
from flask import Flask, jsonify, request

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
CHAT_ID = os.environ.get("CHAT_ID", "")
TEST_SECRET = os.environ.get("TEST_SECRET", "")


def send_telegram_message(message):
    if not BOT_TOKEN or not CHAT_ID:
        raise RuntimeError("BOT_TOKEN or CHAT_ID is missing")

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id": CHAT_ID,
        "text": message
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=15) as response:
        result = json.loads(response.read().decode("utf-8"))

    if not result.get("ok"):
        raise RuntimeError("Telegram rejected the message")

    return result


@app.route("/")
def home():
    return jsonify({
        "service": "Lata Borka House Notifications",
        "status": "running"
    })


@app.route("/test")
def test_notification():
    supplied_key = request.headers.get("X-Test-Key", "")

    if not TEST_SECRET or not secrets.compare_digest(
        supplied_key, TEST_SECRET
    ):
        return jsonify({"error": "Unauthorized"}), 401

    message = (
        "🛍️ New Order Placed! [TEST]\n\n"
        "Order Number: #LBH-TEST-001\n"
        "Date: Test Order\n"
        "Payment: Cash on Delivery\n"
        "Shipping: Standard Delivery\n\n"
        "Customer Info\n"
        "Name: Test Customer\n"
        "Phone: 01XXXXXXXXX\n"
        "Email: test@example.com\n"
        "Location: Test Address, Bangladesh\n\n"
        "Order Items (1)\n"
        "1. Sample Borka × 1 = ৳1,500\n\n"
        "Subtotal: ৳1,500\n"
        "Discount: ৳0\n"
        "Shipping: ৳80\n"
        "Total: ৳1,580\n\n"
        "⚠️ This is a test notification, not a real order."
    )

    try:
        send_telegram_message(message)
        return jsonify({"success": True, "message": "Test sent"})
    except Exception:
        app.logger.exception("Telegram test failed")
        return jsonify({
            "success": False,
            "error": "Telegram message could not be sent"
        }), 502
