import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
REVIEW = int(os.getenv("REVIEW"))


def _env(name: str, default: str = "") -> str:
	# Strip accidental trailing spaces from .env values (common with copied URLs).
	return (os.getenv(name, default) or default).strip()


MERCHANT_ID = _env("MERCHANT_ID")
SECRET_KEY = _env("SECRET_KEY")
WEBHOOK_URL = _env("WEBHOOK_URL").rstrip("/")
TELEGRAM_WEBHOOK_PATH = _env("TELEGRAM_WEBHOOK_PATH")
SECRET_TOKEN = _env("SECRET_TOKEN")
BASE_URL = _env("BASE_URL").rstrip("/")

PAYMENT_CALLBACK_PATH = "/cp/payment/callback"
PAYMENT_CALLBACK_URL = f"{WEBHOOK_URL}{PAYMENT_CALLBACK_PATH}"