import logging
from telegram.ext import ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto

from server.payment_client import create_payment
from db.db import save_payment, has_used_free_trial, activate_free_trial, get_paid_user
from config.config import ADMIN_ID

logger = logging.getLogger(__name__)


TARIFFS = {
    "buy_7days": {"title": "7 дней - 59 руб.", "amount": 59},
    "buy_1month": {"title": "1 месяц - 199 руб.", "amount": 199},
    "buy_3month": {"title": "3 месяца - 499 руб.", "amount": 499},
    "buy_6month": {"title": "6 месяцев - 899 руб.", "amount": 899},
    "buy_12month": {"title": "12 месяцев - 1499 руб.", "amount": 1499},
}


PURCHASE_INFO_TEXT = (
    "🔐 maksud_vpn\n\n"
    "После оплаты с вами свяжется менеджер и отправит ключ для подключения к Amnezia VPN.\n\n"
    "📲 Скачайте приложение заранее:\n\n"
    "iPhone / iOS:\n"
    "https://apps.apple.com/us/app/amneziavpn/id1600529900\n\n"
    "⚠️ Важно: для iPhone в App Store может понадобиться регион ТУРЦИИ, если приложение не отображается в вашем регионе.\n\n"
    "Android:\n"
    "https://play.google.com/store/apps/details?id=org.amnezia.vpn\n\n"
    "Порядок такой:\n\n"
    "1️⃣ Вы оплачиваете тариф\n"
    "2️⃣ Менеджер проверяет оплату\n"
    "3️⃣ Вам отправляют VPN-ключ\n"
    "4️⃣ При необходимости помогают подключиться\n\n"
    "⏳ Обычно выдача занимает 5–15 минут.\n\n"
    "Перед оплатой убедитесь, что вам можно написать в личные сообщения Telegram."
)


FREE_TRIAL_INFO_TEXT = (
    "🔐 maksud_vpn\n\n"
    "Пробный тариф активирован на 3 дня. С вами свяжется менеджер и отправит ключ для подключения к Amnezia VPN.\n\n"
    "📲 Скачайте приложение заранее:\n\n"
    "iPhone / iOS:\n"
    "https://apps.apple.com/us/app/amneziavpn/id1600529900\n\n"
    "⚠️ Важно: для iPhone в App Store может понадобиться регион ТУРЦИИ, если приложение не отображается в вашем регионе.\n\n"
    "Android:\n"
    "https://play.google.com/store/apps/details?id=org.amnezia.vpn\n\n"
    "Порядок такой:\n\n"
    "1️⃣ Вы активируете пробный тариф\n"
    "2️⃣ Менеджер отправляет VPN-ключ\n"
    "3️⃣ При необходимости помогает подключиться\n\n"
    "⏳ Обычно выдача занимает 5–15 минут.\n\n"
    "Убедитесь, что вам можно написать в личные сообщения Telegram."
)


async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    free_trial_used = await has_used_free_trial(user_id)

    keyboard = [
        *([] if free_trial_used else [[InlineKeyboardButton("🎁 3 дня бесплатно", callback_data="buy_free3days")]]),
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

    user_id = update.effective_user.id
    username = update.effective_user.username

    if query.data == "buy_free3days":
        activated = await activate_free_trial(user_id, username=username)

        if activated:
            try:
                paid_user = await get_paid_user(user_id)
                await context.bot.send_message(
                    chat_id=ADMIN_ID,
                    text=(
                        "🎁 Активирован бесплатный тариф\n"
                        f"ID: {user_id}\n"
                        f"Username: {f'@{username}' if username else '-'}\n"
                        "Тариф: 3 дня бесплатно\n"
                        f"Действует до: {paid_user.expires_at if paid_user else '-'}"
                    ),
                )
            except Exception as notify_exc:
                logger.error("Failed to notify admin about free trial activation: %s", notify_exc)

            await query.edit_message_caption(
                caption=FREE_TRIAL_INFO_TEXT,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🏠 В главное меню", callback_data="main_menu")],
                    [InlineKeyboardButton("💳 К тарифам", callback_data="buy")],
                ]),
                parse_mode="HTML",
            )
        else:
            await query.edit_message_caption(
                caption=(
                    "⚠️ Пробный тариф уже использован\n\n"
                    "Бесплатный доступ на 3 дня можно активировать только один раз."
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("💳 Выбрать платный тариф", callback_data="buy")],
                    [InlineKeyboardButton("🏠 В главное меню", callback_data="main_menu")],
                ]),
            )
        return

    tariff = TARIFFS[query.data]

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

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Оплатить", url=payment_url)],
        [InlineKeyboardButton("⬅️ Назад к тарифам", callback_data="buy")],
    ])

    await query.edit_message_caption(
        caption=PURCHASE_INFO_TEXT,
        reply_markup=keyboard,
        parse_mode="HTML",
    )