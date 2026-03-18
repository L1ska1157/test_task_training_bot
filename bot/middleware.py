from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, CallbackQuery, Message
from typing import Callable, Dict, Any, Awaitable
import logging


class CleanupMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
        ):
        state = data.get("state")
        bot = data.get("bot")
        
        if state:
            state_data = await state.get_data()
            kb_message_id = state_data.get("kb_message_id")
            
            if isinstance(event, Message):
                chat_id = event.chat.id
            elif isinstance(event, CallbackQuery):
                chat_id = event.message.chat.id

            if kb_message_id:
                try:
                    await bot.edit_message_reply_markup(
                        chat_id=chat_id,
                        message_id=kb_message_id,
                        reply_markup=None
                    )
                    
                    logging.info('Deleted inline keyboard')
                    
                except Exception:
                    pass
                
                await state.clear()

        return await handler(event, data)
    
    