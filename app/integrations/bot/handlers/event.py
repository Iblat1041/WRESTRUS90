# app/integrations/bot/handlers/event.py
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from enum import Enum
from typing import List
import logging

from app.domains.events.models import Event
from app.domains.events.repo import events_repo

from ..keyboards.base import get_main_menu_keyboard
from ..keyboards.event import build_event_list_keyboard
from ..models import EventFilter
from ..service import BotService

logger = logging.getLogger("my_app.bot.handlers.event")

event_router = Router()


class EventCategory(Enum):
    """Категории событий."""
    COMPETITION = "competition"
    EVENT = "event"
    SPONSOR = "sponsor"


class EventState(StatesGroup):
    """Состояния для работы с событиями."""
    START_EVENT = State()
    DETAILS_EVENT = State()
    current_page = State()
    total_pages = State()
    message_id = State()
    selected_event_id = State()
    category = State()


@event_router.callback_query(F.data == "competition")
async def handle_competitions(
    callback: types.CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    bot_service: BotService,
) -> None:
    """Показывает список соревнований.

    Args:
        callback: Callback-запрос от пользователя.
        state: Контекст FSM для управления состояниями.
        session: Асинхронная сессия SQLAlchemy.
        bot_service: Сервис для работы с бизнес-логикой.
    """
    await state.set_state(EventState.START_EVENT)
    await state.update_data(category=EventCategory.COMPETITION.value)
    await show_event_list(
        callback, state, 1, EventCategory.COMPETITION.value, bot_service, session
    )


@event_router.callback_query(F.data == "event")
async def handle_events(
    callback: types.CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    bot_service: BotService,
) -> None:
    """Показывает список мероприятий.

    Args:
        callback: Callback-запрос от пользователя.
        state: Контекст FSM для управления состояниями.
        session: Асинхронная сессия SQLAlchemy.
        bot_service: Сервис для работы с бизнес-логикой.
    """
    await state.set_state(EventState.START_EVENT)
    await state.update_data(category=EventCategory.EVENT.value)
    await show_event_list(
        callback, state, 1, EventCategory.EVENT.value, bot_service, session
    )


@event_router.callback_query(F.data == "sponsor")
async def handle_sponsors(
    callback: types.CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    bot_service: BotService,
) -> None:
    """Показывает список спонсоров.

    Args:
        callback: Callback-запрос от пользователя.
        state: Контекст FSM для управления состояниями.
        session: Асинхронная сессия SQLAlchemy.
        bot_service: Сервис для работы с бизнес-логикой.
    """
    await state.set_state(EventState.START_EVENT)
    await state.update_data(category=EventCategory.SPONSOR.value)
    await show_event_list(
        callback, state, 1, EventCategory.SPONSOR.value, bot_service, session
    )


@event_router.callback_query(F.data.startswith("page_"))
async def handle_pagination(
    callback: types.CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    bot_service: BotService,
) -> None:
    """Обрабатывает пагинацию списка событий.

    Args:
        callback: Callback-запрос от пользователя.
        state: Контекст FSM для управления состояниями.
        session: Асинхронная сессия SQLAlchemy.
        bot_service: Сервис для работы с бизнес-логикой.
    """
    try:
        page = int(callback.data.split("_")[1])
        state_data = await state.get_data()
        category = state_data.get("category", EventCategory.COMPETITION.value)
        await show_event_list(callback, state, page, category, bot_service, session)
    except (ValueError, IndexError) as e:
        logger.error(f"Ошибка пагинации: {e}")
        await callback.answer("Ошибка обработки страницы.", show_alert=True)


@event_router.callback_query(F.data.startswith("/details_"))
async def handle_details(
    callback: types.CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    bot_service: BotService,
) -> None:
    """Показывает детали события.

    Args:
        callback: Callback-запрос от пользователя.
        state: Контекст FSM для управления состояниями.
        session: Асинхронная сессия SQLAlchemy.
        bot_service: Сервис для работы с бизнес-логикой.
    """
    try:
        event_id = int(callback.data.split("_")[1])
        await state.set_state(EventState.DETAILS_EVENT)
        await show_event_details(callback, state, event_id, session)
    except (ValueError, IndexError) as e:
        logger.error(f"Ошибка загрузки деталей: {e}")
        await callback.answer("Ошибка обработки события.", show_alert=True)


