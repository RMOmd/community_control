from aiogram import Router
from aiogram.types import Message

from database import (
    get_top_users,
    get_total_messages,
    get_user_stats,
    get_users
)

router = Router()


@router.message(lambda m: m.text == "/top")
async def top_users(message: Message):

    users = await get_top_users()

    text = "🏆 Топ активных участников\n\n"

    for i, user in enumerate(users, start=1):

        name, messages = user

        text += f"{i}. {name} — {messages} сообщений\n"

    await message.answer(text)


@router.message(lambda m: m.text.startswith("/stats"))
async def user_stats(message: Message):

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    else:
        user_id = message.from_user.id

    data = await get_user_stats(user_id)

    if not data:
        await message.answer("Нет данных по пользователю")
        return

    username, messages, last_activity, warnings = data

    text = f"""
📊 Статистика пользователя

Имя: {username}
Сообщений: {messages}
Предупреждений: {warnings}
Последняя активность: {last_activity}
"""

    await message.answer(text)


@router.message(lambda m: m.text == "/teamstats")
async def team_stats(message: Message):

    total_messages = await get_total_messages()

    users = await get_users()

    text = f"""
📊 Статистика команды

Участников в базе: {len(users)}
Всего сообщений: {total_messages}
"""

    await message.answer(text)
    