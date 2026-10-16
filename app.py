
import os
import json
import secrets
import urllib.request
from flask import Flask, jsonify, request, render_template_string

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
CHAT_ID = os.environ.get("CHAT_ID", "")
TEST_SECRET = os.environ.get("TEST_SECRET", "")


def send_telegram_message(message):
    if not BOT_TOKEN or not CHAT_ID:
        raise RuntimeError("Bot configuration missing")

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
        raise RuntimeError("Telegram rejected message")


@app.route("/")
def home():
    return jsonify({
        "service": "Lata Borka House Notifications",
        "status": "running"
    })


@app.route("/test", methods=["GET", "POST"])
def test_notification():
    if request.method == "GET":
        return render_template_string("""
        <!doctype html>
        <html lang="en">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>LBH Notification Test</title>
        <body style="font-family:Arial;max-width:420px;margin:40px auto;padding:16px">
        <h2>LBH Telegram Test</h2>
        <p>Send a sample notification to your Telegram.</p>
        <form method="post">
        <label>Test Secret</label><br>
        <input type="password" name="test_secret" required
        style="width:95%;padding:12px;margin:10px 0">
        <button type="submit" style="padding:12px 18px">
        Send Test Notification
        </button>
        </form>
        </body>
        </html>
        """)

    supplied_key = request.form.get("test_secret", "")

    if not TEST_SECRET or not secrets.compare_digest(
        supplied_key, TEST_SECRET
    ):
        return "Unauthorized: check your test secret.", 401

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
        return "Success! Check your Telegram for the test notification."
    except Exception:
        app.logger.exception("Telegram test failed")
        return "Telegram message failed. Check Render logs.", 502
