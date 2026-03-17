# add new training
# add new exercise
# change duration of training
# get all exercises from 1 training get_exr_from_training(training_id = data['training_id'])
# get all exercise names for 1 user 
# get data for 1 exercise get_exr_statistic(exr_name: str, user_id: int)
# delete all trainings older then 1 month

from sqlalchemy import URL, create_engine, text, insert, select, update, func, cast, Integer, and_
from sqlalchemy.orm import aliased, joinedload, selectinload, contains_eager
import logging
import datetime

from database.db import *
from database.models import *


# * Ready
def create_tables():
    logging.info('Creating tables')
    metadata.create_all(engine)
    

# * Ready
def add_training(user_id: int): 
    with ses_factory() as ses:
        new_training = Training(
            date = datetime.datetime.now().date(),
            user = user_id
        )
        ses.add(new_training)
        ses.commit()
        
        logging.info(f'Added training {new_training}')
        return new_training.id
    
    
    

# * Ready
def add_exercise(training_id: int, exr_text: str):
    with ses_factory() as ses:
        exr_list = exr_text.split('|') # => ['name', 'reps', 'sets', 'weight']
        new_exr = Exercise(
            name = exr_list[0],
            reps = int(exr_list[1]),
            sets = int(exr_list[2]),
            training_id = training_id
        )
        if len(exr_list) > 3:
            new_exr.weight = exr_list[3]
            
        ses.add(new_exr)
        ses.commit()
        
        logging.info(f'Added exercise {new_exr}')
        


# TODO
def set_training_duration(training_id: int):
    pass


# TODO
def get_exr_from_training(training_id: int):
    pass


# TODO
def get_exr_list(user_id: int):
    pass


# TODO
def get_exr_statistic(exr_name: str, user_id: int):
    pass


# TODO
def get_trainings_dates(user_id: int):
    pass


# TODO
def get_training_data(training_id: int):
    pass


# TODO
def delete_old_trainings():
    pass