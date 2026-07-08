from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InputMediaPhoto
from telegram.ext import ContextTypes


PRIVACY_POLICY_URL = "https://telegra.ph/Politika-konfidencialnosti-06-21-31"
USER_AGREEMENT_URL = "https://telegra.ph/Polzovatelskoe-soglashenie-04-01-19"


async def legal_docs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("🔐 Политика конфиденциальности", url=PRIVACY_POLICY_URL)],
        [InlineKeyboardButton("📝 Пользовательское соглашение", url=USER_AGREEMENT_URL)],
        [InlineKeyboardButton("🏠 В главное меню", callback_data="main_menu")],
    ]
    markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_media(
        media=InputMediaPhoto(
            media=open("photo/chill.jpg", "rb"),
            caption=(
                "<b>Юридическая информация</b>\n\n"
                "• Политика конфиденциальности\n"
                "• Пользовательское соглашение\n\n"
                "Откройте нужный документ по кнопке ниже."
            ),
            parse_mode="HTML",
        ),
        reply_markup=markup,
    )


async def support_contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("💬 Написать в поддержку", url="https://t.me/i1i1i1iij")],
        [InlineKeyboardButton("🏠 В главное меню", callback_data="main_menu")],
    ]
    markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_media(
        media=InputMediaPhoto(
            media=open("photo/chill.jpg", "rb"),
            caption=(
                "<b>Поддержка</b>\n\n"
                "Telegram: @i1i1i1iij\n"
                "Формат связи: личные обращения в Telegram."
            ),
            parse_mode="HTML",
        ),
        reply_markup=markup,
    )


async def tariffs_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("💳 Приобрести", callback_data="buy")],
        [InlineKeyboardButton("🏠 В главное меню", callback_data="main_menu")],
    ]
    markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_media(
        media=InputMediaPhoto(
            media=open("photo/chill.jpg", "rb"),
            caption=(
                "<b>Тарифы и цены</b>\n\n"
                "• 7 дней - 59 руб.\n"
                "• 1 месяц - 199 руб.\n"
                "• 3 месяца - 499 руб.\n"
                "• 6 месяцев - 899 руб.\n"
                "• 12 месяцев - 1499 руб.\n\n"
                "Оплата дает доступ к VPN на выбранный срок и поддержку по подключению."
            ),
            parse_mode="HTML",
        ),
        reply_markup=markup,
    )