
import asyncio
from headers import register_handlers_common
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher

bot = Bot(token='5492450684:AAFpCj8ekRU3z3WJKuuZnIKLC63O-8dx-ko')
dp = Dispatcher(bot, storage=MemoryStorage())


async def main():
    try:

        register_handlers_common(dp)
        await dp.start_polling()
    except BaseException as err:
        await bot.send_message(504312150, f'Ошибка: {err}')
        await bot.close_bot()
        asyncio.run(main())

asyncio.run(main())

