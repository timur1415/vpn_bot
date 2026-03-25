from telegram.ext import ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

from config.states import MAIN_MENU


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("приобрести", callback_data="buy")],
        [InlineKeyboardButton("почему именно этот впн?", callback_data="why_vpn")],
        [InlineKeyboardButton("отзывы", callback_data="reviews")],
        [InlineKeyboardButton("поддержка", url="https://t.me/i1i1i1iij")],
    ]
    markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=open("photo/welcome.jpg", "rb"),
            caption="Приветствую! Я бот для продажи VPN. Выберите интересующий вас пункт:",
            reply_markup=markup,
        )
    else:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=open("photo/welcome.jpg", "rb"),
            caption="Приветствую! Я бот для продажи VPN. Выберите интересующий вас пункт:",
            reply_markup=markup,
        )
    return MAIN_MENU
