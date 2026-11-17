import logging

from fastapi import APIRouter, Request

from config.config import ADMIN_ID, MERCHANT_ID, SECRET_KEY
from db.db import get_payment, update_payment_status, upsert_paid_user_from_payment

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/payment/callback")
async def payment_callback(request: Request):
    merchant_id_header = request.headers.get("X-MerchantId")
    secret_header = request.headers.get("X-Secret")

    if merchant_id_header != MERCHANT_ID or secret_header != SECRET_KEY:
        logger.warning(
            "Payment callback rejected: invalid merchant headers (X-MerchantId=%s)",
            merchant_id_header,
        )
        return {"status": "forbidden"}
    
    data = await request.json()
    logger.info("Payment callback received: %s", data)

    transaction_id = (
        data.get("transactionId")
        or data.get("transaction_id")
        or data.get("id")
    )
    raw_status = data.get("status") or data.get("state") or ""
    status = str(raw_status).upper()

    if not status and data.get("success") is True:
        status = "CONFIRMED"

    if status in {"SUCCESS", "PAID", "COMPLETED"}:
        status = "CONFIRMED"

    if not transaction_id:
        logger.warning("Payment callback missing transaction_id: %s", data)
        return {"status": "ok"}
    #добавить в гет пэймент проверку тг id
    payment = await get_payment(str(transaction_id))
    if not payment:
        logger.warning("Payment not found for transaction_id: %s", transaction_id)
        return {"status": "ok"}
    


    status_updated = await update_payment_status(str(transaction_id), status or "PENDING")

    if status == "CONFIRMED" and status_updated:
        bot_app = request.app.state.bot_app
        try:
            payment = await get_payment(str(transaction_id))
            if not payment:
                logger.warning("Payment disappeared after confirmation: %s", transaction_id)
                return {"status": "ok"}

            device_count = int(getattr(payment, "device_count", 1) or 1)

            user_name = "-"
            username = None
            try:
                chat = await bot_app.bot.get_chat(payment.telegram_id)
                user_name = " ".join(filter(None, [getattr(chat, "first_name", None), getattr(chat, "last_name", None)])) or "-"
                username = getattr(chat, "username", None)
            except Exception:
                logger.warning("Could not fetch telegram profile for %s", payment.telegram_id)

            await upsert_paid_user_from_payment(str(transaction_id), username=username)

            await bot_app.bot.send_message(
                chat_id=ADMIN_ID,
                text=(
                    "💰 Новая оплата\n"
                    f"ID: {payment.telegram_id}\n"
                    f"Имя: {user_name or '-'}\n"
                    f"Username: {f'@{username}' if username else '-'}\n"
                    f"Тариф: {payment.tariff}\n"
                    f"Устройств: {device_count}\n"
                    f"Сумма: {payment.amount} RUB\n"
                    f"Оплачено: {payment.paid_at or '-'}\n"
                    f"Продлить до: {payment.renew_at or '-'}"
                ),
            )

            await bot_app.bot.send_message(
                chat_id=payment.telegram_id,
                text=(
                    f"✦ GLOW VPN ✦\n\n"
                    f"💜 Оплата прошла успешно — спасибо, что выбрали нас!\n"
                    f"┈┈┈┈┈┈┈┈┈┈┈┈┈┈\n"
                    f"🧾 Тариф: {payment.tariff}\n"
                    f"📱 Устройств: {device_count}\n\n"
                    f"Что дальше:\n"
                    f"1️⃣ Менеджер пришлёт персональную ссылку для подключения\n"
                    f"2️⃣ И видеоинструкцию: как установить приложение и включить VPN\n\n"
                    f"⏳ Обычно это занимает 5–15 минут.\n"
                    f"🌙 Срок подписки можно посмотреть в Личном кабинете (/start).\n\n"
                    f"❗ Важно: чтобы менеджер мог с вами связаться, в профиле Telegram "
                    f"обязательно должен быть указан username.\n"
                    f"Если username нет — напишите в поддержку сами: @i1i1i1iij"
                ),
            )
        except Exception as e:
            logger.error("Failed to notify user %s: %s", payment.telegram_id, e)

    return {"status": "ok"}