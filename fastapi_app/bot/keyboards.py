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
