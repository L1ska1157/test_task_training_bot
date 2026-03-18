from sqlalchemy import select, delete
from sqlalchemy.orm import Session
import logging
import datetime

from database.db import *
from database.models import *


def create_tables():
    logging.info('Creating tables')
    metadata.create_all(engine)
    

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
    

def add_exercise(training_id: int, exr_text: str):
    with ses_factory() as ses:
        exr_list = exr_text.split('|') # => ['name', 'reps', 'sets', 'weight']
        new_exr = Exercise(
            name = exr_list[0],
            reps = int(exr_list[1]),
            sets = int(exr_list[2]),
            weight = exr_list[3] if exr_list[3] else None,
            training_id = training_id
        )
            
        ses.add(new_exr)
        ses.commit()
        
        logging.info(f'Added exercise {new_exr}')
        

def set_training_duration(training_id: int, duration: datetime.timedelta):
    with ses_factory() as ses:
        training = ses.get(Training, training_id)
        training.duration = duration
        ses.commit()
        
        logging.info(f'Changed duration of {training} to {duration}')


def get_info_about_training(training_id: int):
    with ses_factory() as ses:
        training = ses.get(Training, training_id)
        
        logging.info(f'Give info about training {training}')
        
        return {
            'exercises': training.exr,
            'duration': training.duration
        }


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
    

def get_training_dates(user_id: int):
    with Session(engine) as ses:
        stmt = (
            select(Training.date, Training.id)
            .where(
                Training.user == user_id
            )
        )
        
        user_training_dates = ses.execute(stmt).all()
        
        return user_training_dates


def delete_old_trainings():
    end_date = datetime.datetime.now().date() - datetime.timedelta(weeks=5)
    with Session(engine) as ses:
        stmt = (
            delete(Training)
            .where(
                Training.date < end_date
            )
        )
        ses.execute(stmt)