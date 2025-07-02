import logging
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InputMediaPhoto
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_async_session
from event_handl.keyboards import build_event_list_keyboard
from bot.keyboards import get_main_menu_keyboard
from services.models import Event, User

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

event_router = Router()

class EventState(StatesGroup):
    """Состояния FSM для работы с событиями"""
    START_EVENT = State()      # Состояние просмотра списка событий
    DETAILS_EVENT = State()    # Состояние просмотра деталей события
    current_page = State()     # Текущая страница пагинации
    total_pages = State()      # Всего страниц
    message_id = State()       # ID последнего сообщения
    selected_event_id = State()# ID просматриваемого события

# region Основные обработчики

@event_router.callback_query(F.data == 'competition')
async def handle_competitions(
    callback: types.CallbackQuery,
    state: FSMContext,
    ) -> None:
    """Обработчик кнопки 'Соревнования'"""
    await state.set_state(EventState.START_EVENT)
    await show_event_list(callback, state, page=1)


@event_router.callback_query(F.data.startswith('page_'))
async def handle_pagination(
    callback: types.CallbackQuery,
    state: FSMContext,
    ) -> None:
    """Обработчик пагинации"""
    try:
        page = int(callback.data.split('_')[1])
        await show_event_list(callback, state, page)
    except (ValueError, IndexError) as e:
        logger.error(f"Ошибка пагинации: {e}")
        await callback.answer("Ошибка обработки страницы.", show_alert=True)


@event_router.callback_query(F.data.startswith('/details_'))
async def handle_details(
    callback: types.CallbackQuery,
    state: FSMContext,
    ) -> None:
    """Обработчик просмотра деталей события"""
    try:
        event_id = int(callback.data.split('_')[1])
        await state.set_state(EventState.DETAILS_EVENT)
        await show_event_details(callback, state, event_id)
    except (ValueError, IndexError) as e:
        logger.error(f"Ошибка загрузки деталей: {e}")
        await callback.answer("Ошибка обработки события.", show_alert=True)


@event_router.callback_query(F.data.startswith('back_to_list_'))
async def handle_back_to_list(
    callback: types.CallbackQuery,
    state: FSMContext,
    ) -> None:
    """Обработчик возврата к списку событий"""
    try:
        page = int(callback.data.split('_')[-1])
        await state.set_state(EventState.START_EVENT)
        await show_event_list(callback, state, page)
    except (ValueError, IndexError) as e:
        logger.error(f"Ошибка возврата: {e}")
        await callback.answer("Ошибка возврата к списку.", show_alert=True)


@event_router.callback_query(F.data == 'back_to_menu')
async def handle_back_to_menu(
    callback: types.CallbackQuery,
    state: FSMContext,
    ) -> None:
    """Обработчик возврата в главное меню"""
    await return_to_main_menu(callback, state)

# endregion

# region Вспомогательные функции

async def show_event_list(
    callback: types.CallbackQuery,
    state: FSMContext,
    page: int,
    events_per_page: int = 5
):
    """Отображает список событий с пагинацией"""
    async with get_async_session() as session:
        try:
            # Получаем данные из БД
            total_events = await get_total_events_count(session)
            if not total_events:
                await callback.answer("Нет активных соревнований.", show_alert=True)
                return

            # Вычисляем параметры пагинации
            total_pages = calculate_total_pages(total_events, events_per_page)
            page = normalize_page_number(page, total_pages)
            
            # Получаем события для страницы
            current_events = await get_events_for_page(
                session, page, events_per_page
            )

            # Формируем и отправляем сообщение
            await send_event_list_message(
                callback, state, current_events, page, total_pages
            )

        except Exception as e:
            logger.error(f"Ошибка показа списка: {e}", exc_info=True)
            await callback.answer("Ошибка загрузки данных.", show_alert=True)

async def show_event_details(
    callback: types.CallbackQuery,
    state: FSMContext,
    event_id: int
):
    """Отображает детали события"""
    async with get_async_session() as session:
        try:
            event = await get_event_by_id(session, event_id)
            if not event:
                await callback.answer("Событие не найдено.", show_alert=True)
                return

            # Отправляем контент события
            await send_event_content(callback, event)

            # Сохраняем состояние и отправляем клавиатуру
            await save_event_view_state(state, event_id)
            await send_back_button(callback, state)

        except Exception as e:
            logger.error(f"Ошибка показа деталей: {e}", exc_info=True)
            await callback.answer("Ошибка загрузки данных.", show_alert=True)


