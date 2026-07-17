from fastapi import FastAPI
from contextlib import asynccontextmanager
from datetime import datetime
import asyncio
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

from bot_init import create_aplication
from server.routes.admin_routes import router as admin_router
from server.routes.cabinet_routes import router as cabinet_router
from server.routes.telegram_routes import router as telegram_router
from server.routes.payment_routes import router as payment_router

from config.config import WEBHOOK_URL, TELEGRAM_WEBHOOK_PATH, SECRET_TOKEN, ADMIN_ID

from db.db import (
    init_db,
    list_paid_users,
    mark_paid_user_warning,
    mark_paid_user_expired,
    delete_paid_user_if_expired,
)

logger = logging.getLogger(__name__)


async def _send_subscription_reminders(app: FastAPI):
    while True:
        try:
            now = datetime.utcnow()
            paid_users = await list_paid_users()

            for paid_user in paid_users:
                try:
                    if not paid_user.expires_at:
                        continue

                    days_left = (paid_user.expires_at.date() - now.date()).days

                    if days_left <= -3:
                        deleted_now = await delete_paid_user_if_expired(paid_user.telegram_id)
                        if deleted_now:
                            await app.state.bot_app.bot.send_message(
                                chat_id=ADMIN_ID,
                                text=(
                                    "🗑 Пользователь удален из БД после окончания подписки\n"
                                    f"ID: {paid_user.telegram_id}\n"
                                    f"Тариф: {paid_user.tariff}\n"
                                    f"Дата окончания: {paid_user.expires_at}"
                                ),
                            )
                        continue

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

                    if days_left not in (3, 2, 1, 0):
                        continue

                    if (
                        (days_left == 3 and paid_user.warned_3_at)
                        or (days_left == 2 and paid_user.warned_2_at)
                        or (days_left == 1 and paid_user.warned_1_at)
                        or (days_left == 0 and getattr(paid_user, "warned_0_at", None))
                    ):
                        continue

                    days_text = "сегодня" if days_left == 0 else f"через {days_left} дн."
                    keyboard = InlineKeyboardMarkup(
                        [[InlineKeyboardButton("💳 Продлить подписку", callback_data="tariffs")]]
                    )
                    await app.state.bot_app.bot.send_message(
                        chat_id=paid_user.telegram_id,
                        text=(
                            f"⚠️ Подписка заканчивается {days_text}\n"
                            f"Тариф: {paid_user.tariff}"
                        ),
                        reply_markup=keyboard,
                    )

                    await app.state.bot_app.bot.send_message(
                        chat_id=ADMIN_ID,
                        text=(
                            "⚠️ Подписка скоро закончится\n"
                            f"ID: {paid_user.telegram_id}\n"
                            f"Username: {f'@{paid_user.username}' if paid_user.username else '-'}\n"
                            f"Тариф: {paid_user.tariff}\n"
                            f"Осталось: {days_text}\n"
                            f"Дата окончания: {paid_user.expires_at}"
                        ),
                    )

                    await mark_paid_user_warning(paid_user.telegram_id, days_left)
                except Exception as user_exc:
                    logger.error(
                        "Failed reminder for user %s: %s",
                        paid_user.telegram_id,
                        user_exc,
                    )
                    username = f"@{paid_user.username}" if paid_user.username else "username не указан"
                    try:
                        await app.state.bot_app.bot.send_message(
                            chat_id=ADMIN_ID,
                            text=(
                                "⚠️ Не удалось отправить напоминание о продлении\n"
                                f"Пользователь: {username}\n"
                                f"Тариф: {paid_user.tariff}\n"
                                f"Ошибка: {user_exc}"
                            ),
                        )
                    except Exception as admin_notify_exc:
                        logger.error("Failed to notify admin about reminder error: %s", admin_notify_exc)
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