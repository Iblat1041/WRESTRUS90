import logging
from typing import List
from aiogram import types

from services.models import Event

# Настройка логирования
logger = logging.getLogger(__name__)

def build_event_list_keyboard(
    events: List[Event],
    current_page: int,
    total_pages: int
) -> types.InlineKeyboardMarkup:
    """Строит инлайн-клавиатуру для списка событий.

    Args:
        events: Список объектов событий.
        current_page: Текущая страница пагинации (начинается с 1).
        total_pages: Общее количество страниц.

    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками для событий, навигации и возврата в меню.

    Raises:
        ValueError: Если current_page или total_pages имеют некорректные значения.
    """
    if current_page < 1:
        logger.error(f"Некорректное значение current_page: {current_page}")
        raise ValueError("current_page должен быть >= 1")
    if total_pages < 0:
        logger.error(f"Некорректное значение total_pages: {total_pages}")
        raise ValueError("total_pages должен быть >= 0")

    keyboard_rows = []

    # Логируем создание клавиатуры
    logger.debug(f"Создание клавиатуры для {len(events)} событий, страница {current_page}/{total_pages}")

    # Кнопки "Подробнее" для событий (по 2 в ряд)
    if events:
        for i in range(0, len(events), 2):
            row = [
                types.InlineKeyboardButton(
                    text=f"Смотреть пост № {event.id}",
                    callback_data=f"/details_{event.id}"
                )
                for event in events[i:i+2]
            ]
            keyboard_rows.append(row)
    else:
        logger.warning("Список событий пуст, создается клавиатура только с кнопкой 'В меню'")

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

    # Кнопка возврата в меню
    keyboard_rows.append([
        types.InlineKeyboardButton(
            text="🔙 В меню",
            callback_data="back_to_menu"
        )
    ])

    return types.InlineKeyboardMarkup(inline_keyboard=keyboard_rows)