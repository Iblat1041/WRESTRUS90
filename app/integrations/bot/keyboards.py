"""Утилиты для построения inline-клавиатур бота."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_inline_keyboard(
    *buttons: tuple[str, str],
    sizes: tuple[int, ...] = (2,),
    url_buttons: tuple[tuple[str, str]] | None = None,
) -> InlineKeyboardMarkup:
    """
    Универсальная функция создания inline-клавиатуры.

    Args:
        buttons: пары (текст, callback_data).
        sizes: размерность рядов.
        url_buttons: пары (текст, url) для внешних ссылок.

    Returns:
        InlineKeyboardMarkup: готовая клавиатура.
    """
    kb = InlineKeyboardBuilder()
    for text, cb in buttons:
        kb.add(InlineKeyboardButton(text=text, callback_data=cb))
    if url_buttons:
        for text, url in url_buttons:
            kb.add(InlineKeyboardButton(text=text, url=url))
    return kb.adjust(*sizes).as_markup()


def get_main_menu_keyboard(is_admin: bool) -> InlineKeyboardMarkup:
    """
    Сформировать главное меню.

    Args:
        is_admin: признак администратора.

    Returns:
        InlineKeyboardMarkup: клавиатура главного меню.
    """
    kb = InlineKeyboardBuilder()
    rows = [
        ("Соревнования", "competition"),
        ("Мероприятия", "event"),
        ("Записать ребенка в секцию", "child_reg"),
        ("Организация соревнований", "org_of_comps"),
    ]
    if is_admin:
        rows.append(("Администратор", "admin"))
    for text, cb in rows:
        kb.add(InlineKeyboardButton(text=text, callback_data=cb))

    kb.add(InlineKeyboardButton(text="Посетить сайт федерации", url="https://wrestrus90.ru"))
    kb.add(InlineKeyboardButton(text="Посетить страничку VKontakte", url="https://vk.com/fsbmytishchi"))

    sizes = (2, 1, 1, 1) if not is_admin else (2, 1, 1, 1, 1)
    return kb.adjust(*sizes).as_markup()
