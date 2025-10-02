# app/integrations/bot/handlers/child.py
from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from ..keyboards.base import get_main_menu_keyboard
from ..models import ChildRegistrationInput
from ..service import BotService

logger = logging.getLogger("my_app.bot.handlers.child")

child_router = Router()


class ChildRegState(StatesGroup):
    """Состояния для процесса регистрации ребенка."""
    CHILD_NAME = State()
    CHILD_SURNAME = State()
    AGE = State()
    PARENT_CONTACT = State()


@child_router.callback_query(F.data == "child_reg")
async def start_child_registration(
    callback: types.CallbackQuery, state: FSMContext
) -> None:
    """Начинает процесс регистрации ребенка.

    Args:
        callback: Callback-запрос от пользователя.
        state: Контекст FSM для управления состояниями.
    """
    await state.set_state(ChildRegState.CHILD_NAME)
    await callback.message.answer("Введите имя ребенка:")


@child_router.message(ChildRegState.CHILD_NAME)
async def process_child_name(message: types.Message, state: FSMContext) -> None:
    """Обрабатывает ввод имени ребенка.

    Args:
        message: Сообщение от пользователя.
        state: Контекст FSM для управления состояниями.
    """
    await state.update_data(child_name=message.text)
    await state.set_state(ChildRegState.CHILD_SURNAME)
    await message.answer("Введите фамилию ребенка:")


@child_router.message(ChildRegState.CHILD_SURNAME)
async def process_child_surname(message: types.Message, state: FSMContext) -> None:
    """Обрабатывает ввод фамилии ребенка.

    Args:
        message: Сообщение от пользователя.
        state: Контекст FSM для управления состояниями.
    """
    await state.update_data(child_surname=message.text)
    await state.set_state(ChildRegState.AGE)
    await message.answer("Введите возраст ребенка:")


@child_router.message(ChildRegState.AGE)
async def process_age(message: types.Message, state: FSMContext) -> None:
    """Обрабатывает ввод возраста ребенка.

    Args:
        message: Сообщение от пользователя.
        state: Контекст FSM для управления состояниями.
    """
    try:
        age = int(message.text)
        if not 0 < age < 150:
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
    bot_service: BotService,
) -> None:
    """Завершает регистрацию ребенка, сохраняя данные.

    Args:
        message: Сообщение от пользователя.
        state: Контекст FSM для управления состояниями.
        session: Асинхронная сессия SQLAlchemy.
        bot_service: Сервис для работы с бизнес-логикой.
    """
    data = await state.get_data()
    try:
        child_data = ChildRegistrationInput(
            child_name=data["child_name"],
            child_surname=data["child_surname"],
            age=data["age"],
            parent_contact=message.text,
        )
        user = await bot_service.get_or_create_user(
            session, message.from_user.id, message.from_user.username
        )
        await bot_service.register_child(session, user.id, child_data)
        is_admin = user.admin_role is not None
        await state.clear()
        await message.answer(
            "Регистрация ребенка успешно завершена!",
            reply_markup=get_main_menu_keyboard(is_admin=is_admin),
        )
    except Exception as e:
        await message.answer(f"Ошибка при сохранении: {e}")
