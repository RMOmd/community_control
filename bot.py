import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import Message, ChatMemberUpdated
from aiogram.enums import ChatType

from config import BOT_TOKEN

from database import (
    init_db,
    update_activity,
    save_chat,
    add_admin
)

from scheduler import start_scheduler

from admin_panel import router as admin_panel_router
from admin_system import router as admin_system_router
from admin import router as admin_router
from stats import router as stats_router


# создаём объект бота
bot = Bot(token=BOT_TOKEN)

# диспетчер
dp = Dispatcher()


# подключаем роутеры
dp.include_router(admin_router)
dp.include_router(stats_router)
dp.include_router(admin_panel_router)
dp.include_router(admin_system_router)


# событие добавления бота в группу
@dp.my_chat_member()
async def bot_added(event: ChatMemberUpdated):

    new_status = event.new_chat_member.status

    if new_status in ["member", "administrator"]:

        chat = event.chat

        if chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:

            await save_chat(
                chat.id,
                chat.title
            )

            print(f"Бот добавлен в чат: {chat.title} ({chat.id})")


# обработчик сообщений (трек активности)
@dp.message()
async def track_activity(message: Message):

    # только группы
    if message.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        return

    # сохраняем чат (если новый)
    await save_chat(
        message.chat.id,
        message.chat.title
    )

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

    # добавить владельца
    await add_admin(
        40916643,
        "owner",
        "owner"
    )

    # запуск планировщика
    start_scheduler(bot)

    print("Планировщик запущен")

    # запуск polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
