from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes


PRIVACY_POLICY_URL = "https://telegra.ph/Politika-konfidencialnosti-06-21-31"
USER_AGREEMENT_URL = "https://telegra.ph/Polzovatelskoe-soglashenie-04-01-19"


async def legal_docs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("политика конфиденциальности", url=PRIVACY_POLICY_URL)],
        [InlineKeyboardButton("пользовательское соглашение", url=USER_AGREEMENT_URL)],
        [InlineKeyboardButton("в главное меню", callback_data="main_menu")],
    ]
    markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            "Юридическая информация:\n\n"
            "1. Политика конфиденциальности\n"
            "2. Пользовательское соглашение\n\n"
            "Откройте нужный документ по кнопке ниже."
        ),
        reply_markup=markup,
    )


async def support_contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("написать в поддержку", url="https://t.me/i1i1i1iij")],
        [InlineKeyboardButton("в главное меню", callback_data="main_menu")],
    ]
    markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            "Контакты поддержки для обратной связи:\n\n"
            "Telegram: @i1i1i1iij\n"
            "Формат связи: личные обращения (тикеты) в Telegram, не группа."
        ),
        reply_markup=markup,
    )


async def tariffs_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("приобрести", callback_data="buy")],
        [InlineKeyboardButton("в главное меню", callback_data="main_menu")],
    ]
    markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            "Тарифы и цены:\n\n"
            "7 дней - 59 руб.\n"
            "1 месяц - 199 руб.\n"
            "3 месяца - 499 руб.\n"
            "6 месяцев - 899 руб.\n"
            "12 месяцев - 1499 руб.\n\n"
            "За что платит клиент:\n"
            "- доступ к VPN-сервису на оплаченный срок;\n"
            "- доступ к защищенному соединению;\n"
            "- сопровождение по подключению через поддержку."
        ),
        reply_markup=markup,
    )