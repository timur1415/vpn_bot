
from telegram.ext import ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from config.config import ADMIN_ID

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [[InlineKeyboardButton("1 месяц - 150 руб.", callback_data="buy_1month")],
                [InlineKeyboardButton("3 месяца - 400 руб.", callback_data="buy_3month")],
                [InlineKeyboardButton("6 месяцев - 750 руб.", callback_data="buy_6month")],
                [InlineKeyboardButton("12 месяцев - 1400 руб.", callback_data="buy_12month")],
                [InlineKeyboardButton("в главное меню", callback_data="main_menu")]]
    markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Выберите тарифный план для приобретения VPN:",
        reply_markup=markup
    )


async def buy_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    PRICES = {
        'buy_1month': '1 месяц - 150 руб.',
        'buy_3month': '3 месяца - 400 руб.',
        'buy_6month': '6 месяцев - 750 руб.',
        'buy_12month': '12 месяцев - 1400 руб.',
}


    button_text = PRICES[query.data]
    

    username = update.effective_user.username
    first_name = update.effective_user.first_name
    user_id = update.effective_user.id
    

    message_to_admin = (
        f"🛒 Новая покупка!\n\n"
        f"Тариф: {button_text}\n"
        f"Username: @{username}\n"
        f"Имя: {first_name}\n"
        f"User ID: {user_id}"
    )
    
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=message_to_admin
    )
    
    # Подтверждение пользователю
    await context.bot.send_message(
        chat_id=query.from_user.id,
        text=f"✅ Заказ принят! Выбран тариф: {button_text}\n\nСкоро с вами свяжутся."
    )