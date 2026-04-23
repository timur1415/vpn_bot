from telegram.ext import ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

from config.config import ADMIN_ID

from db.db import get_all_users

async def tables_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = ADMIN_ID

    if update.effective_user.id != admin_id:
        await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='вход тоько для админов',
    )
    else:
        users = get_all_users()
        print(users)

    message = "```\nID                Name          Username\n"
    for user in users:
        id_str = str(user[0]).ljust(20)
        name_str = (user[1] or "-").ljust(15)
        username_str = user[2] or "-"
        message += f"{id_str}{name_str}{username_str}\n"
    message += "```"

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        parse_mode='MarkdownV2'
    )