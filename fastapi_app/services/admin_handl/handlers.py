from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from bot.logger import logger
from constants_kb.admin import (
    MAIN_MENU_ADMIN,
    )

from services.admin_handl.keyboards import (
    ADMIN_USERS_MENU,
    )

from core.db import get_async_session
from crud.users import users_crud

from .keyboards import (
    get_users_list_keyboard,
)

admin_router = Router()


class StartState(StatesGroup):
    """Стартовый стэйт."""

    START_ADMIN = State()
    USERS = State()


@admin_router.callback_query(F.data == 'admin')
async def handle_admin_menu(
    callback: types.CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    """Обрабатывает нажатие кнопки 'Администратор'."""
    await state.set_state(StartState.START_ADMIN)

    await callback.message.edit_text(MAIN_MENU_ADMIN,
                                     reply_markup=ADMIN_USERS_MENU)
    await callback.answer()


@admin_router.callback_query(F.data == 'users_list')
async def show_users_list(
    callback: types.CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    data = await state.get_data()
    page = data.get('current_page', 0)
    per_page = 5

    async with get_async_session() as session:
        users = await users_crud.get_all_users(
            session,
            offset=page * per_page,
            limit=per_page,
        )
        total_users = await users_crud.get_users_count(session)

    keyboard = get_users_list_keyboard(users, page, total_users, per_page)

    await state.update_data(
        current_menu='users_list',
        current_page=page,
    )
    await callback.message.edit_text(
        ('Выберите необходимого пользователя для изменения его профиля. \n \n'
         f'Список пользователей (страница {page + 1}):'),
        reply_markup=keyboard,
    )
    await callback.answer()

