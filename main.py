from config import settings, logging_setup
from aiogram import Bot, Dispatcher
from bot.handlers import router
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import logging      


bot = Bot(token=settings.BOT_TOKEN) 
dp = Dispatcher() 

async def main():
    logging_setup()
    log = logging.getLogger(__name__) 
    log.info('Running')
    
    # create_tables()
    
    # scheduler = AsyncIOScheduler()
    # scheduler.delete_old_trainings(
        
    # )
    
    # scheduler.start()  
    
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('[ EXIT ]')