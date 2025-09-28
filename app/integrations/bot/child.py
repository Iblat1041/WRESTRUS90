"""Хэндлеры регистрации ребёнка через бота."""

from __future__ import annotations

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.child_registrations.service import register_child
from app.integrations.bot.keyboards import get_main_menu_keyboard

child_router = Router()


class ChildRegState(StatesGroup):
    """Состояния диалога регистрации ребёнка."""

    CHILD_NAME = State()
    CHILD_SURNAME = State()
    AGE = State()
    PARENT_CONTACT = State()


@child_router.callback_query(F.data == "child_reg")
async def start_child_registration(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Начать процесс регистрации ребёнка."""
    await state.set_state(ChildRegState.CHILD_NAME)
    await callback.message.answer("Введите имя ребёнка:")


@child_router.message(ChildRegState.CHILD_NAME)
async def process_child_name(message: types.Message, state: FSMContext) -> None:
    """Принять имя ребёнка и перейти к фамилии."""
    await state.update_data(child_name=message.text)
    await state.set_state(ChildRegState.CHILD_SURNAME)
    await message.answer("Введите фамилию ребёнка:")


@child_router.message(ChildRegState.CHILD_SURNAME)
async def process_child_surname(message: types.Message, state: FSMContext) -> None:
    """Принять фамилию ребёнка и перейти к возрасту."""
    await state.update_data(child_surname=message.text)
    await state.set_state(ChildRegState.AGE)
    await message.answer("Введите возраст ребёнка (число):")


@child_router.message(ChildRegState.AGE)
async def process_age(message: types.Message, state: FSMContext) -> None:
    """Проверить и принять возраст, перейти к контакту родителя."""
    try:
        age = int(message.text)
        if not 0 < age < 150:
            raise ValueError("Возраст должен быть от 1 до 149.")
        await state.update_data(age=age)
        await state.set_state(ChildRegState.PARENT_CONTACT)
        await message.answer("Введите контакт родителя (например, телефон):")
    except ValueError as err:
        await message.answer(f"Ошибка: {err}. Попробуйте ещё раз.")


@child_router.message(ChildRegState.PARENT_CONTACT)
async def process_parent_contact(
    message: types.Message,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    """Создать запись регистрации и вернуться в главное меню."""
    data = await state.get_data()
    await register_child(
        session=session,
        user_tg_id=message.from_user.id,
        user_name=message.from_user.username or "Anonymous",
        child_name=data["child_name"],
        child_surname=data["child_surname"],
        age=data["age"],
        parent_contact=message.text,
    )
    await state.clear()
    await message.answer(
        "Регистрация ребёнка успешно завершена!",
        reply_markup=get_main_menu_keyboard(is_admin=False),
    )
