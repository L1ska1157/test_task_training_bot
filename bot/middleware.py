from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message
import logging

from bot.states import States
from database.func import add_exercise


class MiddlewareSaveExercise(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any] 
    ):
        
        state = data.get('state')
        if state:
            current_state = await state.get_state()
            
            if current_state == States.training.state:
                state_data = await state.get_data()
                try: 
                    exr_saved_message = state_data['exr_saved_message']
                    exr_text = state_data['exr_text']
                    training_id = state_data['training_id']

                    add_exercise(
                        training_id=training_id,
                        exr_text=exr_text
                    )
                    logging.info('Message parsed correctly. Saving...')
                    
                    await exr_saved_message.edit_reply_markup(None)
                    await state.update_data(exr_saved_message = None)
                except KeyError as e:
                    logging.info('First exercise in training')
                except Exception as e:
                    logging.error(e)
        
        return await handler(event, data)