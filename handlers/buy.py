import html
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import ContextTypes

from config.config import ADMIN_ID, WEBHOOK_URL
from db.db import activate_free_trial, get_paid_user, has_used_free_trial, save_payment
from handlers.ui import BRAND, DIVIDER, PHOTO_SHOP, home_button, media, plural
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
    "buy_7days_3config": {"title": "7 дней - 139 руб.", "amount": 139},
    "buy_1month_3config": {"title": "1 месяц - 499 руб.", "amount": 499},
    "buy_3month_3config": {"title": "3 месяца - 1299 руб.", "amount": 1299},
    "buy_6month_3config": {"title": "6 месяцев - 2299 руб.", "amount": 2299},
    "buy_12month_3config": {"title": "12 месяцев - 3899 руб.", "amount": 3899},
    "buy_7days_8config": {"title": "7 дней - 159 руб.", "amount": 159},
    "buy_1month_8config": {"title": "1 месяц - 699 руб.", "amount": 699},
    "buy_3month_8config": {"title": "3 месяца - 1499 руб.", "amount": 1499},
    "buy_6month_8config": {"title": "6 месяцев - 2499 руб.", "amount": 2499},
    "buy_12month_8config": {"title": "12 месяцев - 4199 руб.", "amount": 4199},
}


PLANS = {
    1: {"name": "Start", "icon": "🌒", "trial": "buy_free3days_1", "suffix": ""},
    3: {"name": "Plus", "icon": "🌓", "trial": "buy_free3days_3", "suffix": "_3config"},
    8: {"name": "Family", "icon": "🌕", "trial": "buy_free3days_8", "suffix": "_8config"},
}

# (часть ключа TARIFFS, иконка, подпись, месяцев)
PERIODS = [
    ("7days", "🫧", "7 дней", None),
    ("1month", "🌙", "1 месяц", 1),
    ("3month", "🔭", "3 месяца", 3),
    ("6month", "☄️", "6 месяцев", 6),
    ("12month", "👑", "12 месяцев", 12),
]


def plan_options(device_count: int):
    """Строки тарифной сетки: (ключ TARIFFS, иконка, срок, цена, выгода в %)."""
    plan = PLANS[device_count]
    monthly = TARIFFS[f"buy_1month{plan['suffix']}"]["amount"]
    options = []
    for period, icon, label, months in PERIODS:
        key = f"buy_{period}{plan['suffix']}"
        amount = TARIFFS[key]["amount"]
        saving = 0
        if months and months > 1:
            saving = round((1 - amount / (monthly * months)) * 100)
        options.append((key, icon, label, amount, saving))
    return options


def plan_min_price(device_count: int) -> int:
    return min(amount for _, _, _, amount, _ in plan_options(device_count))


def describe_tariff(key: str):
    """Название плана и срок по ключу TARIFFS (только для красивого текста)."""
    for device_count in PLANS:
        for option_key, _, label, amount, _ in plan_options(device_count):
            if option_key == key:
                return device_count, PLANS[device_count], label, amount
    return None


CONTACT_NOTE = (
    "🔔 <i>Проверьте, что в профиле Telegram указан username "
    "и вам можно написать в личные сообщения.</i>"
)

FREE_TRIAL_INFO_TEXT = (
    f"{BRAND}\n\n"
    "🪄 <b>Пробный период активирован!</b>\n"
    f"{DIVIDER}\n"
    "3 дня GLOW VPN — бесплатно. Приятного пользования 💜\n\n"
    "<b>Что дальше:</b>\n"
    "1️⃣ Менеджер пришлёт персональную ссылку для подключения\n"
    "2️⃣ И видеоинструкцию: как установить приложение, добавить подписку и включить VPN\n\n"
    "🕰 Обычно это занимает 5–15 минут.\n\n"
    f"{CONTACT_NOTE}"
)


def purchase_text(key: str, device_count: int) -> str:
    info = describe_tariff(key)
    if info:
        _, plan, label, amount = info
        tariff_line = f"{plan['icon']} <b>{plan['name']}</b> · {label}"
    else:
        amount = TARIFFS[key]["amount"]
        tariff_line = f"<b>{html.escape(TARIFFS[key]['title'])}</b>"
    return (
        f"{BRAND}\n\n"
        "🧾 <b>Оформление заказа</b>\n"
        f"{DIVIDER}\n"
        f"Тариф: {tariff_line}\n"
        f"Устройств: <b>{device_count}</b>\n"
        f"К оплате: <b>{amount} ₽</b>\n\n"
        "1️⃣ Нажмите «Оплатить» и завершите платёж\n"
        "2️⃣ Бот пришлёт подтверждение, а менеджер — ссылку для подключения "
        "и видеоинструкцию (обычно 5–15 минут)\n\n"
        f"{CONTACT_NOTE}"
    )


