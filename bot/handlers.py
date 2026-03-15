from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.enums.parse_mode import ParseMode
from aiogram import F, Router
import logging
import datetime

from .keyboards import *
from .states import *

router = Router()

# /start
@router.message(Command('start'))
async def start(message: Message):
    await message.answer(
        text='Привіт! Я зручний бот для відслідковування твого прогресу у тренуваннях. Щоб розпочати тренування, натисни кнопку старт',
        reply_markup=base_keyboard
    )
    logging.info(f'User {message.from_user.username} command /start')


# /help
@router.message(Command('help'))
async def help(message: Message):
    logging.info(f'User {message.from_user.username} command /help')
    await message.answer(
        text='''
• <b>Старт</b> - розпочати тренування. Далі ти можеш надсилати текстовим або голосовим повідомленням яку вправу ти зробив(ла) і я її збережу
• <b>Стоп</b> - завершить твоє тренування, закріпивши всі додані вправи за цим тренуванням. Також ти побачиш всі вправи, зроблені за це тренування
• <b>Історія</b> - історія твоїх тренувань за останній місяць. Просто обери дату тренування зі списку і я покажу всі вправи які ти зробив(ла) тоді 
• <b>Прогрес</b> - статистика по 1 конкретній вправі. Обери вправу зі списку та побачиш свій прогрес у її виконанні за останній місяць
        
<i>Примітка: будь ласка, вказуй однакову назву для однакових вправ, інакше вони будуть розглядатись як 2 різні вправи</i>
        ''',
        parse_mode=ParseMode.HTML,
        reply_markup=base_keyboard
    )
    pass


# 'Старт'
@router.message(F.text == 'Старт')
async def start_training(message: Message, state: FSMContext):
    await state.set_state(States.training)
    # TODO save new training to db, get it's id
    await state.update_data(start_time = datetime.datetime.now(), training_id = None) #training id from db
    await message.answer(
        text='Відправте голосове або текстове повідомлення з інформацією про виконану вправу. Щоб завершити тренування натисніть Стоп',
        reply_markup=stop_keyboard
    )

# 'Стоп'
@router.message(F.text == 'Стоп', States.training) 
async def stop_training(message: Message, state: FSMContext):
    data = await state.get_data() # for training id
    await state.clear()
    duration = datetime.datetime.now() - data['start_time']
    # data = get_exr_from_training() - func from database.func
    # TODO send info about training from data
    await message.answer(
        text = f'*Training info* duration: {duration}',
        reply_markup = base_keyboard
    )


@router.message(F.text, States.training)
async def add_exercise(message: Message, state: FSMContext):
    # TODO text exercise messages logic, adding to db
    await message.answer(
        text = f'Exr to add'
    )


@router.message(F.voice, States.training)
async def voice_message(message: Message, state: FSMContext):
    # TODO voice messages logic
    await message.answer(
        text='Voice message to process'
    )
    add_exercise(message=message, state=state)


@router.message(F.text == "Історія тренувань", StateFilter(state=None))
async def history(message: Message, state: FSMContext):
    await state.set_state(States.choose_date)
    # TODO trainings = get_trainings(user_id = message.from_user.user_id)
    trainings = ['tr1', 'tr2']
    keyboard = history_kb(trainings=trainings)
    message.answer(
        text='Оберіть дату тренування:',
        reply_markup=keyboard
    )


@router.message(F.text == "Прогрес", StateFilter(state=None))
async def progress(message: Message):
    #send keyboard with different types of exercises that this person did
    pass


@router.callback_query(F.data) # + state
async def training_from_history(callback: CallbackQuery):
    #show training that user choosed
    pass


@router.callback_query(F.data) # + state
async def get_progress(callback: CallbackQuery):
    # show progress for choosen exercise
    pass


@router.message() 
async def message_while_not_training(message: Message): 
    # send message that you need to start training before adding exercises
    pass




