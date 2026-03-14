from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram import F, Router

import keyboards as kb
from states import *

router = Router()


@router.message(Command('start'))
async def start(message: Message):
    # send hello and expleining message
    pass


@router.message(Command('help'))
async def help(message: Message):
    #send explainig message (same as start but without hello)
    pass


@router.message(F.text == 'Старт')
async def start_training(message: Message, state: FSMContext):
    #change state, change keyboard, create new training in db
    pass


@router.message(F.text == 'Стоп') # + state
async def stop_training(message: Message, state: FSMContext):
    #change state, save training duration, change keyboard
    pass


@router.message(F.text) # + state
async def add_exercise(message: Message, state: FSMContext):
    # add exercise to db and cash
    pass


@router.message(F.voice) # + state
async def voice_message(message: Message, state: FSMContext):
    #voice message to text, then the same as with text message
    pass


@router.message(F.text == "Історія тренувань")
async def history(message: Message):
    #send keyboard with trainings
    pass


@router.message(F.text == "Прогрес")
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




