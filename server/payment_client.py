import json
import requests
from config.config import (
    MERCHANT_ID,
    SECRET_KEY,
    WEBHOOK_URL,
    BASE_URL,
    PAYMENT_CALLBACK_URL,
)


def create_payment(amount: int, user_id: int, tariff: str):
    # User is redirected to site URL, provider notifies server callback URL.
    payload = {
        "command": "process",
        "paymentMethod": 2,
        "paymentDetails": {"amount": amount, "currency": "RUB"},
        "description": f"VPN тариф {tariff}",
        "return": WEBHOOK_URL,
        "failedUrl": WEBHOOK_URL,
        "callback": PAYMENT_CALLBACK_URL,
        "callbackUrl": PAYMENT_CALLBACK_URL,
        "payload": json.dumps({"telegram_id": user_id, "tariff": tariff}),
    }

    headers = {
        "X-MerchantId": MERCHANT_ID,
        "X-Secret": SECRET_KEY,
        "Content-Type": "application/json",
    }

    response = requests.post(
        f"{BASE_URL}/transaction/process", json=payload, headers=headers, timeout=15
    )

    print("PLATEGA STATUS:", response.status_code)
    print("PLATEGA TEXT:", response.text)

    response.raise_for_status()
    return response.json()
