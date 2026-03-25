from telegram.ext import ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

from config.states import REVIEWS

from config.config import REVIEW


async def reviews_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [
            InlineKeyboardButton(
                "посмотреть отзывы", url="https://t.me/+WUxKV7A4n601MTVi"
            )
        ],
        [InlineKeyboardButton("оставить отзыв", callback_data="leave_review")],
        [InlineKeyboardButton("в главное меню", callback_data="main_menu")],
    ]

    markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=open("photo/reviews.jpg", "rb"),
        caption="Отзывы наших клиентов говорят сами за себя! Присоединяйтесь к числу довольных пользователей нашего VPN и оставьте свой отзыв, чтобы помочь нам стать еще лучше!",
        reply_markup=markup,
    )


async def leave_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Пожалуйста, напишите свой отзыв о нашем VPN. Мы ценим ваше мнение!",
    )
    return REVIEWS


async def finish_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["review"] = update.message.text
    keyboard = [[InlineKeyboardButton("главное меню", callback_data="main_menu")]]
    markup = InlineKeyboardMarkup(keyboard)
    try:
        await context.bot.send_message(
            chat_id=REVIEW,
            text=f"Новый отзыв от {update.effective_user.first_name}: {context.user_data['review']}",
        )

        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=open("photo/chil.jpg", "rb"),
            caption="Спасибо за ваш отзыв! Мы ценим ваше мнение и будем работать над улучшением нашего сервиса.",
            reply_markup=markup,
        )
    except Exception as e:
        print(f"Error sending review to admin: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Произошла ошибка при отправке вашего отзыва. Пожалуйста, попробуйте позже.",
            reply_markup=markup,
        )
