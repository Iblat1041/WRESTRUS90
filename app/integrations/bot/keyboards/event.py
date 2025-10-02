# app/integrations/bot/keyboards/event.py
from aiogram import types
from typing import List
from app.domains.events.models import Event


def build_event_list_keyboard(
    events: List[Event], current_page: int, total_pages: int
) -> types.InlineKeyboardMarkup:
    """Создает клавиатуру для списка событий.

    Args:
        events: Список событий.
        current_page: Текущая страница пагинации.
        total_pages: Общее количество страниц.

    Returns:
        InlineKeyboardMarkup: Клавиатура для списка событий.
    """
    keyboard_rows = []
    if events:
        for i in range(0, len(events), 2):
            row = [
                types.InlineKeyboardButton(
                    text=f"Смотреть пост № {event.id}", callback_data=f"/details_{event.id}"
                )
                for event in events[i : i + 2]
            ]
            keyboard_rows.append(row)
    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(
            types.InlineKeyboardButton(
                text="⬅️ Назад", callback_data=f"page_{current_page-1}"
            )
        )
    if current_page < total_pages:
        nav_buttons.append(
            types.InlineKeyboardButton(
                text="Вперед ➡️", callback_data=f"page_{current_page+1}"
            )
        )
    if nav_buttons:
        keyboard_rows.append(nav_buttons)
    keyboard_rows.append(
        [types.InlineKeyboardButton(text="🔙 В меню", callback_data="back_to_menu")]
    )
    return types.InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
