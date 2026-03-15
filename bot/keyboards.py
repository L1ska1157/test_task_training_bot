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
        [KeyboardButton(text='Стоп')]
    ],
    resize_keyboard=True
)

async def history_kb(trainings):
    keyboard = InlineKeyboardBuilder()
    for training in trainings:
        keyboard.add(InlineKeyboardButton(
            text=training,
            callback_data=training
            )) # text=training.date, callback_data=training.id
    return keyboard.as_markup()


async def progress_kb(user_id: int):
    keyboard = InlineKeyboardBuilder()
    exercises = ['exr1', 'exr2'] # get all trainings from this user
    for exr in exercises:
        keyboard.add(InlineKeyboardButton(
            text=exr,
            callback_data=exr
            )) # text=exr.name, callback_data=exr.id
    return keyboard.as_markup()