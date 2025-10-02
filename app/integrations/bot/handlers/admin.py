# app/integrations/bot/handlers/admin.py
from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging

from app.domains.child_registrations.models import ChildRegistration
from app.domains.events.models import Event
from app.domains.users.models import User
from app.integrations.bot.models import EventFilter

from ..keyboards.admin import (
    get_admin_menu_keyboard,
    get_child_actions_keyboard,
    get_child_registrations_list_keyboard,
    get_event_actions_keyboard,
    get_events_list_keyboard,
    get_users_list_keyboard,
)
from ..service import BotService
from .base import QuizState

logger = logging.getLogger("my_app.bot.handlers.admin")

admin_router = Router()


class StartState(StatesGroup):
    """Состояния для админских операций."""
    START_ADMIN = State()
    USERS = State()
    CHILD_REGISTRATIONS = State()
    SELECT_CHILD = State()
    SELECT_EVENT = State()


@admin_router.callback_query(F.data == "admin")
async def handle_admin_menu(
    callback: types.CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    bot_service: BotService,
) -> None:
    """Открывает меню администратора.

    Args:
        callback: Callback-запрос от пользователя.
        state: Контекст FSM для управления состояниями.
        session: Асинхронная сессия SQLAlchemy.
        bot_service: Сервис для работы с бизнес-логикой.
    """
    await state.set_state(StartState.START_ADMIN)
    await callback.message.edit_text(
        "Меню администратора", reply_markup=get_admin_menu_keyboard()
    )
    await callback.answer()


@admin_router.callback_query(F.data == "back_to_main")
async def handle_back_to_main(
    callback: types.CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    bot_service: BotService,
) -> None:
    """Возвращает пользователя в главное меню.

    Args:
        callback: Callback-запрос от пользователя.
        state: Контекст FSM для управления состояниями.
        session: Асинхронная сессия SQLAlchemy.
        bot_service: Сервис для работы с бизнес-логикой.
    """
    user = await bot_service.get_or_create_user(
        session, callback.from_user.id, callback.from_user.username
    )
    is_admin = user.admin_role is not None
    from ..keyboards.base import get_main_menu_keyboard

    await state.set_state(QuizState.MAIN_MENU)
    await callback.message.edit_text(
        f"Привет, {user.name}! Добро пожаловать в главное меню.",
        reply_markup=get_main_menu_keyboard(is_admin=is_admin),
    )
    await callback.answer()


@admin_router.callback_query(F.data == "users_list")
async def show_users_list(
    callback: types.CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    bot_service: BotService,
) -> None:
    """Показывает список пользователей с пагинацией.

    Args:
        callback: Callback-запрос от пользователя.
        state: Контекст FSM для управления состояниями.
        session: Асинхронная сессия SQLAlchemy.
        bot_service: Сервис для работы с бизнес-логикой.
    """
    data = await state.get_data()
    page: int = data.get("current_page", 0)
    per_page: int = 5
    users, total_users = await bot_service.list_users(session, page * per_page, per_page)
    keyboard = get_users_list_keyboard(users, page, total_users, per_page)
    await state.update_data(current_menu="users_list", current_page=page)
    await callback.message.edit_text(
        f"Список пользователей (страница {page + 1}):", reply_markup=keyboard
    )
    await callback.answer()


@admin_router.callback_query(F.data == "child_registrations_list")
async def show_child_registrations_list(
    callback: types.CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    bot_service: BotService,
) -> None:
    """Показывает список регистраций детей с пагинацией.

    Args:
        callback: Callback-запрос от пользователя.
        state: Контекст FSM для управления состояниями.
        session: Асинхронная сессия SQLAlchemy.
        bot_service: Сервис для работы с бизнес-логикой.
    """
    data = await state.get_data()
    page: int = data.get("current_page", 0)
    per_page: int = 5
    registrations, total = await bot_service.list_child_registrations(
        session, page * per_page, per_page
    )
    keyboard = get_child_registrations_list_keyboard(registrations, page, total, per_page)
    await state.update_data(current_menu="child_registrations_list", current_page=page)
    await callback.message.edit_text(
        f"Список детей (страница {page + 1}):", reply_markup=keyboard
    )
    await callback.answer()


@admin_router.callback_query(F.data.startswith("child_select_"))
async def show_child_actions(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
) -> None:
    """Показывает действия для выбранной регистрации ребенка.

    Args:
        callback: Callback-запрос от пользователя.
        state: Контекст FSM для управления состояниями.
        session: Асинхронная сессия SQLAlchemy.
    """
    reg_id = int(callback.data.split("_")[2])
    from app.domains.child_registrations.repo import child_registrations_repo

    registration = await child_registrations_repo.get_by_id(session, reg_id)
    if not registration:
        await callback.answer("Запись не найдена.", show_alert=True)
        return
    status = (
        "✅" if registration.status == "approved" else
        "❌" if registration.status == "rejected" else "⏳"
    )
    text = (
        f"{registration.child_name} {registration.child_surname} "
        f"(Возраст: {registration.age}) [{status}]"
    )
    keyboard = get_child_actions_keyboard(reg_id, registration.status)
    await state.set_state(StartState.SELECT_CHILD)
    await callback.message.edit_text(f"Действия для ребенка:\n\n{text}", reply_markup=keyboard)
    await callback.answer()


