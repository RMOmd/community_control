from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ChatType

from config import ADMIN_IDS
from database import (
    get_setting,
    get_setting_text,
    get_users,
    get_total_messages
)

router = Router()


def is_admin(user_id):
    return user_id in ADMIN_IDS


# -------------------------
# Главное меню админа
# -------------------------
@router.message(Command("admin"))
async def admin_panel(message: Message):

    if message.chat.type != ChatType.PRIVATE:
        await message.answer("Напишите эту команду боту в личные сообщения")
        return

    if not is_admin(message.from_user.id):
        return

    kb = InlineKeyboardBuilder()

    kb.button(text="⚙ Настройки", callback_data="admin_settings")
    kb.button(text="👥 Неактивные", callback_data="admin_inactive")
    kb.button(text="📊 Статистика", callback_data="admin_stats")

    kb.adjust(1)

    await message.answer(
        "⚙ Панель администратора",
        reply_markup=kb.as_markup()
    )


# -------------------------
# Настройки
# -------------------------
@router.callback_query(F.data == "admin_settings")
async def admin_settings(callback: CallbackQuery):

    warning = await get_setting("warning_days")
    second_warning = await get_setting("second_warning_days")
    kick = await get_setting("kick_days")

    kb = InlineKeyboardBuilder()

    kb.button(text="1️⃣ Первое предупреждение", callback_data="set_warning_days")
    kb.button(text="2️⃣ Второе предупреждение", callback_data="set_second_warning_days")
    kb.button(text="🚫 Удаление", callback_data="set_kick_days")
    kb.button(text="✏ Текст 1 предупреждения", callback_data="set_warning_text")
    kb.button(text="✏ Текст 2 предупреждения", callback_data="set_second_warning_text")
    kb.button(text="⬅ Назад", callback_data="admin_menu")

    kb.adjust(1)

    text = f"""
⚙ Настройки активности

1 предупреждение: {warning} дней
2 предупреждение: {second_warning} дней
Удаление: {kick} дней
"""

    await callback.message.edit_text(text, reply_markup=kb.as_markup())


# -------------------------
# Неактивные пользователи
# -------------------------
@router.callback_query(F.data == "admin_inactive")
async def admin_inactive(callback: CallbackQuery):

    users = await get_users()

    text = "👥 Пользователи в базе\n\n"

    for _, username, *_ in users[:20]:
        text += f"{username}\n"

    await callback.message.edit_text(text)


# -------------------------
# Статистика
# -------------------------
@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):

    users = await get_users()
    messages = await get_total_messages()

    text = f"""
📊 Статистика

Пользователей в базе: {len(users)}
Всего сообщений: {messages}
"""

    await callback.message.edit_text(text)