async def return_to_main_menu(
        callback: types.CallbackQuery,
        state: FSMContext
        ):
    """Возвращает пользователя в главное меню"""
    await state.clear()
    user = await get_user_by_telegram_id(callback.from_user.id)
    
    try:
        await callback.message.answer(
            f"Привет, {user.name if user else 'пользователь'}! Добро пожаловать!",
            reply_markup=get_main_menu_keyboard(is_admin=bool(user and user.admin_role))
        )
        await callback.message.delete()
    except Exception as e:
        logger.error(f"Ошибка возврата в меню: {e}")
    finally:
        await callback.answer()

# endregion

# region Работа с базой данных

async def get_total_events_count(session: AsyncSession) -> int:
    """Возвращает общее количество активных событий"""
    return await session.scalar(
        select(func.count(Event.id))
        .where(Event.category == 'competition')
        .where(Event.status == 'active')
    )


async def get_events_for_page(
    session: AsyncSession,
    page: int,
    per_page: int
) -> list[Event]:
    """Возвращает события для указанной страницы"""
    result = await session.execute(
        select(Event)
        .where(Event.category == 'competition')
        .where(Event.status == 'active')
        .order_by(Event.published_at.desc())
        .offset((page-1)*per_page)
        .limit(per_page)
    )
    return result.scalars().all()


async def get_event_by_id(
        session: AsyncSession,
        event_id: int,
        ) -> Event | None:
    """Возвращает событие по ID"""
    result = await session.execute(
        select(Event)
        .where(Event.id == event_id)
        .where(Event.status == 'active')
    )
    return result.scalars().first()


async def get_user_by_telegram_id(telegram_id: int) -> User | None:
    """Возвращает пользователя по Telegram ID"""
    async with get_async_session() as session:
        result = await session.execute(
            select(User)
            .where(User.telegram_id == telegram_id)
            .options(selectinload(User.admin_role))
        )
        return result.scalar_one_or_none()

# endregion

# region Вспомогательные функции

def calculate_total_pages(
        total_items: int,
        per_page: int,
        ) -> int:
    """Вычисляет общее количество страниц"""
    return max(1, (total_items + per_page - 1) // per_page)


def normalize_page_number(page: int, total_pages: int) -> int:
    """Нормализует номер страницы"""
    return max(1, min(page, total_pages))


async def send_event_list_message(
    callback: types.CallbackQuery,
    state: FSMContext,
    events: list[Event],
    page: int,
    total_pages: int
):
    """Формирует и отправляет сообщение со списком событий"""
    # Формируем текст сообщения
    message_text = (
        f"🏆 Активные соревнования (Страница {page}/{total_pages}):\n\n" +
        "\n".join(
            f"<b>{event.title}</b> - {event.published_at.strftime('%Y-%m-%d')}"
            for event in events
        )
    )

    # Создаем клавиатуру
    keyboard = build_event_list_keyboard(events, page, total_pages)

    # Отправляем сообщение
    try:
        if page == 1:
            await callback.message.delete()
    except Exception as e:
        logger.warning(f"Не удалось удалить сообщение: {e}")

    msg = await callback.message.answer(
        message_text,
        reply_markup=keyboard,
        parse_mode='HTML'
    )

    # Сохраняем состояние
    await state.update_data(
        current_page=page,
        total_pages=total_pages,
        message_id=msg.message_id
    )


async def send_event_content(callback: types.CallbackQuery, event: Event):
    """Отправляет контент события (текст + медиа)"""
    message_text = (
        f"<b>{event.title}</b>\n"
        f"{event.content}\n\n"
        f"Дата: {event.published_at.strftime('%Y-%m-%d')}"
    )

    if event.images and isinstance(event.images, list) and event.images:
        try:
            await callback.message.answer_photo(
                photo=event.images[0],
                caption=message_text,
                parse_mode='HTML'
            )
            return
        except Exception as e:
            logger.error(f"Ошибка отправки фото: {e}")

    await callback.message.answer(message_text, parse_mode='HTML')


async def send_back_button(
        callback: types.CallbackQuery,
        state: FSMContext
        ):
    """Отправляет кнопку возврата к списку"""
    state_data = await state.get_data()
    current_page = state_data.get('current_page', 1)
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[
        types.InlineKeyboardButton(
            text="🔙 Вернуться к списку",
            callback_data=f"back_to_list_{current_page}"
        )
    ]])
    
    await callback.message.answer(
        "Подробности события",
        reply_markup=keyboard
    )

async def save_event_view_state(
        state: FSMContext,
        event_id: int
        ):
    """Сохраняет состояние просмотра события"""
    await state.update_data(
        selected_event_id=event_id,
        viewing_mode='details'
    )

# endregion