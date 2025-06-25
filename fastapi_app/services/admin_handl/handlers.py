from __future__ import annotations

from typing import Optional

from aiogram import F, Router, types
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from bot.logger import logger
from bot.keyboards import get_inline_keyboard
from core.db import get_async_session
from crud.users import users_crud
from crud.child_registrations import (
    get_all_registrations,
    get_registrations_count,
    get_registration_by_id,
    update_registration_status,
)
from .keyboards import get_users_list_keyboard, get_child_registrations_keyboard

admin_router = Router()


class StartState(StatesGroup):
    """Стартовый стэйт."""
    START_ADMIN = State()
    USERS = State()
    CHILD_REGISTRATIONS = State()


# Обновленное главное меню администратора
MAIN_MENU_ADMIN = (
    "Меню администратора:\n"
    "1. Список пользователей\n"
    "2. Список зарегистрированных детей"
)

ADMIN_USERS_MENU = get_inline_keyboard(
    ("Список пользователей", "users_list"),
    ("Список детей", "child_registrations_list"),
    sizes=(1, 1),
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
        MAIN_MENU_ADMIN,
        reply_markup=ADMIN_USERS_MENU,
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
        registrations = await get_all_registrations(session, offset=page * per_page, limit=per_page)
        total_registrations = await get_registrations_count(session)

    keyboard = get_child_registrations_keyboard(registrations, page, total_registrations, per_page)

    await state.update_data(current_menu="child_registrations_list", current_page=page)
    await callback.message.edit_text(
        ("Управление зарегистрированными детьми.\n\n"
         f"Список детей (страница {page + 1}):"),
        reply_markup=keyboard,
    )
    await callback.answer()


@admin_router.callback_query(F.data.startswith("child_reg_"))
async def handle_child_registration_action(
    callback: types.CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    """Обрабатывает действия над записью ребенка (утвердить/отклонить)."""
    action, reg_id = callback.data.split("_")[1:]  # Например, "child_reg_approve_1"
    reg_id = int(reg_id)

    async with get_async_session() as session:
        registration = await get_registration_by_id(session, reg_id)
        if not registration:
            await callback.answer("Запись не найдена.", show_alert=True)
            return

        if action == "approve":
            if update_registration_status(session, reg_id, "approved"):
                await callback.answer("Регистрация утверждена.")
            else:
                await callback.answer("Ошибка при утверждении.", show_alert=True)
        elif action == "reject":
            if update_registration_status(session, reg_id, "rejected"):
                await callback.answer("Регистрация отклонена.")
            else:
                await callback.answer("Ошибка при отклонении.", show_alert=True)

    # Проверяем, изменилось ли содержимое перед редактированием
    data = await state.get_data()
    page = data.get("current_page", 0)
    per_page = 5
    async with get_async_session() as session:
        registrations = await get_all_registrations(session, offset=page * per_page, limit=per_page)
        total_registrations = await get_registrations_count(session)
        new_keyboard = get_child_registrations_keyboard(registrations, page, total_registrations, per_page)
        new_text = (
            f"Управление зарегистрированными детьми.\n\n"
            f"Список детей (страница {page + 1}): {id(registrations)}"  # Уникальный идентификатор
        )

        # Редактируем только если есть изменения
        current_message = callback.message
        if current_message.text != new_text or current_message.reply_markup != new_keyboard:
            await current_message.edit_text(
                new_text,
                reply_markup=new_keyboard,
            )
        else:
            logger.warning("No changes detected, skipping edit_text.")

    await callback.answer()