async def how_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [
            InlineKeyboardButton(
                f"{plan['icon']} {plan['name']} · {count} {plural(count, 'устройство', 'устройства', 'устройств')} · от {plan_min_price(count)} ₽",
                callback_data=f"{count}_config",
                style="primary",
            )
        ]
        for count, plan in PLANS.items()
    ]
    keyboard.append([home_button()])

    caption = (
        f"{BRAND}\n\n"
        "🛸 <b>Подключение VPN</b>\n"
        f"{DIVIDER}\n"
        "<b>Шаг 1 из 2</b> — сколько устройств подключаем?\n\n"
        "🌒 <b>Start</b> — 1 устройство\n"
        "🌓 <b>Plus</b> — 3 устройства\n"
        "🌕 <b>Family</b> — 8 устройств\n\n"
        "<i>Телефон, ноутбук, планшет, ТВ — каждое считается отдельно.</i>"
    )

    await query.edit_message_media(
        media=media(caption, PHOTO_SHOP),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def _show_plan(update: Update, device_count: int):
    query = update.callback_query
    await query.answer()

    plan = PLANS[device_count]
    free_trial_used = await has_used_free_trial(update.effective_user.id)

    keyboard = []
    if not free_trial_used:
        keyboard.append([
            InlineKeyboardButton("🪄 Попробовать 3 дня бесплатно", callback_data=plan["trial"], style="primary")
        ])
    for key, icon, label, amount, saving in plan_options(device_count):
        text = f"{icon} {label} · {amount} ₽"
        if saving > 0:
            text += f" · −{saving}%"
        keyboard.append([InlineKeyboardButton(text, callback_data=key, style="success")])
    keyboard.append([
        InlineKeyboardButton("⟵ Назад", callback_data="buy", style="primary"),
        home_button("🌌 Меню"),
    ])

    caption = (
        f"{BRAND}\n\n"
        f"{plan['icon']} <b>{plan['name']}</b> · {device_count} "
        f"{plural(device_count, 'устройство', 'устройства', 'устройств')}\n"
        f"{DIVIDER}\n"
        "<b>Шаг 2 из 2</b> — выберите срок подписки.\n"
        "Чем дольше срок, тем ниже цена за месяц 💜\n\n"
    )
    if not free_trial_used:
        caption += "🪄 Не уверены? Сначала попробуйте 3 дня бесплатно.\n\n"
    caption += "<i>После выбора появится кнопка оплаты.</i>"

    await query.edit_message_media(
        media=media(caption, PHOTO_SHOP),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def buy_1_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _show_plan(update, 1)


async def buy_3_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _show_plan(update, 3)


async def buy_8_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _show_plan(update, 8)


async def buy_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    username = update.effective_user.username

    if query.data.startswith("buy_free3days"):
        device_count = 1
        if query.data.endswith("_3"):
            device_count = 3
        elif query.data.endswith("_8"):
            device_count = 8

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
                    [
                        InlineKeyboardButton(
                            "🔮 Личный кабинет",
                            web_app=WebAppInfo(url=f"{WEBHOOK_URL}/cabinet?tg_id={user_id}"),
                            style="primary",
                        )
                    ],
                    [home_button()],
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
                    f"{BRAND}\n\n"
                    "🕯 <b>Пробный период уже использован</b>\n"
                    f"{DIVIDER}\n"
                    "Бесплатные 3 дня можно активировать только один раз.\n\n"
                    "Выберите тариф — от 59 ₽, а на длинных сроках выгода до 50% 💜"
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🛸 Выбрать тариф", callback_data="buy", style="success")],
                    [home_button()],
                ]),
                parse_mode="HTML",
            )
        return

    tariff = TARIFFS[query.data]
    device_count = 1
    if query.data.endswith("_3config"):
        device_count = 3
    elif query.data.endswith("_8config"):
        device_count = 8

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
        [InlineKeyboardButton(f"🪙 Оплатить {tariff['amount']} ₽", url=payment_url, style='success')],
        [InlineKeyboardButton("⟵ Назад к тарифам", callback_data="buy", style='primary')],
    ])

    await query.edit_message_caption(
        caption=purchase_text(query.data, device_count),
        reply_markup=keyboard,
        parse_mode="HTML",
    )