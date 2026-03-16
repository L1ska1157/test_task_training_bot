from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.enums.parse_mode import ParseMode
from aiogram import F, Router
import logging
import datetime

from .keyboards import *
from .states import *
from .func import format_exercise

router = Router()


# * Ready
# /start
@router.message(Command('start'), StateFilter(None))
async def start(message: Message):
    logging.info(f'User {message.from_user.username} command /start')
    
    await message.answer(
        text='Привіт! Я зручний бот для відслідковування твого прогресу у тренуваннях. Щоб розпочати тренування, натисни кнопку старт',
        reply_markup=base_keyboard
    )
    

# * Ready
# /help
@router.message(Command('help'), StateFilter(None))
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


# TODO database.func
# 'Старт'
@router.message(F.text == 'Старт', StateFilter(None))
async def start_training(message: Message, state: FSMContext):
    logging.info(f'User {message.from_user.username} text \'Старт\'')
    
    await state.set_state(States.training)
    
    # TODO save new training to db, get it's id
    await state.update_data(start_time = datetime.datetime.now(), training_id = None) #training id from db
    
    await message.answer(
        text='Відправте голосове або текстове повідомлення з інформацією про виконану вправу. Щоб завершити тренування натисніть Стоп',
        reply_markup=stop_keyboard
    )


# TODO database.func
# TODO display info
# 'Стоп'
@router.message(F.text == 'Стоп', States.training) 
async def stop_training(message: Message, state: FSMContext):
    logging.info(f'User {message.from_user.username} text \'Стоп\'')
    
    data = await state.get_data() # for training id
    await state.clear()
    
    duration = datetime.datetime.now() - data['start_time']
    # data = get_exr_from_training(training_id = data['training_id']) - func from database.func
    # TODO send info about training from data
    
    await message.answer(
        text = f'*Training info* duration: {duration}',
        reply_markup = base_keyboard
    )


# TODO bot.func
# TODO database.func
# Text message
@router.message(F.text, States.training)
async def text_exercise(message: Message, state: FSMContext):
    logging.info(f'User {message.from_user.username} text \'{message.text}\'')
    
    exercise = format_exercise(message.text)
    
    # TODO add exercise to db
    await message.answer(
        text = exercise,
        reply_markup=stop_keyboard
    )


# TODO voice message (bot.func or here)
# Voice message
@router.message(F.voice, States.training)
async def voice_exercise(message: Message, state: FSMContext):
    logging.info(f'User {message.from_user.username} voice message')
    
    # TODO voice messages logic
    # TODO text formating
    await message.answer(
        text='Voice message to process',
        reply_markup=stop_keyboard
    )
    

# TODO database.func
# TODO change keyboard (bot.keyboards)
# 'Історія'
@router.message(F.text == "Історія", StateFilter(None))
async def history(message: Message, state: FSMContext):
    logging.info(f'User {message.from_user.username} text \'Історія\'')
    
    await state.set_state(States.choose_date)
    
    # TODO trainings = get_trainings(user_id = message.from_user.id)
    trainings = ['tr1', 'tr2']
    keyboard = await history_kb(trainings=trainings)
    
    await message.answer(
        text='Оберіть дату тренування:',
        reply_markup=keyboard
    )


# TODO database.func
# TODO Change keyboard (bot.keyboards)
# 'Прогрес'
@router.message(F.text == "Прогрес", StateFilter(None))
async def progress(message: Message, state: FSMContext):
    logging.info(f'User {message.from_user.username} text \'Прогрес\'')
    
    await state.set_state(States.choose_exr)
    
    # TODO keyboard = get_exercise_names(message.from_user.id)
    keyboard = await progress_kb(['exr1', 'exr2']) 
    
    await message.answer(
        text='Оберіть вправу:',
        reply_markup=keyboard
    )


# TODO database.func
# TODO display
# Choosed training date
@router.callback_query(F.data, States.choose_date)
async def training_from_history(callback: CallbackQuery, state: FSMContext):
    logging.info(f'User {callback.from_user.username} choosed training {callback.data}')
    
    await state.clear()
    
    # TODO training = get_training(int(callback.data))
    # TODO display training
    mes = '*training info*'
    
    await callback.message.edit_reply_markup(None)
    await callback.message.answer(
        text = mes
    )
    

# TODO database.func
# TODO display
# Choosed exercise
@router.callback_query(F.data, States.choose_exr)
async def get_progress(callback: CallbackQuery, state: FSMContext):
    logging.info(f'User {callback.from_user.username} choosed exercise {callback.data}')
    
    await state.clear()
    
    # TODO exercise = get_exr_statistic(callback.data, callback.message.from_user.id)
    # TODO display exercise statistic
    mes = '*exr info*'
    
    await callback.message.edit_reply_markup(None)
    await callback.message.answer(
        text = mes
    ) 


# * Ready
# Message out of training
@router.message(StateFilter(None)) 
async def message_out_of_training(message: Message): 
    logging.info('Message out of training')
    
    await message.answer(
        text='Щоб розпочати тренування, натисніть старт'
    )




