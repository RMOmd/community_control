from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from datetime import datetime
import aiosqlite

from config import ADMIN_IDS
from database import (
    add_warning,
    get_users,
    get_chats,
    set_setting,
    get_setting,
    get_setting_text,
    DB
)

router = Router()


def is_admin(user_id: int):
    return user_id in ADMIN_IDS


# -------------------------------
# Рассылка пользователям
# -------------------------------
@router.message(Command("broadcast"))
async def broadcast(message: Message):

    if not is_admin(message.from_user.id):
        return

    parts = message.text.split(maxsplit=1)

    if len(parts) < 2:
        await message.answer("Использование: /broadcast текст")
        return

    text = parts[1]

    users = await get_users()

    sent = 0

    for user_id, *_ in users:
        try:
            await message.bot.send_message(user_id, text)
            sent += 1
        except Exception as e:
            print("Broadcast error:", e)

    await message.answer(f"Рассылка завершена\nОтправлено: {sent}")


# -------------------------------
# Предупреждение пользователю
# -------------------------------
@router.message(Command("warn"))
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


# -------------------------------
# Сообщение во все группы
# -------------------------------
@router.message(Command("notify"))
async def notify_group(message: Message):

    if not is_admin(message.from_user.id):
        return

    parts = message.text.split(maxsplit=1)

    if len(parts) < 2:
        await message.answer("Использование: /notify текст")
        return

    text = parts[1]

    chats = await get_chats()

    for chat_id, title in chats:
        try:
            await message.bot.send_message(chat_id, text)
        except Exception as e:
            print(f"Notify error in {title}:", e)

    await message.delete()


# -------------------------------
# Список неактивных пользователей
# -------------------------------
@router.callback_query(F.data == "admin_inactive")
async def admin_inactive(callback: CallbackQuery):

    users = await get_users()
    warning_days = await get_setting("warning_days")

    now = datetime.utcnow()

    text = "👥 Неактивные пользователи\n\n"

    count = 0

    for user_id, username, last_activity, *_ in users:

        try:
            last_activity = datetime.fromisoformat(last_activity)
        except:
            continue

        days = (now - last_activity).days

        if days >= warning_days:

            text += f"{username} — {days} дней\n"
            count += 1

    if count == 0:
        text = "Неактивных пользователей нет"

    await callback.message.edit_text(text)


# -------------------------------
# Настройка первого предупреждения
# -------------------------------
@router.message(Command("set_warning"))
async def set_warning(message: Message):

    if not is_admin(message.from_user.id):
        return

    parts = message.text.split()

    if len(parts) < 2:
        await message.answer("Использование: /set_warning 7")
        return

    days = int(parts[1])

    await set_setting("warning_days", days)

    await message.answer(f"Первое предупреждение: {days} дней")


# -------------------------------
# Настройка второго предупреждения
# -------------------------------
@router.message(Command("set_second_warning"))
async def set_second_warning(message: Message):

    if not is_admin(message.from_user.id):
        return

    parts = message.text.split()

    if len(parts) < 2:
        await message.answer("Использование: /set_second_warning 14")
        return

    days = int(parts[1])

    await set_setting("second_warning_days", days)

    await message.answer(f"Второе предупреждение: {days} дней")


# -------------------------------
# Настройка удаления
# -------------------------------
@router.message(Command("set_kick"))
async def set_kick(message: Message):

    if not is_admin(message.from_user.id):
        return

    parts = message.text.split()

    if len(parts) < 2:
        await message.answer("Использование: /set_kick 180")
        return

    days = int(parts[1])

    await set_setting("kick_days", days)

    await message.answer(f"Удаление пользователей: {days} дней")


# -------------------------------
# Редактирование текста предупреждения
# -------------------------------
@router.message(Command("set_warning_text"))
async def set_warning_text(message: Message):

    if not is_admin(message.from_user.id):
        return

    parts = message.text.split(maxsplit=1)

    if len(parts) < 2:
        await message.answer("Использование: /set_warning_text текст")
        return

    text = parts[1]

    await set_setting("warning_text", text)

    await message.answer("Текст первого предупреждения обновлен")


@router.message(Command("set_second_warning_text"))
async def set_second_warning_text(message: Message):

    if not is_admin(message.from_user.id):
        return

    parts = message.text.split(maxsplit=1)

    if len(parts) < 2:
        await message.answer("Использование: /set_second_warning_text текст")
        return

    text = parts[1]

    await set_setting("second_warning_text", text)

    await message.answer("Текст второго предупреждения обновлен")


# -------------------------------
# Показать настройки
# -------------------------------
@router.message(Command("settings"))
async def show_settings(message: Message):

    if not is_admin(message.from_user.id):
        return

    warning = await get_setting("warning_days")
    second_warning = await get_setting("second_warning_days")
    kick = await get_setting("kick_days")

    warning_text = await get_setting_text("warning_text")
    second_warning_text = await get_setting_text("second_warning_text")

    await message.answer(
        f"""
⚙ Настройки активности

1 предупреждение: {warning} дней
2 предупреждение: {second_warning} дней
Удаление: {kick} дней

Текст 1 предупреждения:
{warning_text}

Текст 2 предупреждения:
{second_warning_text}
"""
    )


# -------------------------------
# Сброс статистики
# -------------------------------
@router.message(Command("reset_stats"))
async def reset_stats(message: Message):

    if not is_admin(message.from_user.id):
        return

    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE users SET messages=0")
        await db.commit()

    await message.answer("Статистика сообщений сброшена")


# -------------------------------
# Удалить неактивных
# -------------------------------
@router.message(Command("kickinactive"))
async def kick_inactive(message: Message):

    if not is_admin(message.from_user.id):
        return

    users = await get_users()
    chats = await get_chats()

    kick_days = await get_setting("kick_days")

    now = datetime.utcnow()

    kicked = 0

    for user_id, username, last_activity, *_ in users:

        last_activity = datetime.fromisoformat(last_activity)

        if (now - last_activity).days >= kick_days:

            for chat_id, title in chats:

                try:
                    await message.bot.ban_chat_member(chat_id, user_id)
                    kicked += 1
                except Exception as e:
                    print("Kick error:", e)

    await message.answer(f"Удалено пользователей: {kicked}")
