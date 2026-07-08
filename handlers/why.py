from telegram.ext import ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto


async def why_vpn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [[InlineKeyboardButton("💳 Приобрести", callback_data="buy")],
                [InlineKeyboardButton("🏠 В главное меню", callback_data="main_menu")]]
    markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_media(
        media=InputMediaPhoto(
            media=open("photo/chill.jpg", "rb"),
            caption=(
                "<b>Почему стоит выбрать именно наш VPN?</b>\n\n"
                "1. Высокая скорость и стабильное соединение.\n"
                "2. Современное шифрование для защиты данных.\n"
                "3. Удобное подключение с разных устройств.\n\n"
                "Нажмите кнопку ниже, чтобы перейти к покупке."
            ),
            parse_mode="HTML",
        ),
        reply_markup=markup,
    )