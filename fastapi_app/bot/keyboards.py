from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_inline_keyboard(
        *buttons: tuple[str, str],
        sizes: tuple[int, ...] = (2,),
        placeholder: str = None,
        url_buttons: tuple[tuple[str, str]] = None,
) -> InlineKeyboardMarkup:
    """Универсальная функция для создания inline-клавиатуры.

    В функцию передаются:
        buttons: Кортеж пар (текст кнопки, callback_data).
        sizes: Кортеж размеров рядов кнопок
        (например, (2, 1) для 2 кнопки в первом ряду, 1 во втором).
        placeholder: Текст для поля ввода (опционально).
        url_buttons: Кортеж пар (текст кнопки, URL)
        для кнопок с внешними ссылками.
    """
    keyboard = InlineKeyboardBuilder()

    for text, callback_data in buttons:
        keyboard.add(InlineKeyboardButton(text=text,
                                          callback_data=callback_data))

    if url_buttons:
        for text, url in url_buttons:
            keyboard.add(InlineKeyboardButton(text=text,
                                              url=url))

    return keyboard.adjust(*sizes).as_markup(
        resize_keyboard=True,
        input_field_placeholder=placeholder,
    )


def get_main_menu_keyboard(is_admin: bool) -> InlineKeyboardMarkup:
    """Создает главную клавиатуру с учетом статуса администратора.

    Args:
        is_admin (bool): Флаг, указывающий, является ли пользователь администратором.

    Returns:
        InlineKeyboardMarkup: Сформированная клавиатура.
    """
    keyboard = InlineKeyboardBuilder()

    # Базовые кнопки для всех пользователей
    buttons = [
        ('Соревнования', 'competition'),
        ('Мероприятия', 'event'),
        ('Записать ребенка в секцию', 'child_reg'),
        ('Организация соревнований', 'org_of_comps'),
    ]

    # Добавляем кнопку "Администратор", если пользователь админ
    if is_admin:
        buttons.append(('Администратор', 'admin'))

    # Добавляем кнопки в клавиатуру
    for text, callback_data in buttons:
        keyboard.add(InlineKeyboardButton(text=text, callback_data=callback_data))

    # Добавляем кнопки с URL для всех пользователей
    url_buttons = [
        ('Посетить сайт федерации', 'https://wrestrus90.ru'),
        ('Посетить страничку VKontakte', 'https://vk.com/fsbmytishchi'),
    ]
    for text, url in url_buttons:
        keyboard.add(InlineKeyboardButton(text=text, url=url))

    # Настраиваем размеры рядов
    sizes = (2, 1, 1, 1) if not is_admin else (2, 1, 1, 1, 1)

    return keyboard.adjust(*sizes).as_markup(
        resize_keyboard=True,
    )
