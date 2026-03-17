from telegram.ext import ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

from config.states import REVIEWS

async def reviews_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [[InlineKeyboardButton('посмотреть отзывы', url='https://t.me/+WUxKV7A4n601MTVi')],
                [InlineKeyboardButton('оставить отзыв', callback_data='leave_review')],
                [InlineKeyboardButton('в главное меню', callback_data='main_menu')]]
    
    markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="выбери действие:",
        reply_markup=markup
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
    context.user_data['review'] = update.message.text
    keyboard = [[InlineKeyboardButton('главное меню', callback_data='main_menu')]]
    markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_message(
        chat_id= -1003705854359,
        text=f"Новый отзыв от {update.effective_user.first_name}: {context.user_data['review']}",
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Спасибо за ваш отзыв! Мы ценим ваше мнение и будем работать над улучшением нашего сервиса.",
        reply_markup=markup
    )

