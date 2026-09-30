import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, Update
from telegram.ext import ContextTypes

from config.config import ADMIN_ID
from db.db import activate_free_trial, get_paid_user, has_used_free_trial, save_payment
from server.payment_client import create_payment

logger = logging.getLogger(__name__)


TARIFFS = {
    "buy_7days": {"title": "7 дней - 59 руб.", "amount": 59},
    "buy_1month": {"title": "1 месяц - 199 руб.", "amount": 199},
    "buy_3month": {"title": "3 месяца - 499 руб.", "amount": 499},
    "buy_6month": {"title": "6 месяцев - 899 руб.", "amount": 899},
    "buy_12month": {"title": "12 месяцев - 1499 руб.", "amount": 1499},
    "buy_7days_1config": {"title": "7 дней - 99 руб.", "amount": 99},
    "buy_1month_1config": {"title": "1 месяц - 349 руб.", "amount": 349},
    "buy_3month_1config": {"title": "3 месяца - 899 руб.", "amount": 899},
    "buy_6month_1config": {"title": "6 месяцев - 1599 руб.", "amount": 1599},
    "buy_12month_1config": {"title": "12 месяцев - 2699 руб.", "amount": 2699},
    "buy_7days_2config": {"title": "7 дней - 99 руб.", "amount": 99},
    "buy_1month_2config": {"title": "1 месяц - 349 руб.", "amount": 349},
    "buy_3month_2config": {"title": "3 месяца - 899 руб.", "amount": 899},
    "buy_6month_2config": {"title": "6 месяцев - 1599 руб.", "amount": 1599},
    "buy_12month_2config": {"title": "12 месяцев - 2699 руб.", "amount": 2699},
    "buy_7days_3config": {"title": "7 дней - 139 руб.", "amount": 139},
    "buy_1month_3config": {"title": "1 месяц - 499 руб.", "amount": 499},
    "buy_3month_3config": {"title": "3 месяца - 1299 руб.", "amount": 1299},
    "buy_6month_3config": {"title": "6 месяцев - 2299 руб.", "amount": 2299},
    "buy_12month_3config": {"title": "12 месяцев - 3899 руб.", "amount": 3899},
}


