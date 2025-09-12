from typing import Optional
from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import logging
import asyncio  # Добавляем для использования asyncio.sleep

from core.db import get_async_session
from bot.keyboards import get_inline_keyboard, get_main_menu_keyboard
from services.models import User
from core.config import settings

# Создание логгера
logger = logging.getLogger(__name__)

# Создание роутеров
base_router = Router()
group_router = Router()

# Определение состояний FSM
class QuizState(StatesGroup):
    """Класс состояний FSM для управления главным меню."""
    MAIN_MENU = State()

# Обработчик команды /start
@base_router.message(Command(commands=["menu", "menu@vasek_100_bot"]))
async def start(message: types.Message, state: FSMContext) -> None:
    """Обработчик команды /start для личного чата с ботом."""
    if message.chat.type != "private":  # Проверка, что чат личный
        response = await message.answer("Команда /start работает только в личном чате. Используйте /menu в группе.")
        logger.info(f"Ignored /start command from user {message.from_user.id} in chat {message.chat.id} (type: {message.chat.type})")
        await asyncio.sleep(5)  # Ждём 10 секунд перед удалением
        try:
            await response.delete()  # Удаляем сообщение бота
            await message.delete()  # Удаляем сообщение пользователя
        except Exception as e:
            logger.error(f"Failed to delete response message in chat {message.chat.id}: {str(e)}")
        return

    user_id = message.from_user.id
    logger.info(f"Received /start command from user {user_id} in private chat")
    
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
                await session.refresh(user, ["admin_role"])
        except Exception as e:
            logger.error("Database error in /start: %s", str(e))
            await message.answer("Произошла ошибка, попробуйте позже.")
            return

        is_admin = user.admin_role is not None
        main_menu_kb = get_main_menu_keyboard(is_admin=is_admin)

        # Извлечение аргументов команды
        args = message.text.split()[1] if len(message.text.split()) > 1 else ""
        if args == "menu":
            await state.set_state(QuizState.MAIN_MENU)
            await message.answer(
                f"Привет, {user.name}! Добро пожаловать в главное меню бота.",
                reply_markup=main_menu_kb,
            )
        else:
            await state.set_state(QuizState.MAIN_MENU)
            await message.answer(
                f"Привет, {user.name}! Добро пожаловать на страничку Федерации Борьбы г. Мытищи",
                reply_markup=main_menu_kb,
            )
        await message.delete()

# Обработчик команды /menu в группе
@group_router.message(Command("menu"))
async def show_group_menu(message: types.Message) -> None:
    """Обработчик команды /menu для отображения меню в группе."""
    logger.info(f"Received /menu command from user {message.from_user.id} in chat {message.chat.id}")
    
    # Создание inline-клавиатуры с помощью get_inline_keyboard
    keyboard = get_inline_keyboard(
        ("Открыть меню бота", "start_menu"),  # Позиционный аргумент для кнопок
        sizes=(1,),
        url_buttons=[
            ("Начать общение с ботом", f"https://t.me/{settings.bot_username}?start=menu"),
        ],
    )

    await message.answer(
        "Нажмите кнопку, чтобы начать взаимодействие с ботом в личном чате:",
        reply_markup=keyboard,
    )

# Обработчик callback-кнопки
@base_router.callback_query(lambda c: c.data == "start_menu")
async def handle_start_menu_callback(callback: types.CallbackQuery) -> None:
    """Обработчик нажатия на кнопку 'Открыть меню бота'."""
    logger.info(f"Received callback 'start_menu' from user {callback.from_user.id}")
    user_id = callback.from_user.id
    async with get_async_session() as session:
        try:
            result = await session.execute(
                select(User).where(User.telegram_id == user_id).options(selectinload(User.admin_role))
            )
            user = result.scalar_one_or_none()
            if not user:
                user = User(telegram_id=user_id, name=callback.from_user.username or "Anonymous")
                session.add(user)
                await session.commit()
                await session.refresh(user, ["admin_role"])
        except Exception as e:
            logger.error("Database error in callback handler: %s", str(e))
            await callback.message.bot.send_message(
                chat_id=user_id,
                text="Произошла ошибка, попробуйте позже."
            )
            await callback.answer()
            return

        is_admin = user.admin_role is not None
        main_menu_kb = get_main_menu_keyboard(is_admin=is_admin)

        # Отправка сообщения в личный чат
        try:
            await callback.message.bot.send_message(
                chat_id=user_id,
                text=f"Привет, {user.name}! Добро пожаловать в главное меню бота!",
                reply_markup=main_menu_kb,
            )
        except Exception as e:
            logger.error(f"Failed to send message to user {user_id}: {str(e)}")
            await callback.message.answer("Пожалуйста, начните чат с ботом, чтобы открыть меню.")
            await callback.answer()
            return

        await callback.message.delete()  # Удаление сообщения с кнопкой в группе
        await callback.answer()  # Подтверждение обработки callback