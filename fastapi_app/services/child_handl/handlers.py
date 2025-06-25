from __future__ import annotations

from typing import Optional

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_async_session
from bot.keyboards import MAIN_MENU_KB
from services.models import ChildRegistration, User

child_router = Router()


class ChildRegState(StatesGroup):
    """Состояния для регистрации ребенка."""
    CHILD_NAME = State()
    CHILD_SURNAME = State()
    AGE = State()
    PARENT_CONTACT = State()


@child_router.callback_query(F.data == "child_reg")
async def start_child_registration(
    callback: types.CallbackQuery,  # Исправлен тип с message на callback
    state: FSMContext,
) -> None:
    """Начать процесс регистрации ребенка."""
    await state.set_state(ChildRegState.CHILD_NAME)
    await callback.message.answer("Введите имя ребенка:")


@child_router.message(ChildRegState.CHILD_NAME)
async def process_child_name(
    message: types.Message,
    state: FSMContext,
) -> None:
    """Обработать имя ребенка и запросить фамилию."""
    await state.update_data(child_name=message.text)
    await state.set_state(ChildRegState.CHILD_SURNAME)
    await message.answer("Введите фамилию ребенка:")


@child_router.message(ChildRegState.CHILD_SURNAME)
async def process_child_surname(
    message: types.Message,
    state: FSMContext,
) -> None:
    """Обработать фамилию ребенка и запросить возраст."""
    await state.update_data(child_surname=message.text)
    await state.set_state(ChildRegState.AGE)
    await message.answer("Введите возраст ребенка:")


@child_router.message(ChildRegState.AGE)
async def process_age(
    message: types.Message,
    state: FSMContext,
) -> None:
    """Обработать возраст и запросить контакт родителя."""
    try:
        age = int(message.text)
        if not 0 < age < 150:  # Проверка разумного диапазона возраста
            raise ValueError("Возраст должен быть от 1 до 149 лет")
        await state.update_data(age=age)
        await state.set_state(ChildRegState.PARENT_CONTACT)
        await message.answer("Введите контакт родителя (например, телефон):")
    except ValueError as e:
        await message.answer(f"Ошибка: {e}. Пожалуйста, введите корректный возраст.")


@child_router.message(ChildRegState.PARENT_CONTACT)
async def process_parent_contact(
    message: types.Message,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    """Завершить регистрацию ребенка и вернуть в главное меню."""
    data = await state.get_data()
    user_id = message.from_user.id

    # Проверка или создание пользователя
    result = await session.execute(select(User).where(User.telegram_id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        user = User(
            telegram_id=user_id,
            name=message.from_user.username or "Anonymous",
            created_at=func.now(),
        )
        session.add(user)
        await session.flush()  # Получаем ID пользователя

    # Сохранение регистрации ребенка
    child_reg = ChildRegistration(
        user_id=user.id,
        child_name=data["child_name"],
        child_surname=data["child_surname"],
        age=data["age"],
        parent_contact=message.text,
        status="pending",
        created_at=func.now(),
    )
    session.add(child_reg)
    try:
        await session.commit()
    except Exception as e:
        await session.rollback()
        await message.answer(f"Ошибка при сохранении: {e}")
        return

    await state.clear()
    await message.answer(
        "Регистрация ребенка успешно завершена!",
        reply_markup=MAIN_MENU_KB,
    )
