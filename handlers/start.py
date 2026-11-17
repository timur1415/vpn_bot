import html

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
    WebAppInfo,
)
from telegram.ext import ContextTypes

from config.config import ADMIN_ID, WEBHOOK_URL
from config.states import MAIN_MENU
from db.db import has_used_free_trial, register_bot_visit
from handlers.ui import BRAND, DIVIDER, buy_button, media, photo


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user:
        await register_bot_visit(
            telegram_id=update.effective_user.id,
            username=update.effective_user.username,
            first_name=update.effective_user.first_name,
        )

    first_name = html.escape(update.effective_user.first_name or "друг")
    trial_used = await has_used_free_trial(update.effective_user.id)

    keyboard = [
        [
            InlineKeyboardButton(
                "🌙 Личный кабинет",
                web_app=WebAppInfo(
                    url=f"{WEBHOOK_URL}/cabinet?tg_id={update.effective_user.id}"
                ),
                style="primary",
            )
        ],
        [buy_button("🎁 Попробовать бесплатно" if not trial_used else "⚡ Подключить VPN")],
        [
            InlineKeyboardButton("💎 Тарифы", callback_data="tariffs", style="primary"),
            InlineKeyboardButton("✨ Почему GLOW", callback_data="why_vpn", style="primary"),
        ],
        [
            InlineKeyboardButton("⭐ Отзывы", callback_data="reviews", style="primary"),
            InlineKeyboardButton("📄 Документы", callback_data="legal_docs", style="primary"),
        ],
        [InlineKeyboardButton("💬 Поддержка", callback_data="support", style="primary")],
    ]

    if update.effective_user and update.effective_user.id == ADMIN_ID:
        keyboard.insert(
            0,
            [
                InlineKeyboardButton(
                    "🛠 Админ-панель",
                    web_app=WebAppInfo(url=f"{WEBHOOK_URL}/admin?tg_id={ADMIN_ID}"),
                    style="danger",
                )
            ],
        )
    markup = InlineKeyboardMarkup(keyboard)

    caption = (
        f"{BRAND}\n\n"
        f"Привет, <b>{first_name}</b>! 👋\n"
        "Быстрый и стабильный VPN — без рекламы и сложных настроек.\n"
        f"{DIVIDER}\n"
        "⚡ Высокая скорость\n"
        "🔒 Современное шифрование\n"
        "📱 До 8 устройств в одной подписке\n"
        "💬 Живая поддержка и помощь с подключением\n"
    )
    if not trial_used:
        caption += "\n🎁 <b>3 дня бесплатно</b> — попробуйте прямо сейчас."
    else:
        caption += "\n🌙 Подписка и платежи — в <b>Личном кабинете</b>."

    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_media(media=media(caption), reply_markup=markup)
    else:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=photo(),
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
