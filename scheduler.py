from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime

from database import get_users,set_warned,get_setting
from config import CHAT_ID,ADMIN_IDS


def start_scheduler(bot):

    scheduler = AsyncIOScheduler()

    async def check_activity():

        warning_days = await get_setting("warning_days")
        kick_days = await get_setting("kick_days")

        users = await get_users()

        now = datetime.utcnow()

        for user_id,username,last_activity,warned,warnings in users:

            if user_id in ADMIN_IDS:
                continue

            last_activity = datetime.fromisoformat(last_activity)

            days = (now-last_activity).days

            if days >= warning_days and not warned:

                try:

                    await bot.send_message(
                        user_id,
                        f"Вы не проявляли активность {warning_days} дней."
                    )

                    await set_warned(user_id)

                except:
                    pass

            if days >= kick_days:

                try:

                    await bot.ban_chat_member(CHAT_ID,user_id)

                except:
                    pass

    scheduler.add_job(check_activity,"interval",hours=24)

    scheduler.start()
    