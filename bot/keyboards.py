from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


base_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Старт')],
        [KeyboardButton(text='Історія'), KeyboardButton(text='Прогрес')]
    ],
    resize_keyboard=True,
    input_field_placeholder='Щоб почати тренування, натисніть кнопку старт'
)

stop_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Стоп')],
    ],
    resize_keyboard=True,
    input_field_placeholder='Введіть інформацію про виконану вправу'
)


async def history_kb(training_dates):
    keyboard = InlineKeyboardBuilder()
    for date, id in training_dates:
        keyboard.add(InlineKeyboardButton(
            text=str(date),
            callback_data=str(id)
            ))
    return keyboard.adjust(1).as_markup()


async def progress_kb(exercise_names):
    keyboard = InlineKeyboardBuilder()
    for exr in exercise_names:
        keyboard.add(InlineKeyboardButton(
            text=exr,
            callback_data=exr
            ))
    return keyboard.adjust(1).as_markup()