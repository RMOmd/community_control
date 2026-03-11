import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.enums import ChatType
from admin_panel import router as admin_panel_router
from config import BOT_TOKEN
from database import init_db, update_activity
from scheduler import start_scheduler
from admin_system import router as admin_system_router
from admin import router as admin_router
from stats import router as stats_router
from database import add_admin

# создаём объект бота
bot = Bot(token=BOT_TOKEN)

# диспетчер aiogram
dp = Dispatcher()

# подключаем роутеры
dp.include_router(admin_router)
dp.include_router(stats_router)
dp.include_router(admin_panel_router)
dp.include_router(admin_system_router)


# обработчик всех сообщений (трек активности)
@dp.message()
async def track_activity(message: Message):

    # учитываем только сообщения из групп
    if message.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        return

    user = message.from_user

    if not user:
        return

    user_id = user.id

    username = user.username or user.first_name or "unknown"

    # обновляем активность
    await update_activity(user_id, username)


# запуск бота
async def main():

    print("Запуск бота...")

    # инициализация базы
    await init_db()

    print("База данных готова")

    await add_admin(
        40916643,
        "owner",
        "owner"
    )

    # запуск планировщика активности
    start_scheduler(bot)

    print("Планировщик запущен")

    # запуск polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