@event_router.callback_query(F.data.startswith("back_to_list_"))
async def handle_back_to_list(
    callback: types.CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    bot_service: BotService,
) -> None:
    """Возвращает к списку событий.

    Args:
        callback: Callback-запрос от пользователя.
        state: Контекст FSM для управления состояниями.
        session: Асинхронная сессия SQLAlchemy.
        bot_service: Сервис для работы с бизнес-логикой.
    """
    try:
        page = int(callback.data.split("_")[-1])
        state_data = await state.get_data()
        category = state_data.get("category", EventCategory.COMPETITION.value)
        await state.set_state(EventState.START_EVENT)
        await show_event_list(callback, state, page, category, bot_service, session)
    except (ValueError, IndexError) as e:
        logger.error(f"Ошибка возврата: {e}")
        await callback.answer("Ошибка возврата к списку.", show_alert=True)


@event_router.callback_query(F.data == "back_to_menu")
async def handle_back_to_menu(
    callback: types.CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    bot_service: BotService,
) -> None:
    """Возвращает в главное меню.

    Args:
        callback: Callback-запрос от пользователя.
        state: Контекст FSM для управления состояниями.
        session: Асинхронная сессия SQLAlchemy.
        bot_service: Сервис для работы с бизнес-логикой.
    """
    user = await bot_service.get_or_create_user(
        session, callback.from_user.id, callback.from_user.username
    )
    is_admin = user.admin_role is not None
    await state.clear()
    await callback.message.answer(
        f"Привет, {user.name}! Добро пожаловать!",
        reply_markup=get_main_menu_keyboard(is_admin=is_admin),
    )
    await callback.message.delete()
    await callback.answer()


async def show_event_list(
    callback: types.CallbackQuery,
    state: FSMContext,
    page: int,
    category: str,
    bot_service: BotService,
    session: AsyncSession,
    events_per_page: int = 5,
) -> None:
    """Показывает список событий с пагинацией.

    Args:
        callback: Callback-запрос от пользователя.
        state: Контекст FSM для управления состояниями.
        page: Номер текущей страницы.
        category: Категория событий.
        bot_service: Сервис для работы с бизнес-логикой.
        session: Асинхронная сессия SQLAlchemy.
        events_per_page: Количество событий на страницу.
    """
    events, total = await bot_service.list_events(
        session, EventFilter(category=category, offset=(page - 1) * events_per_page)
    )
    if not total:
        await callback.answer(f"Нет активных {category}.", show_alert=True)
        return
    total_pages = max(1, (total + events_per_page - 1) // events_per_page)
    page = max(1, min(page, total_pages))
    category_titles = {
        EventCategory.COMPETITION.value: "🏆 Активные соревнования",
        EventCategory.EVENT.value: "📅 Активные мероприятия",
        EventCategory.SPONSOR.value: "🤝 Спонсоры",
    }
    message_text = (
        f"{category_titles.get(category, 'События')} (Страница {page}/{total_pages}):\n\n"
        + "\n".join(
            f"Пост № <b>{event.id}</b>. <b>{event.title[:30].capitalize()}"
            f"{'...' if len(event.title) > 30 else ''}</b> - "
            f"{event.published_at.strftime('%Y-%m-%d')}"
            for event in events
        )
    )
    keyboard = build_event_list_keyboard(events, page, total_pages)
    if page == 1:
        await callback.message.delete()
    msg = await callback.message.answer(
        message_text, reply_markup=keyboard, parse_mode="HTML"
    )
    await state.update_data(
        current_page=page,
        total_pages=total_pages,
        message_id=msg.message_id,
        category=category,
    )


async def show_event_details(
    callback: types.CallbackQuery, state: FSMContext, event_id: int, session: AsyncSession
) -> None:
    """Показывает детали выбранного события.

    Args:
        callback: Callback-запрос от пользователя.
        state: Контекст FSM для управления состояниями.
        event_id: ID события.
        session: Асинхронная сессия SQLAlchemy.
    """
    event = await events_repo.get_by_id(session, event_id)
    if not event:
        await callback.answer("Событие не найдено.", show_alert=True)
        return
    message_text = (
        f"<b>{event.title}</b>\n"
        f"{event.content}\n\n"
        f"Дата: {event.published_at.strftime('%Y-%m-%d')}"
    )
    state_data = await state.get_data()
    if event.images and isinstance(event.images, list) and event.images:
        await callback.message.answer_photo(
            photo=event.images[0], caption=message_text, parse_mode="HTML"
        )
    else:
        await callback.message.answer(message_text, parse_mode="HTML")
    await state.update_data(selected_event_id=event_id, viewing_mode="details")
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="🔙 Вернуться к списку",
                    callback_data=f"back_to_list_{state_data.get('current_page', 1)}",
                )
            ]
        ]
    )
    await callback.message.answer("Вернуться к событиям", reply_markup=keyboard)
