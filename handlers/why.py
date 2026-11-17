from telegram import InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from handlers.ui import BRAND, DIVIDER, buy_button, home_button, media


async def why_vpn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [[buy_button()], [home_button()]]

    caption = (
        f"{BRAND}\n\n"
        "✨ <b>Почему GLOW VPN</b>\n"
        f"{DIVIDER}\n"
        "⚡ <b>Скорость</b>\n"
        "Видео, игры и соцсети работают без тормозов.\n\n"
        "🔒 <b>Защита</b>\n"
        "Современное шифрование трафика — ваши данные остаются вашими.\n\n"
        "📱 <b>Все устройства</b>\n"
        "Телефон, ноутбук, планшет, ТВ — до 8 устройств в одной подписке.\n\n"
        "🎥 <b>Простое подключение</b>\n"
        "Персональная ссылка и видеоинструкция — настройка за пару минут.\n\n"
        "💬 <b>Живая поддержка</b>\n"
        "Отвечают люди, а не боты. Поможем, если что-то не получается.\n\n"
        "🎁 Начните с <b>3 бесплатных дней</b> 👇"
    )

    await query.edit_message_media(media=media(caption), reply_markup=InlineKeyboardMarkup(keyboard))
