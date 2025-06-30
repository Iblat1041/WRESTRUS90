from __future__ import annotations

from typing import Optional

from aiogram import F, Router, types
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bot.logger import logger
from bot.keyboards import get_main_menu_keyboard, get_inline_keyboard
from core.db import get_async_session
from crud.events import events_crud
from crud.users import users_crud
from crud.child_registrations import child_reg_crud
# from crud.child_registrations import (
#     get_all_registrations,
#     get_registrations_count,
#     get_registration_by_id,
#     update_registration_status,
# )
from services.models import User
from .keyboards import (
    get_child_actions_keyboard,
    get_child_registrations_list_keyboard,
    get_users_list_keyboard,
    get_events_list_keyboard,
    get_event_actions_keyboard,
)

admin_router = Router()


class StartState(StatesGroup):
    """Стартовый стэйт для состояний администратора."""
    START_ADMIN = State()
    USERS = State()
    CHILD_REGISTRATIONS = State()
    SELECT_CHILD = State()
    SELECT_EVENT = State()


ADMIN_USERS_MENU = get_inline_keyboard(
    ("Список пользователей", "users_list"),
    ("Список детей", "child_registrations_list"),
    ("Список мероприятий", "event_list_admin"),
    ("Вернуться в главное меню", "back_to_main"),
    sizes=(1, 1, 1, 1),
)


