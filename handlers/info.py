from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InputMediaPhoto
from telegram.ext import ContextTypes


PRIVACY_POLICY_URL = "https://telegra.ph/Politika-konfidencialnosti-09-30-168"
USER_AGREEMENT_URL = "https://telegra.ph/Polzovatelskoe-soglashenie-09-30-50"
SUPPORT_USERNAME = "@i1i1i1iij"
SUPPORT_URL = f"https://t.me/{SUPPORT_USERNAME.replace('@', '')}"


async def legal_docs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("🔐 Политика конфиденциальности", url=PRIVACY_POLICY_URL, style='primary')],
        [InlineKeyboardButton("📝 Пользовательское соглашение", url=USER_AGREEMENT_URL, style='primary')],
        [InlineKeyboardButton("🏠 В главное меню", callback_data="main_menu", style='danger')],
    ]
    markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_media(
        media=InputMediaPhoto(
            media=open("photo/flow.png", "rb"),
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
        [InlineKeyboardButton("💬 Написать в поддержку", url=SUPPORT_URL, style='primary')],
        [InlineKeyboardButton("🏠 В главное меню", callback_data="main_menu", style='danger')],
    ]
    markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_media(
        media=InputMediaPhoto(
            media=open("photo/flow.png", "rb"),
            caption=(
                "<b>Поддержка</b>\n\n"
                f"Telegram: {SUPPORT_USERNAME}\n"
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
        [InlineKeyboardButton("💳 Приобрести", callback_data="buy", style='success')],
        [InlineKeyboardButton("🏠 В главное меню", callback_data="main_menu", style='danger')],
    ]
    markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_media(
        media=InputMediaPhoto(
            media=open("photo/flow.png", "rb"),
            caption=(
                "💎 *Тарифы и цены*\n\n"
                "🎁 *Пробный период* — 3 дня бесплатно\n"
                "_\\(один раз на пользователя\\)_\n\n"
                "📱 *start*\n"
                ">🗓 7 дней — *59 ₽*\n"
                ">📅 1 месяц — *199 ₽*\n"
                ">🧭 3 месяца — *499 ₽*\n"
                ">🛫 6 месяцев — *899 ₽*\n"
                ">🏆 12 месяцев — *1499 ₽*\n\n"
                "📱📱📱 *plus*\n"
                ">🗓 7 дней — *139 ₽*\n"
                ">📅 1 месяц — *499 ₽*\n"
                ">🧭 3 месяца — *1299 ₽*\n"
                ">🛫 6 месяцев — *2299 ₽*\n"
                ">🏆 12 месяцев — *3899 ₽*\n\n"
                "📱📱📱📱📱📱📱📱 *Family*\n"
                ">🗓 7 дней — *159 ₽*\n"
                ">📅 1 месяц — *699 ₽*\n"
                ">🧭 3 месяца — *1499 ₽*\n"
                ">🛫 6 месяцев — *2499 ₽*\n"
                ">🏆 12 месяцев — *4199 ₽*\n\n"
                "✅ Оплата дает доступ к VPN на выбранный срок и поддержку по подключению\\."
            ),
            parse_mode="MarkdownV2",
        ),
        reply_markup=markup,
    )