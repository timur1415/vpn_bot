import logging
from telegram.ext import ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto

from server.payment_client import create_payment
from db.db import save_payment

logger = logging.getLogger(__name__)


TARIFFS = {
    "buy_7days": {"title": "7 дней - 59 руб.", "amount": 59},
    "buy_1month": {"title": "1 месяц - 199 руб.", "amount": 199},
    "buy_3month": {"title": "3 месяца - 499 руб.", "amount": 499},
    "buy_6month": {"title": "6 месяцев - 899 руб.", "amount": 899},
    "buy_12month": {"title": "12 месяцев - 1499 руб.", "amount": 1499},
}


async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("🗓 7 дней - 59 руб.", callback_data="buy_7days")],
        [InlineKeyboardButton("📅 1 месяц - 199 руб.", callback_data="buy_1month")],
        [InlineKeyboardButton("🧭 3 месяца - 499 руб.", callback_data="buy_3month")],
        [InlineKeyboardButton("🛫 6 месяцев - 899 руб.", callback_data="buy_6month")],
        [InlineKeyboardButton("🏆 12 месяцев - 1499 руб.", callback_data="buy_12month")],
        [InlineKeyboardButton("🏠 В главное меню", callback_data="main_menu")],
    ]

    await query.edit_message_media(
        media=InputMediaPhoto(
            media=open("photo/chill.jpg", "rb"),
            caption=(
                "<b>Выберите тарифный план</b>\n\n"
                "Ниже собраны все доступные варианты.\n"
                "После выбора вы получите кнопку для оплаты."
            ),
            parse_mode="HTML",
        ),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def buy_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    tariff = TARIFFS[query.data]
    user_id = update.effective_user.id

    payment = create_payment(
        amount=tariff["amount"],
        user_id=user_id,
        tariff=tariff["title"],
    )
    logger.info(payment)
    payment_url = payment.get("redirect")
    transaction_id = payment.get("transactionId", "")

    if transaction_id:
        try:
            await save_payment(
                transaction_id=transaction_id,
                telegram_id=user_id,
                tariff=tariff["title"],
                amount=tariff["amount"],
            )
        except Exception as e:
            logger.error("Failed to save payment to DB: %s", e)

    # success danger primary 
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Оплатить", url=payment_url,style='success')],
        [InlineKeyboardButton("⬅️ Назад к тарифам", callback_data="buy")],
    ])

    await query.edit_message_caption(
        caption=(
            "🔐 maksud_vpn\n\n"
            "После оплаты с вами свяжется менеджер и отправит ключ для подключения к Amnezia VPN.\n\n"
            "📲 Скачайте приложение заранее:\n\n"
            "iPhone / iOS:\n"
            "https://apps.apple.com/us/app/amneziavpn/id1600529900\n\n"
            "⚠️ Важно: для iPhone в App Store может понадобиться регион Узбекистан, если приложение не отображается в вашем регионе.\n\n"
            "Android:\n"
            "https://play.google.com/store/apps/details?id=org.amnezia.vpn\n\n"
            "Порядок такой:\n\n"
            "1️⃣ Вы оплачиваете тариф\n"
            "2️⃣ Менеджер проверяет оплату\n"
            "3️⃣ Вам отправляют VPN-ключ\n"
            "4️⃣ При необходимости помогают подключиться\n\n"
            "⏳ Обычно выдача занимает 5–15 минут.\n\n"
            "Перед оплатой убедитесь, что вам можно написать в личные сообщения Telegram."
        ),
        reply_markup=keyboard,
        parse_mode="HTML",
    )