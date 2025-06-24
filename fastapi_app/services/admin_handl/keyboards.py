from aiogram.types import InlineKeyboardMarkup

from bot.keyboards import get_inline_keyboard
from constants_kb.admin import (
    BACK_BUTTON,
    BACK_TO_MAIN_BUTTON,
    CREATE_USER_BUTTON,
    USERS_LIST_BUTTON,
)

ADMIN_USERS_MENU = get_inline_keyboard(
    (USERS_LIST_BUTTON, 'users_list'),
    (CREATE_USER_BUTTON, 'create_user'),
    (BACK_BUTTON, 'back_to_admin_menu'),
    placeholder='Вы находитесь в меню пользователей',
    sizes=(2, 2),
)


from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_users_list_keyboard(
    users: list,
    page: int = 0,
    total_users: int = 0,
    per_page: int = 5,
    back_button_text: str = "⬅️ Вернуться",
    back_to_main_button_text: str = "🏠 На главную",
) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с списком пользователей и кнопками навигации/возврата.

    Args:
        users: Список пользователей для отображения.
        page: Текущая страница (нумерация с 0).
        total_users: Общее количество пользователей.
        per_page: Количество пользователей на странице.
        back_button_text: Текст кнопки возврата к меню пользователей.
        back_to_main_button_text: Текст кнопки возврата на главное меню.

    Returns:
        InlineKeyboardMarkup: Сформированная клавиатура.
    """
    # Формируем кнопки для пользователей
    buttons = [
        (f"{user.name} {user.email or ''}", f"user_{user.id}")
        for user in users
    ]

    # Формируем кнопки навигации
    navigation_buttons = []
    if page > 0:
        navigation_buttons.append(('⬅️ Назад', f'prev_page_{page-1}'))
    if (page + 1) * per_page < total_users:
        navigation_buttons.append(('Вперед ➡️', f'next_page_{page+1}'))
    buttons.extend(navigation_buttons)

    # Добавляем кнопки возврата
    buttons.extend(
        [
            (back_button_text, 'back_to_users_menu'),
            (back_to_main_button_text, 'cancel_to_main_menu'),
        ],
    )

    # Вычисляем количество строк для sizes
    num_user_rows = len(users)  # Одна кнопка на пользователя в отдельной строке
    nav_and_back_rows = 1  # Одна строка для навигации и кнопок возврата
    sizes = (1,) * num_user_rows + (2,) * nav_and_back_rows

    return get_inline_keyboard(
        *buttons,
        sizes=sizes,
        placeholder='Выберите пользователя',
    )
