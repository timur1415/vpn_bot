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

        message = " ID                             Name      Username \n"
        for user in users:
            print(user)
            id = user[0]
            user_first_name = user[1]
            user_name = user[2]
            message += f"{id}          {user_first_name}      {user_name} \n"
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message,
            parse_mode='MarkdownV2'
        )