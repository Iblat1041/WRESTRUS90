from bot.keyboards import get_inline_keyboard


QUIZZES_STAGE_INTERN = get_inline_keyboard(
    ('Записаться на занятие', 'start_training'),
    ('Назад', 'back'),
    ('Меню', 'intern_menu'),
    sizes=(1, 2),
)