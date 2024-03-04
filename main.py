import asyncio
import logging
import sys
import aioredis

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.storage.memory import MemoryStorage

from configuration import BOT_TOKEN, USE_REDIS
from bot.routers.main_router import main_router
from bot.middlewares.user_base import UserToContextMiddleware, UpdateUsernameMiddleware
from bot.middlewares.only_private import AnswerOnlyInPrivateChats


async def main() -> None:
    if USE_REDIS:
        redis = aioredis.from_url("redis://redis:6379/1", encoding="utf8", decode_responses=True)
        storage = RedisStorage(redis)
    else:
        storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.message.middleware(UserToContextMiddleware())
    dp.message.middleware(UpdateUsernameMiddleware())
    dp.message.middleware(AnswerOnlyInPrivateChats())
    bot = Bot(BOT_TOKEN)
    dp.include_router(main_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
