from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.enums.parse_mode import ParseMode
from aiogram import F, Router, Bot
import logging
import datetime
from speech_recognition import UnknownValueError, RequestError

from bot.keyboards import *
from bot.states import *
from bot.func import format_exercise, voice_to_text, get_training_info_message
from database.func import *

router = Router()


# /start
@router.message(Command('start'), ~StateFilter(States.training))
async def start(message: Message):
    logging.info(f'User {message.from_user.username} command /start')
    
    await message.answer(
        text='Привіт! Я зручний бот для відслідковування вашого прогресу у тренуваннях. Щоб розпочати тренування, натисніть кнопку старт',
        reply_markup=base_keyboard
    )
    

# /help
@router.message(Command('help'))
async def help(message: Message):
    logging.info(f'User {message.from_user.username} command /help')
    
    await message.answer(
        text='''
• <b>Старт</b> - розпочати тренування. Далі ви можете надсилати текстовим або голосовим повідомленням яку вправу ви зробили і я її збережу
• <b>Стоп</b> - завершити тренування, закріпивши всі додані вправи за цим тренуванням. Також ви побачите всі вправи, зроблені за це тренування
• <b>Історія</b> - історія ваших тренувань за останній місяць. Просто оберіть дату тренування зі списку і я покажу всі вправи які ви зробили тоді 
• <b>Прогрес</b> - статистика по 1 конкретній вправі. Оберіть вправу зі списку та побачите свій прогрес у її виконанні за останній місяць
        
<i>Примітка: будь ласка, вказуйте однакову назву для однакових вправ, інакше вони будуть розглядатись як 2 різні вправи</i>
        ''',
        parse_mode=ParseMode.HTML,
        reply_markup=base_keyboard
    )
    pass


# 'Старт'
@router.message(F.text == 'Старт', ~StateFilter(States.training))
async def start_training(message: Message, state: FSMContext):
    logging.info(f'User {message.from_user.username} text \'Старт\'')
    
    await state.set_state(States.training)
    
    training_id = add_training(message.from_user.id)
    await state.update_data(start_time = datetime.datetime.now(), training_id = training_id) 
    
    await message.answer(
        text='Відправте голосове або текстове повідомлення з інформацією про виконану вправу. Щоб завершити тренування, натисніть Стоп',
        reply_markup=stop_keyboard
    )


# 'Стоп'
@router.message(F.text == 'Стоп', States.training) 
async def stop_training(message: Message, state: FSMContext):
    logging.info(f'User {message.from_user.username} text \'Стоп\'')
    
    data = await state.get_data()
    await state.clear()
    
    duration = datetime.datetime.now() - data['start_time']
    set_training_duration(
        training_id = data['training_id'], 
        duration = duration
        )
    
    training_info = get_info_about_training(
        training_id=data['training_id']
    )
    
    mes = get_training_info_message(
        base_mes = 'Підсумок сьогоднішнього тренування:\n',
        training_info = training_info
    )
    
    await message.answer(
        text = mes,
        reply_markup = base_keyboard
    )


# Text message
@router.message(F.text, States.training)
async def text_exercise(message: Message, state: FSMContext):
    logging.info(f'User {message.from_user.username} text \'{message.text}\'')
    
    temp_message = await message.answer(
        text='⏳',
        reply_markup=ReplyKeyboardRemove()
    )

    try:
        formatted_exr = format_exercise(message.text)
        
        if formatted_exr == 'error':
            await message.answer(
                text='Вибачте, я не зрозумів(',
                reply_markup=stop_keyboard
            )
        else:
            state_data = await state.get_data()
            add_exercise(
                training_id = state_data['training_id'],
                exr_text = formatted_exr
            )
            await message.answer(
                text='Вправу додано ✔️',
                reply_markup=stop_keyboard
        )
    except:
        await message.answer(
            text='Ой, щось пішло не так...',
            reply_markup=stop_keyboard
        )
    
    await temp_message.delete()
    

