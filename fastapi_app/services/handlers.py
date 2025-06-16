from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession


from .keyboards import QUIZZES_STAGE_INTERN

router_quizzes = Router()


class QuizState(StatesGroup):
    """Класс состояний FSM для управления процессом прохождения тестов."""

    MENU = State()
    PROGRESS = State()
    PREVIOUS_STEP = State()


@router_quizzes.message(Command('hi'))
async def intern_stage_quizzes_test_command(
    message: types.Message,
    state: FSMContext,
) -> None:
    """Обработчик команды /hi для начала тестирования."""
    await message.answer(
        'Выберети ваши дальнейшие действия.\n'
        'Выберете нужное вам меню.',
        reply_markup=QUIZZES_STAGE_INTERN,
    )
    await message.delete()
