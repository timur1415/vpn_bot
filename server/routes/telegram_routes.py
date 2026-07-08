from fastapi import APIRouter, Request
from telegram import Update

router = APIRouter()

@router.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()

    application = request.app.state.bot_app

    update = Update.de_json(
        data=data,
        bot=application.bot
    )

    await application.process_update(update)

    return {"ok": True}