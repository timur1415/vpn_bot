from fastapi import FastAPI
from contextlib import asynccontextmanager
from datetime import datetime
import asyncio
import logging

from telegram import Update

from bot_init import create_aplication
from server.routes.admin_routes import router as admin_router
from server.routes.cabinet_routes import router as cabinet_router
from server.routes.telegram_routes import router as telegram_router
from server.routes.payment_routes import router as payment_router

from config.config import WEBHOOK_URL, TELEGRAM_WEBHOOK_PATH, SECRET_TOKEN, ADMIN_ID

from db.db import init_db, list_paid_users, mark_paid_user_warning, mark_paid_user_expired, save_payment
from server.payment_client import create_payment

logger = logging.getLogger(__name__)
def _tariff_amount(tariff: str) -> int | None:
    tariff_lower = tariff.lower()
    if "7 дней" in tariff_lower:
        return 59
    if "1 месяц" in tariff_lower:
        return 199
    if "3 месяца" in tariff_lower:
        return 499
    if "6 месяцев" in tariff_lower:
        return 899
    if "12 месяцев" in tariff_lower:
        return 1499
    return None


async def _send_subscription_reminders(app: FastAPI):
    while True:
        try:
            now = datetime.utcnow()
            paid_users = await list_paid_users()

            for paid_user in paid_users:
                if not paid_user.expires_at:
                    continue

                days_left = (paid_user.expires_at.date() - now.date()).days

                if days_left < 0:
                    expired_now = await mark_paid_user_expired(paid_user.telegram_id)
                    if expired_now:
                        await app.state.bot_app.bot.send_message(
                            chat_id=ADMIN_ID,
                            text=(
                                "⛔ Подписка закончилась\n"
                                f"ID: {paid_user.telegram_id}\n"
                                f"Тариф: {paid_user.tariff}\n"
                                f"Дата окончания: {paid_user.expires_at}"
                            ),
                        )
                    continue

                if days_left not in (3, 2, 1):
                    continue

                warning_sent = await mark_paid_user_warning(paid_user.telegram_id, days_left)
                if not warning_sent:
                    continue

                amount = _tariff_amount(paid_user.tariff)
                if amount is None:
                    logger.warning("Unknown tariff for renewal link: %s", paid_user.tariff)
                    continue

                payment = await asyncio.to_thread(
                    create_payment,
                    amount,
                    paid_user.telegram_id,
                    f"{paid_user.tariff} (продление)",
                )

                payment_url = payment.get("url") or payment.get("redirect")
                transaction_id = str(payment.get("id") or payment.get("transaction_id") or payment.get("transactionId", ""))
                if transaction_id:
                    await save_payment(
                        transaction_id=transaction_id,
                        telegram_id=paid_user.telegram_id,
                        tariff=paid_user.tariff,
                        amount=amount,
                    )

                await app.state.bot_app.bot.send_message(
                    chat_id=paid_user.telegram_id,
                    text=(
                        f"⚠️ Подписка заканчивается через {days_left} дн.\n"
                        f"Тариф: {paid_user.tariff}\n\n"
                        f"Ссылка на продление: {payment_url or 'ссылка временно недоступна'}"
                    ),
                )
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.error("Subscription reminder loop failed: %s", exc)

        await asyncio.sleep(3600)





@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
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

    reminder_task = asyncio.create_task(_send_subscription_reminders(app))

    yield
    # что будет происходить при выходе
    try:
        await application.bot.delete_webhook()
    finally:
        reminder_task.cancel()
        try:
            await reminder_task
        except asyncio.CancelledError:
            pass
        await application.stop()
        await application.shutdown()



def init_fastapi_app():
    app = FastAPI(lifespan=lifespan)

    app.include_router(admin_router)
    app.include_router(cabinet_router)
    app.include_router(telegram_router)
    app.include_router(payment_router, prefix='/cp')

    return app