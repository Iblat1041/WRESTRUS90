# Импорты из стандартной библиотеки
from typing import Optional

# Импорты из aiogram
from aiogram import Router, types
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# Импорты из SQLAlchemy
from sqlalchemy import select
from sqlalchemy.orm import selectinload

# Импорт для логирования
import logging

# Создание логгера
logger = logging.getLogger(__name__)

# Импорты из кастомных модулей
from core.db import get_async_session
from bot.keyboards import get_main_menu_keyboard  # Импортируем только функцию
from services.models import User

# Создание роутера
base_router = Router()

# Определение состояний FSM
class QuizState(StatesGroup):
    """Класс состояний FSM для управления главным меню."""
    MAIN_MENU = State()

# Обработчик команды /start
@base_router.message(Command("start"))
async def start(
    message: types.Message,
    state: FSMContext,
) -> None:
    user_id = message.from_user.id
    async with get_async_session() as session:
        try:
            result = await session.execute(
                select(User).where(User.telegram_id == user_id).options(selectinload(User.admin_role))
            )
            user = result.scalar_one_or_none()
            if not user:
                user = User(telegram_id=user_id, name=message.from_user.username or "Anonymous")
                session.add(user)
                await session.commit()
                await session.refresh(user, ["admin_role"])  # Убедимся, что admin_role загружено
        except Exception as e:
            logger.error("Database error in /start: %s", str(e))
            await message.answer("Произошла ошибка, попробуйте позже.")
            return

        is_admin = user.admin_role is not None
        main_menu_kb = get_main_menu_keyboard(is_admin=is_admin)

        await state.set_state(QuizState.MAIN_MENU)
        await message.answer(
            f"Привет {user.name} добро пожаловать на страничку Федерации Борьбы г. Мытищи",
            reply_markup=main_menu_kb,
        )
        await message.delete()