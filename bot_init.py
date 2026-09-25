import logging

from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    PicklePersistence,
    filters,
)

from config.config import TOKEN
from config.states import MAIN_MENU, REVIEWS
from handlers.buy import (
    buy_1_config,
    buy_2_config,
    buy_3_config,
    buy_callback,
    how_config,
)
from handlers.info import legal_docs, support_contacts, tariffs_info
from handlers.start import start
from handlers.why import why_vpn
from reviews.reviews import finish_review, leave_review, reviews_handler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def create_aplication():
    persistence = PicklePersistence(filepath="vpn_bot")
    application = ApplicationBuilder().token(TOKEN).persistence(persistence).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAIN_MENU: [
                CallbackQueryHandler(how_config, pattern="^buy$"),
                CallbackQueryHandler(buy_1_config, pattern="^1_config$"),
                CallbackQueryHandler(buy_2_config, pattern="^2_config$"),
                CallbackQueryHandler(buy_3_config, pattern="^3_config$"),
                CallbackQueryHandler(buy_callback, pattern="^buy_"),
                CallbackQueryHandler(tariffs_info, pattern="^tariffs$"),
                CallbackQueryHandler(why_vpn, pattern="^why_vpn$"),
                CallbackQueryHandler(reviews_handler, pattern="^reviews$"),
                CallbackQueryHandler(legal_docs, pattern="^legal_docs$"),
                CallbackQueryHandler(support_contacts, pattern="^support$"),
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
    return application

