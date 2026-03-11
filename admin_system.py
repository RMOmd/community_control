from aiogram import Router
from aiogram.types import Message

from database import (
    add_admin,
    remove_admin,
    get_admin,
    get_all_admins
)

router = Router()


async def is_admin(user_id):

    admin = await get_admin(user_id)

    return admin is not None


async def is_owner(user_id):

    admin = await get_admin(user_id)

    if admin and admin[0] == "owner":
        return True

    return False


@router.message(lambda m: m.text == "/admins")
async def list_admins(message: Message):

    admins = await get_all_admins()

    text = "Администраторы:\n\n"

    for user_id, username, role in admins:

        text += f"{username} — {role}\n"

    await message.answer(text)


@router.message(lambda m: m.text.startswith("/addadmin"))
async def add_admin_command(message: Message):

    if not await is_owner(message.from_user.id):
        return

    if not message.reply_to_message:
        await message.answer("Ответьте на сообщение пользователя")
        return

    user = message.reply_to_message.from_user

    role = "admin"

    parts = message.text.split()

    if len(parts) > 1:
        role = parts[1]

    await add_admin(
        user.id,
        user.username or user.first_name,
        role
    )

    await message.answer(
        f"{user.username} добавлен как {role}"
    )


@router.message(lambda m: m.text == "/removeadmin")
async def remove_admin_command(message: Message):

    if not await is_owner(message.from_user.id):
        return

    if not message.reply_to_message:
        await message.answer("Ответьте на сообщение администратора")
        return

    user = message.reply_to_message.from_user

    await remove_admin(user.id)

    await message.answer(
        f"{user.username} удалён из администраторов"
    )
