# add new training
# add new exercise
# change duration of training
# get all exercises from 1 training get_exr_from_training(training_id = data['training_id'])
# get all exercise names for 1 user 
# get data for 1 exercise get_exr_statistic(exr_name: str, user_id: int)
# delete all trainings older then 1 month

from sqlalchemy import URL, create_engine, text, insert, select, update, func, cast, Integer, and_, delete
from sqlalchemy.orm import aliased, joinedload, selectinload, contains_eager, Session
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
        

# * Ready
def set_training_duration(training_id: int, duration: datetime.timedelta):
    with ses_factory() as ses:
        training = ses.get(Training, training_id)
        training.duration = duration
        ses.commit()
        
        logging.info(f'Changed duration of {training} to {duration}')


# * Ready
def get_info_about_training(training_id: int):
    with ses_factory() as ses:
        training = ses.get(Training, training_id)
        
        logging.info(f'Give info about training {training}')
        
        return {
            'exercises': training.exr,
            'duration': training.duration
        }


# * Ready
def get_exr_list(user_id: int):
    with Session(engine) as ses:
        stmt = (
            select(Exercise.name)
            .join(Training, Exercise.training_id == Training.id)
            .filter(Training.user == user_id)
            .distinct()
        )
    exercise_names = ses.execute(stmt).scalars().all()
    
    logging.info(f'Got exercise names {exercise_names} for user {user_id}')
    
    return exercise_names


# * Ready
def get_exr_statistic(exr_name: str, user_id: int):
    with Session(engine) as ses:
        stmt = (
                select(Exercise, Training.date)
                .join(Training, Exercise.training_id == Training.id)
                .where(
                    Training.user == user_id,
                    Exercise.name == exr_name
                    )
            )
        exercise_statistic = ses.execute(stmt).all()
        
        logging.info(f'Got exercises({len(exercise_statistic)}) with name {exr_name} for user {user_id}')

        return exercise_statistic
    

# * Ready
def get_training_dates(user_id: int):
    with Session(engine) as ses:
        stmt = (
            select(Training.date, Training.id)
            .where(
                Training.user == user_id
            )
        )
        
        user_training_dates = ses.execute(stmt)
        
        return user_training_dates


# TODO
def delete_old_trainings():
    end_date = datetime.datetime.now().date() - datetime.timedelta(weeks=5)
    with Session(engine) as ses:
        stmt = (
            delete(Training)
            .where(
                Training.date < end_date
            )
        )