@admin_router.callback_query(F.data == "admin")
async def handle_admin_menu(
    callback: types.CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    """Обрабатывает нажатие кнопки 'Администратор'."""
    await state.set_state(StartState.START_ADMIN)
    await callback.message.edit_text(
        "Меню администратора",
        reply_markup=ADMIN_USERS_MENU,
    )
    await callback.answer()


@admin_router.callback_query(F.data == "back_to_main")
async def handle_back_to_main(
    callback: types.CallbackQuery,
    state: FSMContext,
    session: AsyncSession,  # Добавляем сессию как зависимость
) -> None:
    """Возвращает пользователя в главное меню."""
    # Ленивый импорт QuizState
    from bot.handlers import QuizState
    user_id = callback.from_user.id
    async with session:  # Используем переданную сессию
        result = await session.execute(
            select(User)
            .where(User.telegram_id == user_id)
            .options(selectinload(User.admin_role))  # Предварительная загрузка admin_role
        )
        user = result.scalar_one_or_none()
        if not user:
            user = User(telegram_id=user_id, name=callback.from_user.username or "Anonymous")
            session.add(user)
            await session.commit()
    
    is_admin = user.admin_role is not None if user else False
    main_menu_kb = get_main_menu_keyboard(is_admin=is_admin)

    await state.set_state(QuizState.MAIN_MENU)
    await callback.message.edit_text(
        f"Привет {user.name} добро пожаловать на страничку Федерации Борьбы г. Мытищи",
        reply_markup=main_menu_kb,
    )
    await callback.answer()


@admin_router.callback_query(F.data == "users_list")
async def show_users_list(
    callback: types.CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    """Обрабатывает отображение списка пользователей."""
    data = await state.get_data()
    page = data.get("current_page", 0)
    per_page = 5

    async with get_async_session() as session:
        users = await users_crud.get_all_users(session, offset=page * per_page, limit=per_page)
        total_users = await users_crud.get_users_count(session)

    keyboard = get_users_list_keyboard(users, page, total_users, per_page)

    await state.update_data(current_menu="users_list", current_page=page)
    await callback.message.edit_text(
        ("Выберите необходимого пользователя для изменения его профиля.\n\n"
         f"Список пользователей (страница {page + 1}):"),
        reply_markup=keyboard,
    )
    await callback.answer()


@admin_router.callback_query(F.data == "child_registrations_list")
async def show_child_registrations_list(
    callback: types.CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    """Обрабатывает отображение списка зарегистрированных детей."""
    data = await state.get_data()
    page = data.get("current_page", 0)
    per_page = 5

    async with get_async_session() as session:
        registrations = await child_reg_crud.get_all_registrations(
            session,
            offset=page * per_page,
            limit=per_page
        )
        total_registrations = await child_reg_crud.get_registrations_count(session)

    keyboard = get_child_registrations_list_keyboard(
        registrations,
        page,
        total_registrations,
        per_page
    )

    await state.update_data(
        current_menu="child_registrations_list",
        current_page=page
    )
    await callback.message.edit_text(
        ("Управление зарегистрированными детьми.\n\n"
         f"Список детей (страница {page + 1}):"),
        reply_markup=keyboard,
    )
    await callback.answer()


@admin_router.callback_query(F.data.startswith("child_select_"))
async def show_child_actions(
    callback: types.CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    """Отображает действия (Утвердить/Отклонить) для выбранного ребенка.

    Args:
        callback: Объект CallbackQuery от aiogram.
        state: Контекст конечного автомата состояний.
        session: Асинхронная сессия SQLAlchemy.
    """
    reg_id = int(callback.data.split("_")[2])  # Извлекаем reg_id из child_select_{reg_id}

    async with get_async_session() as session:
        registration = await child_reg_crud.get_registration_by_id(session, reg_id)
        if not registration:
            await callback.answer("Запись не найдена.", show_alert=True)
            return

    status = "✅" if registration.status == "approved" else "❌" if registration.status == "rejected" else "⏳"
    text = f"{registration.child_name} {registration.child_surname} (Возраст: {registration.age}) [{status}]"
    keyboard = get_child_actions_keyboard(reg_id, registration.status)

    await state.set_state(StartState.SELECT_CHILD)
    await callback.message.edit_text(
        f"Действия для ребенка:\n\n{text}",
        reply_markup=keyboard,
    )
    await callback.answer()


@admin_router.callback_query(F.data.startswith("child_reg_"))
async def handle_child_registration_action(
    callback: types.CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    """Обрабатывает действия над записью ребенка (утвердить/отклонить).

    Args:
        callback: Объект CallbackQuery от aiogram.
        state: Контекст конечного автомата состояний.
        session: Асинхронная сессия SQLAlchemy.
    """
    parts = callback.data.split("_")
    if len(parts) < 3:  # Минимальный формат: ["child", "reg", "action", "reg_id"]
        await callback.answer("Неверный формат действия.", show_alert=True)
        return

    action = parts[2]  # Третий элемент — действие (approve/reject)
    reg_id = int(parts[3])  # Четвертый элемент — ID регистрации

    async with get_async_session() as session:
            registration = await child_reg_crud.get_registration_by_id(session, reg_id)
            if not registration:
                await callback.answer("Запись не найдена.", show_alert=True)
                return

            if action == "approve":
                if await child_reg_crud.update_registration_status(session, reg_id, "approved"):  # Добавлен await
                    await callback.answer("Регистрация утверждена.")
                else:
                    await callback.answer("Ошибка при утверждении.", show_alert=True)
            elif action == "reject":
                if await child_reg_crud.update_registration_status(session, reg_id, "rejected"):  # Добавлен await
                    await callback.answer("Регистрация отклонена.")
                else:
                    await callback.answer("Ошибка при отклонении.", show_alert=True)

        # Обновляем список после изменения статуса
    data = await state.get_data()
    page = data.get("current_page", 0)
    per_page = 5
    async with get_async_session() as session:
        registrations = await child_reg_crud.get_all_registrations(
            session,
            offset=page * per_page,
            limit=per_page
        )
        total_registrations = await child_reg_crud.get_registrations_count(session)
        new_keyboard = get_child_registrations_list_keyboard(
            registrations,
            page,
            total_registrations,
            per_page
        )
        # Добавляем информацию о последней измененной записи в текст
        last_updated_reg = next((reg for reg in registrations if reg.id == reg_id), None)
        status_text = f" (Последняя запись: {last_updated_reg.child_name} [{last_updated_reg.status}]" if last_updated_reg else ""
        new_text = (
            f"Управление зарегистрированными детьми.\n\n"
            f"Список детей (страница {page + 1}):{status_text}"
        )

        current_message = callback.message
        # Преобразуем клавиатуру в строку для сравнения содержимого
        current_markup_str = str(current_message.reply_markup) if current_message.reply_markup else ""
        new_markup_str = str(new_keyboard) if new_keyboard else ""
        # Проверяем, изменилось ли сообщение
        if (current_message.text != new_text or current_markup_str != new_markup_str):
            await current_message.edit_text(
                new_text,
                reply_markup=new_keyboard,
            )
            logger.info("Message updated with new status.")
        else:
            logger.info("Message not modified, skipping edit_text.")

    await callback.answer()


@admin_router.callback_query(F.data == "event_list_admin")
async def show_events_list(
    callback: types.CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    """Обрабатывает отображение списка мероприятий."""
    data = await state.get_data()
    page = data.get("current_page", 0)
    per_page = 5

    async with get_async_session() as session:
        events = await events_crud.get_all_events(
            session,
            offset=page * per_page,
            limit=per_page
        )
        total_events = await events_crud.get_events_count(session)

    keyboard = get_events_list_keyboard(
        events,
        page,
        total_events,
        per_page
    )

    await state.update_data(
        current_menu="event_list_admin",
        current_page=page
    )
    await callback.message.edit_text(
        ("Управление мероприятиями.\n\n"
         f"Список мероприятий (страница {page + 1}):"),
        reply_markup=keyboard,
    )
    await callback.answer()


@admin_router.callback_query(F.data.startswith("event_select_"))
async def show_event_actions(
    callback: types.CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    """Отображает действия (изменить статус/категорию, удалить) для выбранного мероприятия."""
    event_id = int(callback.data.split("_")[2])

    async with get_async_session() as session:
        event = await events_crud.get_event_by_id(session, event_id)
        if not event:
            await callback.answer("Мероприятие не найдено.", show_alert=True)
            return

    status = {"active": "✅", "inactive": "❌", "pending": "⏳"}.get(event.status, "⏳")
    text = f"{event.title} (ID: {event.vk_post_id}) [{status}, {event.category}]"
    keyboard = get_event_actions_keyboard(event_id, event.status, event.category)

    await state.set_state(StartState.SELECT_EVENT)
    await callback.message.edit_text(
        f"Действия для мероприятия:\n\n{text}",
        reply_markup=keyboard,
    )
    await callback.answer()


@admin_router.callback_query(F.data.startswith("event_action_"))
async def handle_event_action(
    callback: types.CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    """Обрабатывает действия над мероприятием (изменить статус/категорию, удалить)."""
    parts = callback.data.split("_")
    if len(parts) < 4 or (parts[2] != "delete" and len(parts) < 5):
        await callback.answer("Неверный формат действия.", show_alert=True)
        return

    action_type = parts[2]
    event_id = int(parts[4] if action_type != "delete" else parts[3])
    value = parts[3] if action_type != "delete" else None

    async with get_async_session() as session:
        event = await events_crud.get_event_by_id(session, event_id)
        if not event:
            await callback.answer("Мероприятие не найдено.", show_alert=True)
            return

        if action_type == "status":
            if value in ["active", "inactive", "pending"]:
                if await events_crud.update_event_status(session, event_id, value):
                    await callback.answer(f"Статус изменён на {value}.")
                else:
                    await callback.answer("Ошибка при изменении статуса.", show_alert=True)
            else:
                await callback.answer("Недопустимый статус.", show_alert=True)
        elif action_type == "category":
            if value in ["competition", "event", "sponsor"]:
                if await events_crud.update_event_category(session, event_id, value):
                    await callback.answer(f"Категория изменена на {value}.")
                else:
                    await callback.answer("Ошибка при изменении категории.", show_alert=True)
            else:
                await callback.answer("Недопустимая категория.", show_alert=True)
        elif action_type == "delete":
            if await events_crud.delete_event(session, event_id):
                await callback.answer("Мероприятие удалено.")
            else:
                await callback.answer("Ошибка при удалении.", show_alert=True)

    # Обновляем список после изменения
    data = await state.get_data()
    page = data.get("current_page", 0)
    per_page = 5
    async with get_async_session() as session:
        events = await events_crud.get_all_events(
            session,
            offset=page * per_page,
            limit=per_page
        )
        total_events = await events_crud.get_events_count(session)
        new_keyboard = get_events_list_keyboard(
            events,
            page,
            total_events,
            per_page
        )
        last_updated_event = next((evt for evt in events if evt.id == event_id), None)
        status_text = (f" (Последнее: {last_updated_event.title} [{last_updated_event.status}, {last_updated_event.category}])" 
                       if last_updated_event else "")
        new_text = (
            f"Управление мероприятиями.\n\n"
            f"Список мероприятий (страница {page + 1}):{status_text}"
        )

        current_message = callback.message
        current_markup_str = str(current_message.reply_markup) if current_message.reply_markup else ""
        new_markup_str = str(new_keyboard) if new_keyboard else ""
        if current_message.text != new_text or current_markup_str != new_markup_str:
            await current_message.edit_text(
                new_text,
                reply_markup=new_keyboard,
            )
            logger.info(f"Event list updated after action: {action_type}={value or 'delete'} on event_id={event_id}")
        else:
            logger.info("Event list not modified, skipping edit_text.")

    await callback.answer()
