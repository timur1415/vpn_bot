"""Общие элементы оформления бота GLOW VPN: картинки, кнопки, подписи."""

from functools import lru_cache
from pathlib import Path

from telegram import InlineKeyboardButton, InputMediaPhoto

PHOTO_DIR = Path(__file__).resolve().parents[1] / "photo"
PHOTO_MAIN = "glow.jpg"      # светлячок — главное меню и инфо-разделы
PHOTO_SHOP = "glow_orb.jpg"  # портал — выбор тарифа и оформление

BRAND = "✦ <b>GLOW VPN</b> ✦"
DIVIDER = "┈┈┈┈┈┈┈┈┈┈┈┈┈┈"

SUPPORT_USERNAME = "@i1i1i1iij"
SUPPORT_URL = f"https://t.me/{SUPPORT_USERNAME.replace('@', '')}"

# Без username менеджер не сможет написать пользователю первым.
USERNAME_NOTE = (
    "❗ <b>Важно:</b> чтобы менеджер мог с вами связаться, в профиле Telegram "
    "обязательно должен быть указан <b>username</b>.\n"
    f"Если username нет — напишите в поддержку сами: {SUPPORT_USERNAME}"
)
NO_USERNAME_WARNING = (
    "❗ <b>У вас не указан username</b> — менеджер не сможет написать вам первым. "
    f"Напишите в поддержку сами: {SUPPORT_USERNAME}"
)


@lru_cache(maxsize=None)
def _photo_bytes(name: str) -> bytes:
    return (PHOTO_DIR / name).read_bytes()


def photo(name: str = PHOTO_MAIN) -> bytes:
    """Картинка для send_photo / InputMediaPhoto (читается с диска один раз)."""
    return _photo_bytes(name)


def media(caption: str, name: str = PHOTO_MAIN) -> InputMediaPhoto:
    return InputMediaPhoto(media=photo(name), caption=caption, parse_mode="HTML")


def home_button(text: str = "🏠 Главное меню") -> InlineKeyboardButton:
    return InlineKeyboardButton(text, callback_data="main_menu", style="danger")


def buy_button(text: str = "⚡ Подключить VPN") -> InlineKeyboardButton:
    return InlineKeyboardButton(text, callback_data="buy", style="success")


def support_button(text: str = "💬 Написать в поддержку") -> InlineKeyboardButton:
    return InlineKeyboardButton(text, url=SUPPORT_URL, style="primary")


def plural(n: int, one: str, few: str, many: str) -> str:
    n = abs(n) % 100
    if 10 < n < 20:
        return many
    if n % 10 == 1:
        return one
    if 2 <= n % 10 <= 4:
        return few
    return many
