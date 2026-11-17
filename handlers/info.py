from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from handlers.buy import PLANS, plan_options
from handlers.ui import (
    BRAND,
    DIVIDER,
    PHOTO_SHOP,
    SUPPORT_URL,
    SUPPORT_USERNAME,
    buy_button,
    home_button,
    media,
    plural,
)


PRIVACY_POLICY_URL = "https://telegra.ph/Politika-konfidencialnosti-09-30-168"
USER_AGREEMENT_URL = "https://telegra.ph/Polzovatelskoe-soglashenie-09-30-50"


async def legal_docs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("🔐 Политика конфиденциальности", url=PRIVACY_POLICY_URL, style="primary")],
        [InlineKeyboardButton("📝 Пользовательское соглашение", url=USER_AGREEMENT_URL, style="primary")],
        [home_button()],
    ]

    caption = (
        f"{BRAND}\n\n"
        "📄 <b>Документы</b>\n"
        f"{DIVIDER}\n"
        "Мы бережно относимся к вашим данным и честно описываем условия работы сервиса.\n\n"
        "Откройте нужный документ кнопкой ниже 👇"
    )

    await query.edit_message_media(media=media(caption), reply_markup=InlineKeyboardMarkup(keyboard))


async def support_contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("💬 Написать в поддержку", url=SUPPORT_URL, style="success")],
        [home_button()],
    ]

    caption = (
        f"{BRAND}\n\n"
        "💬 <b>Поддержка</b>\n"
        f"{DIVIDER}\n"
        "Поможем с подключением, оплатой и любыми вопросами по VPN.\n\n"
        f"👤 Telegram: {SUPPORT_USERNAME}\n\n"
        "<i>Чтобы мы ответили быстрее, опишите проблему и укажите устройство "
        "(iPhone, Android, Windows, macOS, ТВ).</i>"
    )

    await query.edit_message_media(media=media(caption), reply_markup=InlineKeyboardMarkup(keyboard))


def _tariffs_caption() -> str:
    blocks = []
    for count, plan in PLANS.items():
        lines = []
        for _, icon, label, amount, saving in plan_options(count):
            line = f"{icon} {label} — <b>{amount} ₽</b>"
            if saving > 0:
                line += f" <i>−{saving}%</i>"
            lines.append(line)
        devices = f"{count} {plural(count, 'устройство', 'устройства', 'устройств')}"
        blocks.append(
            f"{plan['icon']} <b>{plan['name']}</b> · {devices}\n"
            f"<blockquote>{chr(10).join(lines)}</blockquote>"
        )

    return (
        f"{BRAND}\n\n"
        "💎 <b>Тарифы и цены</b>\n"
        "🎁 Пробный период — <b>3 дня бесплатно</b> <i>(один раз)</i>\n\n"
        + "\n".join(blocks)
        + "\n✅ Доступ к VPN на весь срок и помощь с подключением."
    )


async def tariffs_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [buy_button()],
        [home_button()],
    ]

    await query.edit_message_media(
        media=media(_tariffs_caption(), PHOTO_SHOP),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