# Voice message
@router.message(F.voice, States.training)
async def voice_exercise(message: Message, bot: Bot, state: FSMContext): 
    logging.info(f'User {message.from_user.username} voice message')
    
    temp_message = await message.answer(
        text='⏳',
        reply_markup=ReplyKeyboardRemove()
    )
    
    try: 
        audio_text = await voice_to_text(message.voice.file_id, bot)
    
    except UnknownValueError:
        logging.info('Couldn\'t recognise text on this audio')
        await message.answer(
            text='Вибачте, я не зрозумів що ви сказали',
            reply_markup=stop_keyboard
        )
    
    except RequestError as e:
        logging.error("Could not request results from Google Speech Recognition service; {0}".format(e))
        await message.answer(
            text='Ой, щось пішло не так...',
            reply_markup=stop_keyboard
        )
        
    formatted_exr = format_exercise(audio_text)
    
    if formatted_exr == 'error':
        await message.answer(
            text='Вибачте, я не зрозумів',
            reply_markup=stop_keyboard
        )
    else:
        data = await state.get_data()
        add_exercise(
            training_id = data['training_id'],
            exr_text = formatted_exr
        )
        await message.answer(
            text='Вправу додано ✔️',
            reply_markup=stop_keyboard
        )
        
    await temp_message.delete()
    

# 'Історія'
@router.message(F.text == "Історія", ~StateFilter(States.training))
async def history(message: Message, state: FSMContext):
    logging.info(f'User {message.from_user.username} text \'Історія\'')
    
    await state.set_state(States.choose_date)
    
    training_dates = get_training_dates(
        user_id = message.from_user.id
    )
    if training_dates:
        keyboard = await history_kb(
            training_dates = training_dates
        )
        
        kb_message = await message.answer(
            text='Оберіть дату тренування:',
            reply_markup=keyboard
        )
        
        await state.update_data(kb_message_id=kb_message.message_id)
    else: 
        await message.answer(
            text='Ви ще не додали жодного тренування\nЩоб розпочати тренування, натисніть Старт',
            reply_markup=base_keyboard
        )


# 'Прогрес'
@router.message(F.text == "Прогрес", ~StateFilter(States.training))
async def progress(message: Message, state: FSMContext):
    logging.info(f'User {message.from_user.username} text \'Прогрес\'')
    
    await state.set_state(States.choose_exr)
    
    exercise_names = get_exr_list(message.from_user.id)
    
    if exercise_names:
        keyboard = await progress_kb(exercise_names) 
    
        kb_message = await message.answer(
            text='Оберіть вправу:',
            reply_markup=keyboard
        )

        await state.update_data(kb_message_id=kb_message.message_id)
    
    else:
        await message.answer(
            text='Ви ще не додали жодної вправи\nЩоб розпочати тренування, натисніть Старт',
            reply_markup=base_keyboard
        )
    

# Back
@router.callback_query(F.data == '<=')
async def back(callback: CallbackQuery, state: FSMContext):
    logging.info('Back')
    
    await callback.message.edit_reply_markup(None)
    await state.clear()
    
    await callback.message.answer(
        text = 'Повертаюся...',
        reply_markup=base_keyboard
    )

# Choosed training date
@router.callback_query(F.data, States.choose_date)
async def training_from_history(callback: CallbackQuery, state: FSMContext):
    logging.info(f'User {callback.from_user.username} choosed training {callback.data}')
    
    await callback.message.edit_reply_markup(None)
    await state.clear()
    
    training = get_info_about_training(int(callback.data))
    mes = get_training_info_message('', training)
    
    await callback.message.answer(
        text = mes,
        reply_markup=base_keyboard
    )
    

# Choosed exercise
@router.callback_query(F.data, States.choose_exr)
async def get_progress(callback: CallbackQuery, state: FSMContext):
    logging.info(f'User {callback.from_user.username} choosed exercise {callback.data}')
    
    await callback.message.edit_reply_markup(None)
    await state.clear()
    
    exr_name = callback.data
    user_id = callback.from_user.id
    
    exercise_statistic = get_exr_statistic(
        exr_name = exr_name, 
        user_id = user_id)
    
    mes = f'Статистика по вправі {exr_name}: '
    
    for exr, date in exercise_statistic:
        mes += f'\n{date}:{f' {exr.weight} кг' if exr.weight else ''} {exr.sets} підх. по {exr.reps} р.'
        # Дата: вага(якщо є) n підх. по k р.
        
    await callback.message.answer(
        text = mes,
        reply_markup=base_keyboard
    ) 


# Message out of training
@router.message(~StateFilter(States.training)) 
async def message_out_of_training(message: Message): 
    logging.info('Message out of training')
    
    await message.answer(
        text='Щоб розпочати тренування, натисніть старт',
        reply_markup=base_keyboard
    )




