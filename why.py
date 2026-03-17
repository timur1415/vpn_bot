from telegram.ext import ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup


async def why_vpn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [[InlineKeyboardButton("приобрести", callback_data="buy")],
                [InlineKeyboardButton("в главное меню", callback_data="main_menu")]]
    markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Почему этот VPN?\n\n"
        "1. Высокая скорость для видео и игр\n\n"
        "2. Безопасность и шифрование\n\n"
        "3. Доступ к заблокированным ресурсам\n\n"
        "4. Поддержка всех платформ (Windows, macOS, iOS, Android)\n\n"
        "5. Отличная поддержка клиентов",
        reply_markup=markup
    )
