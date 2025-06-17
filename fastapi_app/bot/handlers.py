from aiogram import Router, types
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select

from core.db import get_async_session
from bot.keyboards import MAIN_MENU_KB
from services.models import User

base_router = Router()


class QuizState(StatesGroup):
    """Класс состояний FSM для управления главным меню."""

    MAIN_MENU = State()


@base_router.message(Command("start"))
async def start(
    message: types.Message,
    state: FSMContext,
) -> None:
    user_id = message.from_user.id
    async with get_async_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            user = User(telegram_id=user_id, name=message.from_user.username or "Anonymous")
            session.add(user)
            await session.commit()
        await state.set_state(QuizState.MAIN_MENU)
    await message.answer(
        f"Привет {user.name} добро пожаловать на страничку Федерации Борьбы г. Мытищи",
        reply_markup=MAIN_MENU_KB,
    )
    await message.delete()
