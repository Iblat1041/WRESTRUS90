from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_child_registrations_keyboard(registrations, page: int, total: int, per_page: int):
    """Создает клавиатуру для списка зарегистрированных детей."""
    builder = InlineKeyboardBuilder()
    for reg in registrations:
        status = "✅" if reg.status == "approved" else "❌" if reg.status == "rejected" else "⏳"
        text = f"{reg.child_name} {reg.child_surname} ({reg.age}) [{status}]"
        builder.add(InlineKeyboardButton(
            text=text,
            callback_data=f"child_reg_{reg.id}"
        ))
    # Кнопки пагинации
    if page > 0:
        builder.add(InlineKeyboardButton(text="⬅️ Предыдущая", callback_data="child_reg_prev"))
    if (page + 1) * per_page < total:
        builder.add(InlineKeyboardButton(text="➡️ Следующая", callback_data="child_reg_next"))
    return builder.adjust(1).as_markup()


from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.models import User


def get_users_list_keyboard(users: list[User], page: int, total_users: int, per_page: int) -> InlineKeyboardMarkup:
    """Создает клавиатуру для списка пользователей с пагинацией.

    Args:
        users: Список объектов User для текущей страницы.
        page: Текущий номер страницы (начиная с 0).
        total_users: Общее количество пользователей.
        per_page: Количество пользователей на странице.

    Returns:
        InlineKeyboardMarkup: Готовая клавиатура.
    """
    builder = InlineKeyboardBuilder()

    # Добавляем кнопки для каждого пользователя
    for user in users:
        text = f"{user.name} (ID: {user.telegram_id})"
        builder.add(InlineKeyboardButton(
            text=text,
            callback_data=f"user_{user.id}"  # Уникальный callback_data для каждого пользователя
        ))

    # Добавляем кнопки пагинации
    if page > 0:
        builder.add(InlineKeyboardButton(
            text="⬅️ Предыдущая",
            callback_data="users_prev"
        ))
    if (page + 1) * per_page < total_users:
        builder.add(InlineKeyboardButton(
            text="➡️ Следующая",
            callback_data="users_next"
        ))

    # Настраиваем расположение кнопок (по одной в ряд)
    return builder.adjust(1).as_markup()
