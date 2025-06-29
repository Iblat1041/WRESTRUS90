from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from services.models import User, Event


def get_child_registrations_list_keyboard(
    registrations,
    page: int,
    total: int,
    per_page: int
) -> InlineKeyboardMarkup:
    """Создает клавиатуру для списка зарегистрированных детей с выбором."""
    builder = InlineKeyboardBuilder()
    for reg in registrations:
        status = "✅" if reg.status == "approved" else "❌" if reg.status == "rejected" else "⏳"
        text = f"{reg.child_name} {reg.child_surname} (Возраст: {reg.age}) [{status}]"
        builder.row(
            InlineKeyboardButton(
                text=text,
                callback_data=f"child_select_{reg.id}"
            )
        )
    if page > 0:
        builder.row(InlineKeyboardButton(
            text="⬅️ Предыдущая",
            callback_data="child_reg_prev"
        ))
    if (page + 1) * per_page < total:
        builder.row(InlineKeyboardButton(
            text="➡️ Следующая",
            callback_data="child_reg_next"
        ))
    builder.row(InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data="admin"
    ))
    return builder.as_markup()


def get_child_actions_keyboard(
    reg_id: int,
    status: str
) -> InlineKeyboardMarkup:
    """Создает клавиатуру с действиями для выбранного ребенка."""
    builder = InlineKeyboardBuilder()
    if status == "pending":
        builder.row(
            InlineKeyboardButton(
                text="Утвердить",
                callback_data=f"child_reg_approve_{reg_id}"
            ),
            InlineKeyboardButton(
                text="Отклонить",
                callback_data=f"child_reg_reject_{reg_id}"
            ),
            width=2
        )
    builder.row(
        InlineKeyboardButton(
            text="Назад",
            callback_data="child_registrations_list"
        )
    )
    return builder.as_markup()


def get_users_list_keyboard(
    users: list[User],
    page: int,
    total_users: int,
    per_page: int,
) -> InlineKeyboardMarkup:
    """Создает клавиатуру для списка пользователей с пагинацией."""
    builder = InlineKeyboardBuilder()
    for user in users:
        text = f"{user.name} (ID: {user.telegram_id})"
        builder.add(InlineKeyboardButton(
            text=text,
            callback_data=f"user_{user.id}"
        ))
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
    builder.add(InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data="admin"
    ))
    return builder.adjust(1).as_markup()


def get_events_list_keyboard(
    events: list[Event],
    page: int,
    total_events: int,
    per_page: int
) -> InlineKeyboardMarkup:
    """Создает клавиатуру для списка мероприятий с выбором."""
    builder = InlineKeyboardBuilder()
    for event in events:
        status = {"active": "✅", "inactive": "❌", "pending": "⏳"}.get(event.status, "⏳")
        text = f"{event.title} (ID: {event.vk_post_id}) [{status}, {event.category}]"
        builder.row(
            InlineKeyboardButton(
                text=text,
                callback_data=f"event_select_{event.id}"
            )
        )
    if page > 0:
        builder.row(InlineKeyboardButton(
            text="⬅️ Предыдущая",
            callback_data="event_prev"
        ))
    if (page + 1) * per_page < total_events:
        builder.row(InlineKeyboardButton(
            text="➡️ Следующая",
            callback_data="event_next"
        ))
    builder.row(InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data="admin"
    ))
    return builder.as_markup()


def get_event_actions_keyboard(
    event_id: int,
    status: str,
    category: str
) -> InlineKeyboardMarkup:
    """Создает клавиатуру с действиями для выбранного мероприятия."""
    builder = InlineKeyboardBuilder()
    status_options = ["active", "inactive", "pending"]
    category_options = ["competition", "event", "sponsor"]

    for stat in status_options:
        if stat != status:
            builder.add(InlineKeyboardButton(
                text=f"Статус: {stat}",
                callback_data=f"event_action_status_{stat}_{event_id}"
            ))
    for cat in category_options:
        if cat != category:
            builder.add(InlineKeyboardButton(
                text=f"Категория: {cat}",
                callback_data=f"event_action_category_{cat}_{event_id}"
            ))
    builder.add(InlineKeyboardButton(
        text="Удалить",
        callback_data=f"event_action_delete_{event_id}"
    ))
    builder.row(InlineKeyboardButton(
        text="Назад",
        callback_data="event_list_admin"
    ))
    return builder.adjust(2).as_markup()