from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from services.models import ChildRegistration
from core.db import get_async_session

child_router = Router()


class ChildRegState(StatesGroup):
    """Состояния для регистрации ребенка."""
    CHILD_NAME = State()
    CHILD_SURNAME = State()
    AGE = State()
    PARENT_CONTACT = State()


@child_router.message(F.text == "child_reg")
async def start_child_registration(
    message: types.Message,
    state: FSMContext,
) -> None:
    """Начать процесс регистрации ребенка."""
    await state.set_state(ChildRegState.CHILD_NAME)
    await message.answer("Введите имя ребенка:")


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
    await state.update_data(age=int(message.text))
    await state.set_state(ChildRegState.PARENT_CONTACT)
    await message.answer("Введите контакт родителя (например, телефон):")


@child_router.message(ChildRegState.PARENT_CONTACT)
async def process_parent_contact(
    message: types.Message,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    """Завершить регистрацию ребенка."""
    data = await state.get_data()
    async with get_async_session() as session:
        child_reg = ChildRegistration(
            user_id=message.from_user.id,
            child_name=data["child_name"],
            child_surname=data["child_surname"],
            age=data["age"],
            parent_contact=message.text,
        )
        session.add(child_reg)
        await session.commit()
    await state.clear()
    await message.answer("Регистрация ребенка успешно завершена!")