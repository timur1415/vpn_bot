from telegram.ext import ContextTypes
import html
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

from config.states import MAIN_MENU, REVIEWS

from config.config import REVIEW
from handlers.ui import BRAND, DIVIDER, home_button, media, photo

logger = logging.getLogger(__name__)

THANKS_TEXT = (
    f"{BRAND}\n\n"
    "💜 <b>Спасибо за отзыв!</b>\n"
    f"{DIVIDER}\n"
    "Мы читаем каждый отзыв — он помогает делать GLOW VPN лучше."
)


async def reviews_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [
            InlineKeyboardButton(
                "👀 Посмотреть отзывы", url="https://t.me/+WUxKV7A4n601MTVi", style='primary'
            )
        ],
        [InlineKeyboardButton("✍️ Оставить отзыв", callback_data="leave_review", style='success')],
        [home_button()],
    ]

    caption = (
        f"{BRAND}\n\n"
        "⭐ <b>Отзывы</b>\n"
        f"{DIVIDER}\n"
        "Почитайте, что говорят наши пользователи, или поделитесь своим впечатлением.\n\n"
        "<i>Каждый отзыв помогает нам делать сервис лучше 💜</i>"
    )

    await query.edit_message_media(media=media(caption), reply_markup=InlineKeyboardMarkup(keyboard))


async def leave_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data["review_message_id"] = query.message.message_id
    context.user_data["review_chat_id"] = update.effective_chat.id

    caption = (
        f"{BRAND}\n\n"
        "✍️ <b>Ваш отзыв</b>\n"
        f"{DIVIDER}\n"
        "Напишите отзыв <b>одним сообщением</b> прямо в этот чат.\n"
        "Что понравилось, что можно улучшить — нам важно всё."
    )

    await query.edit_message_media(
        media=media(caption),
        reply_markup=InlineKeyboardMarkup([[home_button("✖️ Отмена")]]),
    )
    return REVIEWS


async def finish_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["review"] = update.message.text
    markup = InlineKeyboardMarkup([[home_button()]])
    user = update.effective_user
    author = html.escape(user.first_name or "Без имени")
    if user.username:
        author += f" (@{html.escape(user.username)})"
    try:
        await context.bot.send_message(
            chat_id=REVIEW,
            text=(
                "⭐ <b>Новый отзыв</b>\n"
                f"От: {author} · ID <code>{user.id}</code>\n\n"
                f"{html.escape(context.user_data['review'])}"
            ),
            parse_mode="HTML",
        )

        chat_id = context.user_data.get("review_chat_id", update.effective_chat.id)
        message_id = context.user_data.get("review_message_id")
        if message_id:
            await context.bot.edit_message_media(
                chat_id=chat_id,
                message_id=message_id,
                media=media(THANKS_TEXT),
                reply_markup=markup,
            )
        else:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=photo(),
                caption=THANKS_TEXT,
                reply_markup=markup,
                parse_mode="HTML",
            )
    except Exception as e:
        logger.error("Error sending review to admin: %s", e)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="😔 Не получилось отправить отзыв. Попробуйте ещё раз чуть позже.",
            reply_markup=markup,
        )
    return MAIN_MENU
