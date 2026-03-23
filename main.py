import logging
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackQueryHandler,
    PicklePersistence,
)

from config.config import TOKEN

from config.states import MAIN_MENU, REVIEWS

from reviews.reviews import finish_review, reviews_handler
from start import start

from why import why_vpn

from buy import buy, buy_callback

from reviews.reviews import leave_review

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    persistence = PicklePersistence(filepath="vpn_bot")
    application = ApplicationBuilder().token(TOKEN).persistence(persistence).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAIN_MENU: [
                CallbackQueryHandler(buy, pattern="^buy$"),
                CallbackQueryHandler(buy_callback, pattern="^buy_"),
                CallbackQueryHandler(why_vpn, pattern="^why_vpn$"),
                CallbackQueryHandler(reviews_handler, pattern="^reviews$"),
                CallbackQueryHandler(start, pattern="^support$"),
                CallbackQueryHandler(start, pattern="^main_menu$"),
                CallbackQueryHandler(leave_review, pattern="^leave_review$"),
            ],
            REVIEWS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, finish_review),
                CallbackQueryHandler(start, pattern="^main_menu$"),
            ]
        },
        fallbacks=[CommandHandler("start", start)],
        name="vpn_bot",
        persistent=True,
    )

    application.add_handler(conv_handler)

    application.run_polling()