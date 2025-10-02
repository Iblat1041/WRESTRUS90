# app/integrations/bot/handlers/base.py
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import asyncio
import logging

from app.core.settings import settings

from ..keyboards.base import get_inline_keyboard, get_main_menu_keyboard
from ..service import BotService

logger = logging.getLogger("my_app.bot.handlers.base")

base_router = Router()
group_router = Router()


class QuizState(StatesGroup):
    """Состояния для базовых операций бота."""
    MAIN_MENU = State()


@base_router.message(Command(commands=["start", "menu@vasek_100_bot"]))
async def start(
    message: types.Message,
    state: FSMContext,
    session: AsyncSession,
    bot_service: BotService,
) -> None:
    """Обрабатывает команды /start и /menu в личных чатах.

    Args:
        message: Сообщение от пользователя.
        state: Контекст FSM для управления состояниями.
        session: Асинхронная сессия SQLAlchemy.
        bot_service: Сервис для работы с бизнес-логикой.
    """
    if message.chat.type != "private":
        response = await message.answer(
            "Команда /start работает только в личном чате. Используйте /menu в группе."
        )
        logger.info(
            f"Ignored /start command from user {message.from_user.id} in chat "
            f"{message.chat.id} (type: {message.chat.type})"
        )
        await asyncio.sleep(5)
        try:
            await response.delete()
            await message.delete()
        except Exception as e:
            logger.error(f"Failed to delete response in chat {message.chat.id}: {e}")
        return

    user = await bot_service.get_or_create_user(
        session, message.from_user.id, message.from_user.username
    )
    is_admin = user.admin_role is not None
    main_menu_kb = get_main_menu_keyboard(is_admin=is_admin)
    args = message.text.split()[1] if len(message.text.split()) > 1 else ""
    text = (
        f"Привет, {user.name}! Добро пожаловать в главное меню бота."
        if args == "menu"
        else f"Привет, {user.name}! Добро пожаловать на страничку Федерации Борьбы г. Мытищи"
    )
    await state.set_state(QuizState.MAIN_MENU)
    await message.answer(text, reply_markup=main_menu_kb)
    await message.delete()


@group_router.message(Command(commands=["menu", "menu@vasek_100_bot"]))
async def show_group_menu(message: types.Message) -> None:
    """Обрабатывает команду /menu в групповых чатах.

    Args:
        message: Сообщение от пользователя.
    """
    logger.info(
        f"Received /menu command from user {message.from_user.id} in chat "
        f"{message.chat.id}"
    )
    keyboard = get_inline_keyboard(
        ("Открыть меню бота", "start_menu"),
        sizes=(1,),
        url_buttons=[("Начать общение с ботом", f"https://t.me/{settings.bot_username}")],
    )
    response = await message.answer(
        "Нажмите кнопку, чтобы начать взаимодействие с ботом в личном чате:",
        reply_markup=keyboard,
    )
    await asyncio.sleep(5)
    try:
        await message.delete()
        await response.delete()
    except Exception as e:
        logger.error(f"Failed to delete messages in chat {message.chat.id}: {e}")


@base_router.callback_query(lambda c: c.data == "start_menu")
async def handle_start_menu_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    bot_service: BotService,
) -> None:
    """Обрабатывает callback для открытия меню в личном чате.

    Args:
        callback: Callback-запрос от пользователя.
        state: Контекст FSM для управления состояниями.
        session: Асинхронная сессия SQLAlchemy.
        bot_service: Сервис для работы с бизнес-логикой.
    """
    logger.info(f"Received callback 'start_menu' from user {callback.from_user.id}")
    user = await bot_service.get_or_create_user(
        session, callback.from_user.id, callback.from_user.username
    )
    is_admin = user.admin_role is not None
    main_menu_kb = get_main_menu_keyboard(is_admin=is_admin)
    try:
        await callback.message.bot.send_message(
            chat_id=callback.from_user.id,
            text=f"Привет, {user.name}! Добро пожаловать в главное меню бота!",
            reply_markup=main_menu_kb,
        )
    except Exception as e:
        logger.error(f"Failed to send message to user {callback.from_user.id}: {e}")
        await callback.message.answer(
            "Пожалуйста, начните чат с ботом, чтобы открыть меню."
        )
        await callback.answer()
        return
    await callback.message.delete()
    await callback.answer()