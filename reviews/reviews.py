from telegram.ext import ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto

from config.states import MAIN_MENU, REVIEWS

from config.config import REVIEW


async def reviews_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [
            InlineKeyboardButton(
                "👀 Посмотреть отзывы", url="https://t.me/+WUxKV7A4n601MTVi"
            )
        ],
        [InlineKeyboardButton("✍️ Оставить отзыв", callback_data="leave_review")],
        [InlineKeyboardButton("🏠 В главное меню", callback_data="main_menu")],
    ]

    markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_media(
        media=InputMediaPhoto(
            media=open("photo/chill.jpg", "rb"),
            caption=(
                "<b>Отзывы наших клиентов</b>\n\n"
                "Присоединяйтесь к числу довольных пользователей и оставьте свой отзыв.\n"
                "Это помогает нам делать сервис лучше."
            ),
            parse_mode="HTML",
        ),
        reply_markup=markup,
    )


async def leave_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data["review_message_id"] = query.message.message_id
    context.user_data["review_chat_id"] = update.effective_chat.id

    await query.edit_message_media(
        media=InputMediaPhoto(
            media=open("photo/chill.jpg", "rb"),
            caption=(
                "<b>Оставить отзыв</b>\n\n"
                "Напишите свой отзыв одним сообщением.\n"
                "После отправки я сразу покажу подтверждение здесь же."
            ),
            parse_mode="HTML",
        ),
    )
    return REVIEWS


async def finish_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["review"] = update.message.text
    keyboard = [[InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]
    markup = InlineKeyboardMarkup(keyboard)
    try:
        await context.bot.send_message(
            chat_id=REVIEW,
            text=f"Новый отзыв от {update.effective_user.first_name}: {context.user_data['review']}",
        )

        chat_id = context.user_data.get("review_chat_id", update.effective_chat.id)
        message_id = context.user_data.get("review_message_id")
        if message_id:
            await context.bot.edit_message_media(
                chat_id=chat_id,
                message_id=message_id,
                media=InputMediaPhoto(
                    media=open("photo/chill.jpg", "rb"),
                    caption=(
                        "<b>Спасибо за ваш отзыв!</b>\n\n"
                        "Мы ценим ваше мнение и будем работать над улучшением сервиса."
                    ),
                    parse_mode="HTML",
                ),
                reply_markup=markup,
            )
        else:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=open("photo/chill.jpg", "rb"),
                caption=(
                    "<b>Спасибо за ваш отзыв!</b>\n\n"
                    "Мы ценим ваше мнение и будем работать над улучшением сервиса."
                ),
                reply_markup=markup,
                parse_mode="HTML",
            )
    except Exception as e:
        print(f"Error sending review to admin: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Произошла ошибка при отправке вашего отзыва. Пожалуйста, попробуйте позже.",
            reply_markup=markup,
        )
    return MAIN_MENU
