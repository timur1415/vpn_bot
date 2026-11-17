"""Общие элементы оформления бота GLOW VPN: картинки, кнопки, подписи."""

from functools import lru_cache
from pathlib import Path

from telegram import InlineKeyboardButton, InputMediaPhoto

PHOTO_DIR = Path(__file__).resolve().parents[1] / "photo"
PHOTO_MAIN = "glow.jpg"      # светлячок — главное меню и инфо-разделы
PHOTO_SHOP = "glow_orb.jpg"  # портал — выбор тарифа и оформление

BRAND = "✦ <b>GLOW VPN</b> ✦"
DIVIDER = "⋆ ˚｡⋆ ✦ ⋆｡˚ ⋆"


@lru_cache(maxsize=None)
def _photo_bytes(name: str) -> bytes:
    return (PHOTO_DIR / name).read_bytes()


def photo(name: str = PHOTO_MAIN) -> bytes:
    """Картинка для send_photo / InputMediaPhoto (читается с диска один раз)."""
    return _photo_bytes(name)


def media(caption: str, name: str = PHOTO_MAIN) -> InputMediaPhoto:
    return InputMediaPhoto(media=photo(name), caption=caption, parse_mode="HTML")


def home_button(text: str = "🌌 Главное меню") -> InlineKeyboardButton:
    return InlineKeyboardButton(text, callback_data="main_menu", style="danger")


def buy_button(text: str = "🛸 Подключить VPN") -> InlineKeyboardButton:
    return InlineKeyboardButton(text, callback_data="buy", style="success")


def plural(n: int, one: str, few: str, many: str) -> str:
    n = abs(n) % 100
    if 10 < n < 20:
        return many
    if n % 10 == 1:
        return one
    if 2 <= n % 10 <= 4:
        return few
    return many
