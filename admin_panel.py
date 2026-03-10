from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from config import ADMIN_IDS
from database import (
    get_setting,
    set_setting,
    get_total_messages,
    get_users
)

router = Router()


def is_admin(user_id: int):
    return user_id in ADMIN_IDS


def admin_menu():

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📊 Статистика",
                    callback_data="admin_stats"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⚙ Настройки активности",
                    callback_data="admin_settings"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📢 Рассылка",
                    callback_data="admin_broadcast"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👥 Пользователи",
                    callback_data="admin_users"
                )
            ]
        ]
    )

    return keyboard


@router.message(F.text == "/admin")
async def open_admin_panel(message: Message):

    if not is_admin(message.from_user.id):
        return

    await message.answer(
        "Панель администратора",
        reply_markup=admin_menu()
    )


@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):

    users = await get_users()
    messages = await get_total_messages()

    text = f"""
📊 Статистика

Пользователей: {len(users)}
Сообщений: {messages}
"""

    await callback.message.edit_text(
        text,
        reply_markup=admin_menu()
    )


@router.callback_query(F.data == "admin_settings")
async def admin_settings(callback: CallbackQuery):

    warning = await get_setting("warning_days")
    kick = await get_setting("kick_days")

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⚠ Предупреждение +1 день",
                    callback_data="warning_plus"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Удаление +10 дней",
                    callback_data="kick_plus"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅ Назад",
                    callback_data="admin_back"
                )
            ]
        ]
    )

    await callback.message.edit_text(
        f"""
⚙ Настройки активности

Предупреждение: {warning} дней
Удаление: {kick} дней
""",
        reply_markup=keyboard
    )


@router.callback_query(F.data == "warning_plus")
async def warning_plus(callback: CallbackQuery):

    current = await get_setting("warning_days")

    new_value = current + 1

    await set_setting("warning_days", new_value)

    await callback.answer("Период предупреждения увеличен")


@router.callback_query(F.data == "kick_plus")
async def kick_plus(callback: CallbackQuery):

    current = await get_setting("kick_days")

    new_value = current + 10

    await set_setting("kick_days", new_value)

    await callback.answer("Период удаления увеличен")


@router.callback_query(F.data == "admin_users")
async def admin_users(callback: CallbackQuery):

    users = await get_users()

    text = "👥 Пользователи в базе\n\n"

    for user in users[:20]:
        text += f"{user[1]}\n"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅ Назад",
                    callback_data="admin_back"
                )
            ]
        ]
    )

    await callback.message.edit_text(
        text,
        reply_markup=keyboard
    )


@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast(callback: CallbackQuery):

    await callback.message.edit_text(
        "Отправьте сообщение, которое нужно разослать пользователям."
    )

    await callback.answer()


@router.callback_query(F.data == "admin_back")
async def admin_back(callback: CallbackQuery):

    await callback.message.edit_text(
        "Панель администратора",
        reply_markup=admin_menu()
    )