@admin_router.callback_query(F.data.startswith("child_reg_"))
async def handle_child_registration_action(
    callback: types.CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    bot_service: BotService,
) -> None:
    """Обрабатывает действия с регистрацией ребенка (утверждение/отклонение).

    Args:
        callback: Callback-запрос от пользователя.
        state: Контекст FSM для управления состояниями.
        session: Асинхронная сессия SQLAlchemy.
        bot_service: Сервис для работы с бизнес-логикой.
    """
    parts = callback.data.split("_")
    if len(parts) < 3:
        await callback.answer("Неверный формат действия.", show_alert=True)
        return
    action, reg_id = parts[2], int(parts[3])
    success = await bot_service.update_child_registration_status(session, reg_id, action)
    if not success:
        await callback.answer("Запись не найдена.", show_alert=True)
        return
    await callback.answer(
        f"Регистрация {'утверждена' if action == 'approve' else 'отклонена'}."
    )
    data = await state.get_data()
    page: int = data.get("current_page", 0)
    per_page: int = 5
    registrations, total = await bot_service.list_child_registrations(
        session, page * per_page, per_page
    )
    keyboard = get_child_registrations_list_keyboard(registrations, page, total, per_page)
    status_text = (
        f" (Последняя запись: {registrations[0].child_name} [{registrations[0].status}])"
        if registrations else ""
    )
    await callback.message.edit_text(
        f"Список детей (страница {page + 1}):{status_text}", reply_markup=keyboard
    )
    await callback.answer()


@admin_router.callback_query(F.data == "event_list_admin")
async def show_events_list(
    callback: types.CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    bot_service: BotService,
) -> None:
    """Показывает список мероприятий с пагинацией.

    Args:
        callback: Callback-запрос от пользователя.
        state: Контекст FSM для управления состояниями.
        session: Асинхронная сессия SQLAlchemy.
        bot_service: Сервис для работы с бизнес-логикой.
    """
    data = await state.get_data()
    page: int = data.get("current_page", 0)
    per_page: int = 5
    events, total = await bot_service.list_events(session, EventFilter(category="all"))
    keyboard = get_events_list_keyboard(events, page, total, per_page)
    await state.update_data(current_menu="event_list_admin", current_page=page)
    await callback.message.edit_text(
        f"Список мероприятий (страница {page + 1}):", reply_markup=keyboard
    )
    await callback.answer()


@admin_router.callback_query(F.data.startswith("event_select_"))
async def show_event_actions(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
) -> None:
    """Показывает действия для выбранного мероприятия.

    Args:
        callback: Callback-запрос от пользователя.
        state: Контекст FSM для управления состояниями.
        session: Асинхронная сессия SQLAlchemy.
    """
    event_id = int(callback.data.split("_")[2])
    from app.domains.events.repo import events_repo

    event = await events_repo.get_by_id(session, event_id)
    if not event:
        await callback.answer("Мероприятие не найдено.", show_alert=True)
        return
    status = {"active": "✅", "inactive": "❌", "pending": "⏳"}.get(event.status, "⏳")
    text = f"{event.title} (ID: {event.vk_post_id}) [{status}, {event.category}]"
    keyboard = get_event_actions_keyboard(event_id, event.status, event.category)
    await state.set_state(StartState.SELECT_EVENT)
    await callback.message.edit_text(
        f"Действия для мероприятия:\n\n{text}", reply_markup=keyboard
    )
    await callback.answer()


@admin_router.callback_query(F.data.startswith("event_action_"))
async def handle_event_action(
    callback: types.CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    bot_service: BotService,
) -> None:
    """Обрабатывает действия с мероприятием (изменение статуса/категории, удаление).

    Args:
        callback: Callback-запрос от пользователя.
        state: Контекст FSM для управления состояниями.
        session: Асинхронная сессия SQLAlchemy.
        bot_service: Сервис для работы с бизнес-логикой.
    """
    parts = callback.data.split("_")
    if len(parts) < 4 or (parts[2] != "delete" and len(parts) < 5):
        await callback.answer("Неверный формат действия.", show_alert=True)
        return
    action_type, value, event_id = (
        parts[2],
        parts[3] if parts[2] != "delete" else None,
        int(parts[4] if parts[2] != "delete" else parts[3]),
    )
    if action_type == "delete":
        success = await bot_service.delete_event(session, event_id)
        await callback.answer(
            "Мероприятие удалено." if success else "Ошибка при удалении."
        )
    else:
        success = await bot_service.update_event_status_or_category(
            session, event_id, action_type, value
        )
        await callback.answer(
            f"{'Статус' if action_type == 'status' else 'Категория'} изменён на {value}."
            if success else "Ошибка при изменении."
        )
    data = await state.get_data()
    page: int = data.get("current_page", 0)
    per_page: int = 5
    events, total = await bot_service.list_events(session, EventFilter(category="all"))
    keyboard = get_events_list_keyboard(events, page, total, per_page)
    status_text = (
        f" (Последнее: {events[0].title} [{events[0].status}, {events[0].category}])"
        if events else ""
    )
    await callback.message.edit_text(
        f"Список мероприятий (страница {page + 1}):{status_text}",
        reply_markup=keyboard,
    )
    await callback.answer()
