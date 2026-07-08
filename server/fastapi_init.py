from fastapi import FastAPI
from contextlib import asynccontextmanager

from telegram import Update

from bot_init import create_aplication
from server.routes.telegram_routes import router as telegram_router
from server.routes.payment_routes import router as payment_router

from config.config import WEBHOOK_URL, TELEGRAM_WEBHOOK_PATH, SECRET_TOKEN



@asynccontextmanager
async def lifespan(app: FastAPI):
    application = await create_aplication()

    app.state.bot_app = application

    await application.initialize()
    await application.start()
    await application.bot.set_webhook(
        url=WEBHOOK_URL + TELEGRAM_WEBHOOK_PATH,
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
        secret_token=SECRET_TOKEN,
    )

    yield
    # что будет происходить при выходе
    try:
        await application.bot.delete_webhook()
    finally:
        await application.stop()
        await application.shutdown()



def init_fastapi_app():
    app = FastAPI(lifespan=lifespan)

    app.include_router(telegram_router)
    app.include_router(payment_router, prefix='/cp')

    return app