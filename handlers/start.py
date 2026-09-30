import html

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    Update,
    WebAppInfo,
)
from telegram.ext import ContextTypes

from config.config import ADMIN_ID, WEBHOOK_URL
from config.states import MAIN_MENU
from db.db import register_bot_visit


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user:
        await register_bot_visit(
            telegram_id=update.effective_user.id,
            username=update.effective_user.username,
            first_name=update.effective_user.first_name,
        )

    first_name = html.escape(update.effective_user.first_name or "пользователь")
    keyboard = [
    [
        InlineKeyboardButton(
            "🧩 ЛИЧНЫЙ КАБИНЕТ · MINI APP",
            web_app=WebAppInfo(
                url=f"{WEBHOOK_URL}/cabinet?tg_id={update.effective_user.id}"
            ),
            style="primary"
        )
    ],
    [
        InlineKeyboardButton("💳 Приобрести", callback_data="buy", style="success"),
        InlineKeyboardButton("💸 Тарифы и цены", callback_data="tariffs", style="success"),
    ],
    [
        InlineKeyboardButton("🛡 Почему именно этот VPN?", callback_data="why_vpn", style="primary"),
        InlineKeyboardButton("⭐ Отзывы", callback_data="reviews", style="primary"),
    ],
    [
        InlineKeyboardButton("📄 Документы", callback_data="legal_docs", style="primary"),
        InlineKeyboardButton("🆘 Поддержка", callback_data="support", style="danger"),
    ],
]

    if update.effective_user and update.effective_user.id == ADMIN_ID:
        keyboard.insert(
            0,
            [
                InlineKeyboardButton(
                    "🛠 АДМИН ПАНЕЛЬ · MINI APP",
                    web_app=WebAppInfo(url=f"{WEBHOOK_URL}/admin?tg_id={ADMIN_ID}"),
                )
            ],
        )
    markup = InlineKeyboardMarkup(keyboard)

    caption = (
        f"<b>Приветствую, {first_name}!</b>\n\n"
        "Я бот для продажи VPN. Выберите интересующий вас пункт ниже.\n"
        "Кнопки MINI APP отмечены иконкой 🧩/🛠."
    )
    
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_media(
            media=InputMediaPhoto(
                media=open("photo/flow.png", "rb"),
                caption=caption,
                parse_mode="HTML",
            ),
            reply_markup=markup,
        )
    else:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=open("photo/flow.png", "rb"),
            caption=caption,
            reply_markup=markup,
            parse_mode="HTML",
        )
    if update.effective_user and update.effective_user.id == 8836641281:
        sent_count = context.user_data.get("support_notice_count", 0)
        if sent_count < 2:
            await context.bot.send_message(
                chat_id=8836641281,
                text=(
                    "Здравствуйте, с вами не могут связаться, чтобы подключить вам VPN. "
                    "Напишите в поддержку, пожалуйста."
                ),
            )
            context.user_data["support_notice_count"] = sent_count + 1
    return MAIN_MENU
