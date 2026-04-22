from telegram.ext import ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup


async def why_vpn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [[InlineKeyboardButton("приобрести", callback_data="buy")],
                [InlineKeyboardButton("в главное меню", callback_data="main_menu")]]
    markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_video(
        chat_id=update.effective_chat.id,
        video=open("photo/work_vpn.MP4", "rb"),
        caption="Почему стоит выбрать именно наш VPN?\n\n"
                "1. Высокая скорость и стабильность соединения.\n"
                "2. Современные технологии шифрования для защиты ваших данных.\n"
                "3. Доступ к заблокированным ресурсам и контенту.\n"
                "4. Удобное приложение для всех устройств.\n\n"
                "Выбирайте наш VPN и наслаждайтесь безопасным и свободным интернетом!",
        reply_markup=markup,
    )