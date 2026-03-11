from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime

from database import (
    get_users,
    get_chats,
    get_setting,
    get_setting_text,
    add_warning
)

from config import ADMIN_IDS


def start_scheduler(bot):

    scheduler = AsyncIOScheduler()

    async def check_activity():

        warning_days = await get_setting("warning_days")
        second_warning_days = await get_setting("second_warning_days")
        kick_days = await get_setting("kick_days")

        warning_text = await get_setting_text("warning_text")
        second_warning_text = await get_setting_text("second_warning_text")

        users = await get_users()
        chats = await get_chats()

        now = datetime.utcnow()

        for user_id, username, last_activity, warned, warnings in users:

            # админов не трогаем
            if user_id in ADMIN_IDS:
                continue

            last_activity = datetime.fromisoformat(last_activity)
            days = (now - last_activity).days

            # первое предупреждение
            if days >= warning_days and warnings == 0:

                try:
                    await bot.send_message(user_id, warning_text)
                    await add_warning(user_id)
                except Exception as e:
                    print("Warning send error:", e)

            # второе предупреждение
            elif days >= second_warning_days and warnings == 1:

                try:
                    await bot.send_message(user_id, second_warning_text)
                    await add_warning(user_id)
                except Exception as e:
                    print("Second warning error:", e)

            # удаление из чатов
            elif days >= kick_days:

                for chat_id, title in chats:

                    try:
                        await bot.ban_chat_member(chat_id, user_id)
                    except Exception as e:
                        print(f"Kick error in {title}:", e)

    scheduler.add_job(check_activity, "interval", hours=24)

    scheduler.start()