PURCHASE_INFO_TEXT = (
    "🔐 flow vpn\n\n"
    "После оплаты с вами свяжется менеджер(убедитесь что у вас есть возможность получать сообщения в Telegram и есть username) и отправит ключ для подключения к Amnezia VPN.\n\n"
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
    "🔐 flow vpn\n\n"
    "Пробный тариф активирован на 3 дня. С вами свяжется менеджер(убедитесь что у вас есть возможность получать сообщения в Telegram и есть username) и отправит ключ для подключения к Amnezia VPN.\n\n"
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


async def how_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [[InlineKeyboardButton("1 устройство 🔧", callback_data="1_config", style="primary")],
                [InlineKeyboardButton("2 устройства 🔧", callback_data="2_config", style="primary")],
                [InlineKeyboardButton("3 устройства 🔧", callback_data="3_config", style="primary")],
                [InlineKeyboardButton("В главное меню 🏠", callback_data="main_menu", style="danger")]]

    await query.edit_message_media(
        media=InputMediaPhoto(
            media=open("photo/flow.png", "rb"),
            caption="<b>Выберите количество устройств</b>\n\nВыберите, сколько устройств нужно подключить к VPN.",
            parse_mode="HTML",
        ),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )



async def buy_1_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    free_trial_used = await has_used_free_trial(user_id)

    keyboard = [
        *([] if free_trial_used else [[InlineKeyboardButton("🎁 3 дня бесплатно", callback_data="buy_free3days_1")]]),
        [InlineKeyboardButton("🗓 7 дней - 59 руб.", callback_data="buy_7days")],
        [InlineKeyboardButton("📅 1 месяц - 199 руб.", callback_data="buy_1month")],
        [InlineKeyboardButton("🧭 3 месяца - 499 руб.", callback_data="buy_3month")],
        [InlineKeyboardButton("🛫 6 месяцев - 899 руб.", callback_data="buy_6month")],
        [InlineKeyboardButton("🏆 12 месяцев - 1499 руб.", callback_data="buy_12month")],
        [InlineKeyboardButton("🏠 В главное меню", callback_data="main_menu")],
    ]

    await query.edit_message_media(
        media=InputMediaPhoto(
            media=open("photo/flow.png", "rb"),
            caption=(
                "<b>Выберите тарифный план</b>\n\n"
                "Ниже собраны все доступные варианты.\n"
                "После выбора вы получите кнопку для оплаты."
            ),
            parse_mode="HTML",
        ),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def buy_2_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    free_trial_used = await has_used_free_trial(user_id)

    keyboard = [
        *([] if free_trial_used else [[InlineKeyboardButton("🎁 3 дня бесплатно", callback_data="buy_free3days_2", style='primary')]]),
        [InlineKeyboardButton("🗓 7 дней - 99 руб.", callback_data="buy_7days_2config", style='success')],
        [InlineKeyboardButton("📅 1 месяц - 349 руб.", callback_data="buy_1month_2config", style='success')],
        [InlineKeyboardButton("🧭 3 месяца - 899 руб.", callback_data="buy_3month_2config", style='success')],
        [InlineKeyboardButton("🛫 6 месяцев - 1599 руб.", callback_data="buy_6month_2config", style='success')],
        [InlineKeyboardButton("🏆 12 месяцев - 2699 руб.", callback_data="buy_12month_2config", style='success')],
        [InlineKeyboardButton("🏠 В главное меню", callback_data="main_menu", style='danger')],
    ]

    await query.edit_message_media(
        media=InputMediaPhoto(
            media=open("photo/flow.png", "rb"),
            caption=(
                "<b>Выберите тарифный план</b>\n\n"
                "Ниже собраны все доступные варианты.\n"
                "После выбора вы получите кнопку для оплаты."
            ),
            parse_mode="HTML",
        ),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def buy_3_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    free_trial_used = await has_used_free_trial(user_id)

    keyboard = [
        *([] if free_trial_used else [[InlineKeyboardButton("🎁 3 дня бесплатно", callback_data="buy_free3days_3", style='primary')]]),
        [InlineKeyboardButton("🗓 7 дней - 139 руб.", callback_data="buy_7days_3config", style='success')],
        [InlineKeyboardButton("📅 1 месяц - 499 руб.", callback_data="buy_1month_3config", style='success')],
        [InlineKeyboardButton("🧭 3 месяца - 1299 руб.", callback_data="buy_3month_3config", style='success')],
        [InlineKeyboardButton("🛫 6 месяцев - 2299 руб.", callback_data="buy_6month_3config", style='success')],
        [InlineKeyboardButton("🏆 12 месяцев - 3899 руб.", callback_data="buy_12month_3config", style='success')],
        [InlineKeyboardButton("🏠 В главное меню", callback_data="main_menu", style='danger')],
    ]

    await query.edit_message_media(
        media=InputMediaPhoto(
            media=open("photo/flow.png", "rb"),
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

    if query.data.startswith("buy_free3days"):
        device_count = 1
        if query.data.endswith("_2"):
            device_count = 2
        elif query.data.endswith("_3"):
            device_count = 3

        activated = await activate_free_trial(user_id, username=username, device_count=device_count)

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
                        f"Устройств: {getattr(paid_user, 'device_count', device_count) or device_count}\n"
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

            if user_id == 8836641281:
                sent_count = context.user_data.get("support_notice_count", 0)
                remaining = max(0, 2 - sent_count)
                if remaining > 0:
                    for _ in range(remaining):
                        await context.bot.send_message(
                            chat_id=user_id,
                            text=(
                                "Здравствуйте, с вами не могут связаться, чтобы подключить вам VPN. "
                                "Напишите в поддержку, пожалуйста."
                            ),
                        )
                    context.user_data["support_notice_count"] = 2
        else:
            await query.edit_message_caption(
                caption=(
                    "⚠️ Пробный тариф уже использован\n\n"
                    "Бесплатный доступ на 3 дня можно активировать только один раз."
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("💳 Выбрать платный тариф", callback_data="buy", style='success')],
                    [InlineKeyboardButton("🏠 В главное меню", callback_data="main_menu", style='danger')],
                ]),
            )
        return

    tariff = TARIFFS[query.data]
    device_count = 1
    if query.data.endswith("_1config"):
        device_count = 1
    elif query.data.endswith("_2config"):
        device_count = 2
    elif query.data.endswith("_3config"):
        device_count = 3

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
                device_count=device_count,
            )
        except Exception as e:
            logger.error("Failed to save payment to DB: %s", e)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Оплатить", url=payment_url, style='success')],
        [InlineKeyboardButton("⬅️ Назад к тарифам", callback_data="buy", style='primary')],
    ])

    await query.edit_message_caption(
        caption=PURCHASE_INFO_TEXT,
        reply_markup=keyboard,
        parse_mode="HTML",
    )