import logging
from typing import Any, Dict
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InputMediaPhoto
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_async_session
from services.event_handl.keyboards import build_event_list_keyboard
from bot.keyboards import get_main_menu_keyboard
from services.models import Event, User
from crud.events import CRUDEvents
from crud.users import CRUDUsers  # Предполагаемый импорт

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

event_router = Router()

# Инициализация CRUD-объектов
events_crud = CRUDEvents(Event)
users_crud = CRUDUsers(User)  # Предполагается, что класс CRUDUsers существует

class EventState(StatesGroup):
    """Состояния FSM для работы с событиями"""
    START_EVENT = State()      # Состояние просмотра списка событий
    DETAILS_EVENT = State()    # Состояние просмотра деталей события
    current_page = State()     # Tекущая страница пагинации
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
    session: AsyncSession,
    **kwargs: Any  # Добавляем kwargs для получения данных из middleware
) -> None:
    """Обработчик возврата в главное меню"""
    try:
        # Получаем данные из kwargs (переданные middleware)
        data = kwargs.get('data', {})
        
        # Если пользователя нет в данных, пробуем получить его из БД
        if not data.get('user'):
            user = await users_crud.get_user_by_telegram_id(
                session=session,
                telegram_id=callback.from_user.id
            )
            if user:
                data['user'] = user
                data['is_admin'] = hasattr(user, 'admin_role') and user.admin_role is not None

        await return_to_main_menu(callback, state, data)
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка возврата в меню: {e}", exc_info=True)
        await callback.message.answer("Произошла ошибка. Попробуйте позже.")
        await callback.answer()

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
            # Получаем общее количество активных соревнований
            total_events = await events_crud.get_total_active_competitions(session)
            if not total_events:
                await callback.answer("Нет активных соревнований.", show_alert=True)
                return

            # Вычисляем параметры пагинации
            total_pages = calculate_total_pages(total_events, events_per_page)
            page = normalize_page_number(page, total_pages)
            
            # Получаем события для страницы
            current_events = await events_crud.get_all_events(
                session=session,
                offset=(page - 1) * events_per_page,
                limit=events_per_page,
                category="competition",
                status="active"
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
            event = await events_crud.get_event_by_id(session, event_id)
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
    state: FSMContext,
    data: Dict[str, Any]
) -> None:
    """Возвращает пользователя в главное меню"""
    try:
        await state.clear()
        
        user = data.get("user")
        is_admin = data.get("is_admin", False)

        if not user:
            logger.warning(f"Пользователь с Telegram ID {callback.from_user.id} не найден")
            await callback.message.answer(
                "Добро пожаловать! Пожалуйста, зарегистрируйтесь для доступа к функциям бота."
            )
            return

        logger.debug(f"Возврат в меню для пользователя {user.id}, is_admin={is_admin}")
        
        await callback.message.answer(
            f"Привет, {user.name if user else 'пользователь'}! Добро пожаловать!",
            reply_markup=get_main_menu_keyboard(is_admin=is_admin)
        )
        
        try:
            await callback.message.delete()
        except Exception as delete_error:
            logger.warning(f"Не удалось удалить сообщение: {delete_error}")
            
    except Exception as e:
        logger.error(f"Ошибка возврата в меню: {e}", exc_info=True)
        raise

# endregion

# region Вспомогательные функции

def calculate_total_pages(
    total_items: int,
    per_page: int,
) -> int:
    """Вычисляет общее количество страниц"""
    return max(1, (total_items + per_page - 1) // per_page)


def normalize_page_number(
    page: int,
    total_pages: int
) -> int:
    """Нормализует номер страницы"""
    return max(1, min(page, total_pages))


async def send_event_list_message(
    callback: types.CallbackQuery,
    state: FSMContext,
    events: list[Event],
    page: int,
    total_pages: int
) -> None:
    """Формирует и отправляет сообщение со списком событий."""
    # Максимальная длина заголовка события
    max_title_length = 30

    # Формируем текст сообщения
    message_text = (
        f"🏆 Активные соревнования (Страница {page}/{total_pages}):\n\n" +
        "\n".join(
            f"Пост № <b>{event.id}</b>. <b>{event.title[:max_title_length].capitalize()}"
            f"{'...' if len(event.title) > max_title_length else ''}</b> - "
            f"{event.published_at.strftime('%Y-%m-%d')}"
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


async def send_event_content(
    callback: types.CallbackQuery,
    event: Event
):
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
        "Вернуться к событиям",
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