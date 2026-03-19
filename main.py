from config import settings, logging_setup
from aiogram import Bot, Dispatcher
from bot.handlers import router
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import logging
from database.func import create_tables, delete_old_trainings
 

bot = Bot(token=settings.BOT_TOKEN) 
dp = Dispatcher() 

async def main():
    logging_setup()
    log = logging.getLogger(__name__) 
    log.info('Running')
    
    create_tables()
    
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        delete_old_trainings, 
        trigger='cron', 
        day_of_week='mon',
        hour=0, 
        minute=0
    )
    
    scheduler.start()  
    
    if settings.DROP_BEFORE_START:
        await bot.delete_webhook(drop_pending_updates=True)
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('[ EXIT ]')