from aiogram import Router
from aiogram.types import Message
from datetime import datetime
import aiosqlite

from config import ADMIN_IDS, CHAT_ID
from database import (
    add_warning,
    get_users,
    set_setting,
    get_setting,
    DB
)

router = Router()


def is_admin(user_id: int):
    return user_id in ADMIN_IDS


@router.message(lambda m: m.text and m.text.startswith("/broadcast"))
async def broadcast(message: Message):

    if not is_admin(message.from_user.id):
        return

    text = message.text.replace("/broadcast ", "")

    users = await get_users()

    sent = 0

    for user_id, *_ in users:
        try:
            await message.bot.send_message(user_id, text)
            sent += 1
        except:
            pass

    await message.answer(f"Рассылка завершена\nОтправлено: {sent}")


@router.message(lambda m: m.text and m.text.startswith("/warn"))
async def warn_user(message: Message):

    if not is_admin(message.from_user.id):
        return

    if not message.reply_to_message:
        await message.answer("Ответьте на сообщение пользователя")
        return

    user = message.reply_to_message.from_user

    await add_warning(user.id)

    await message.answer(
        f"Пользователь {user.username or user.first_name} получил предупреждение"
    )


@router.message(lambda m: m.text and m.text.startswith("/notify"))
async def notify_group(message: Message):

    if not is_admin(message.from_user.id):
        return

    text = message.text.replace("/notify ", "")

    await message.bot.send_message(CHAT_ID, text)


@router.message(lambda m: m.text == "/inactive")
async def inactive_list(message: Message):

    if not is_admin(message.from_user.id):
        return

    users = await get_users()

    text = "Список пользователей:\n\n"

    for user in users:
        text += f"{user[1]}\n"

    await message.answer(text)


@router.message(lambda m: m.text and m.text.startswith("/set_warning"))
async def set_warning(message: Message):

    if not is_admin(message.from_user.id):
        return

    try:
        days = int(message.text.split()[1])
    except:
        await message.answer("Использование: /set_warning 7")
        return

    await set_setting("warning_days", days)

    await message.answer(
        f"Период предупреждения установлен: {days} дней"
    )


@router.message(lambda m: m.text and m.text.startswith("/set_kick"))
async def set_kick(message: Message):

    if not is_admin(message.from_user.id):
        return

    try:
        days = int(message.text.split()[1])
    except:
        await message.answer("Использование: /set_kick 180")
        return

    await set_setting("kick_days", days)

    await message.answer(
        f"Период удаления установлен: {days} дней"
    )


@router.message(lambda m: m.text == "/settings")
async def show_settings(message: Message):

    if not is_admin(message.from_user.id):
        return

    warning = await get_setting("warning_days")
    kick = await get_setting("kick_days")

    await message.answer(
        f"""
Настройки активности

Предупреждение: {warning} дней
Удаление: {kick} дней
"""
    )


@router.message(lambda m: m.text == "/reset_stats")
async def reset_stats(message: Message):

    if not is_admin(message.from_user.id):
        return

    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE users SET messages=0")
        await db.commit()

    await message.answer("Статистика сообщений сброшена")


@router.message(lambda m: m.text == "/kickinactive")
async def kick_inactive(message: Message):

    if not is_admin(message.from_user.id):
        return

    users = await get_users()

    kick_days = await get_setting("kick_days")

    now = datetime.utcnow()

    kicked = 0

    for user_id, username, last_activity, *_ in users:

        last_activity = datetime.fromisoformat(last_activity)

        if (now - last_activity).days >= kick_days:

            try:
                await message.bot.ban_chat_member(CHAT_ID, user_id)
                kicked += 1
            except:
                pass

    await message.answer(f"Удалено пользователей: {kicked}")
