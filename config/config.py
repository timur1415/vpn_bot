import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
REVIEW = int(os.getenv("REVIEW"))
MERCHANT_ID = os.getenv('MERCHANT_ID')
SECRET_KEY = os.getenv('SECRET_KEY')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
TELEGRAM_WEBHOOK_PATH = os.getenv('TELEGRAM_WEBHOOK_PATH')
SECRET_TOKEN = os.getenv('SECRET_TOKEN')
BASE_URL = os.getenv('BASE_URL')