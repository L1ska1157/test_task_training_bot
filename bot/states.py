from aiogram.fsm.state import StatesGroup, State

class States(StatesGroup): 
    choose_date = State() 
    choose_exr = State()
    training = State()