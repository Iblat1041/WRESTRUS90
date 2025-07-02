from aiogram import types

from services.models import Event


def build_event_list_keyboard(
    events: list[Event],
    current_page: int,
    total_pages: int
) -> types.InlineKeyboardMarkup:
    """Строит инлайн-клавиатуру для списка событий"""
    keyboard_rows = []
    
    # Кнопки "Подробнее" (по 2 в ряд)
    for i in range(0, len(events), 2):
        row = [
            types.InlineKeyboardButton(
                text=f"Подробнее {event.id}",
                callback_data=f"/details_{event.id}"
            )
            for event in events[i:i+2]
        ]
        keyboard_rows.append(row)

    # Кнопки навигации
    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(types.InlineKeyboardButton(
            text="⬅️ Назад", 
            callback_data=f"page_{current_page-1}"
        ))
    if current_page < total_pages:
        nav_buttons.append(types.InlineKeyboardButton(
            text="Вперед ➡️", 
            callback_data=f"page_{current_page+1}"
        ))
    
    if nav_buttons:
        keyboard_rows.append(nav_buttons)
    
    # Кнопка возврата
    keyboard_rows.append([
        types.InlineKeyboardButton(
            text="🔙 В меню", 
            callback_data="back_to_menu"
        )
    ])

    return types.InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
