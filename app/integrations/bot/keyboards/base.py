# app/integrations/bot/keyboards/base.py
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import Tuple, Optional
from app.core.settings import settings


def get_inline_keyboard(
    *buttons: Tuple[str, str],
    sizes: Tuple[int, ...] = (2,),
    placeholder: Optional[str] = None,
    url_buttons: Optional[Tuple[Tuple[str, str], ...]] = None,
) -> InlineKeyboardMarkup:
    """Создает инлайн-клавиатуру с кнопками.

    Args:
        buttons: Список кортежей (текст кнопки, callback-данные).
        sizes: Размеры строк клавиатуры.
        placeholder: Текст-заполнитель для поля ввода.
        url_buttons: Список кортежей (текст кнопки, URL).

    Returns:
        InlineKeyboardMarkup: Готовая инлайн-клавиатура.
    """
    keyboard = InlineKeyboardBuilder()
    for text, callback_data in buttons:
        keyboard.add(InlineKeyboardButton(text=text, callback_data=callback_data))
    if url_buttons:
        for text, url in url_buttons:
            keyboard.add(InlineKeyboardButton(text=text, url=url))
    return keyboard.adjust(*sizes).as_markup(
        resize_keyboard=True, input_field_placeholder=placeholder
    )


def get_main_menu_keyboard(is_admin: bool) -> InlineKeyboardMarkup:
    """Создает клавиатуру главного меню.

    Args:
        is_admin: Флаг, указывающий, является ли пользователь администратором.

    Returns:
        InlineKeyboardMarkup: Клавиатура главного меню.
    """
    keyboard = InlineKeyboardBuilder()
    buttons = [
        ("Соревнования", "competition"),
        ("Мероприятия", "event"),
        ("Записать ребенка в секцию", "child_reg"),
        ("Организация соревнований", "org_of_comps"),
    ]
    if is_admin:
        buttons.append(("Администратор", "admin"))
    for text, callback_data in buttons:
        keyboard.add(InlineKeyboardButton(text=text, callback_data=callback_data))
    url_buttons = [
        ("Посетить сайт федерации", "https://wrestrus90.ru"),
        ("Посетить страничку VKontakte", "https://vk.com/fsbmytishchi"),
    ]
    for text, url in url_buttons:
        keyboard.add(InlineKeyboardButton(text=text, url=url))
    sizes = (2, 1, 1, 1) if not is_admin else (2, 1, 1, 1, 1)
    return keyboard.adjust(*sizes).as_markup(resize_keyboard=True)
