import aiosqlite
from datetime import datetime

DB = "team_activity.db"


async def init_db():

    async with aiosqlite.connect(DB) as db:

        # таблица пользователей
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            last_activity TEXT,
            warned INTEGER DEFAULT 0,
            warnings INTEGER DEFAULT 0,
            messages INTEGER DEFAULT 0
        )
        """)

        # таблица настроек
        await db.execute("""
        CREATE TABLE IF NOT EXISTS settings(
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """)

        # таблица администраторов
        await db.execute("""
        CREATE TABLE IF NOT EXISTS admins(
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            role TEXT
        )
        """)

        # таблица чатов
        await db.execute("""
        CREATE TABLE IF NOT EXISTS chats(
            chat_id INTEGER PRIMARY KEY,
            title TEXT
        )
        """)

        # настройки по умолчанию
        await db.execute("""
        INSERT OR IGNORE INTO settings(key,value)
        VALUES
        ('warning_days','7'),
        ('second_warning_days','14'),
        ('kick_days','180'),
        ('warning_text','Вы давно не проявляли активность в группе.'),
        ('second_warning_text','Вы не активны уже долгое время. Это второе предупреждение.')
        """)

        await db.commit()


# обновление активности пользователя
async def update_activity(user_id, username):

    now = datetime.utcnow().isoformat()

    async with aiosqlite.connect(DB) as db:

        await db.execute("""
        INSERT INTO users(user_id,username,last_activity,warned,messages)
        VALUES(?,?,?,0,1)

        ON CONFLICT(user_id)
        DO UPDATE SET
            last_activity=excluded.last_activity,
            username=excluded.username,
            messages=messages+1,
            warned=0
        """,(user_id,username,now))

        await db.commit()


# получить пользователей
async def get_users():

    async with aiosqlite.connect(DB) as db:

        cursor = await db.execute("SELECT * FROM users")

        return await cursor.fetchall()


# добавить предупреждение
async def add_warning(user_id):

    async with aiosqlite.connect(DB) as db:

        await db.execute(
            "UPDATE users SET warnings = warnings + 1 WHERE user_id=?",
            (user_id,)
        )

        await db.commit()


# установить флаг предупреждения
async def set_warned(user_id):

    async with aiosqlite.connect(DB) as db:

        await db.execute(
            "UPDATE users SET warned=1 WHERE user_id=?",
            (user_id,)
        )

        await db.commit()


# получить настройку (числовую)
async def get_setting(key):

    async with aiosqlite.connect(DB) as db:

        cursor = await db.execute(
            "SELECT value FROM settings WHERE key=?",
            (key,)
        )

        row = await cursor.fetchone()

        if row:
            return int(row[0])

        return 0


# изменить настройку
async def set_setting(key,value):

    async with aiosqlite.connect(DB) as db:

        await db.execute(
            "UPDATE settings SET value=? WHERE key=?",
            (str(value),key)
        )

        await db.commit()


# получить текстовую настройку
async def get_setting_text(key):

    async with aiosqlite.connect(DB) as db:

        cursor = await db.execute(
            "SELECT value FROM settings WHERE key=?",
            (key,)
        )

        row = await cursor.fetchone()

        if row:
            return row[0]

        return ""


# топ пользователей
async def get_top_users(limit=10):

    async with aiosqlite.connect(DB) as db:

        cursor = await db.execute(
            "SELECT username,messages FROM users ORDER BY messages DESC LIMIT ?",
            (limit,)
        )

        return await cursor.fetchall()


# общее количество сообщений
async def get_total_messages():

    async with aiosqlite.connect(DB) as db:

        cursor = await db.execute(
            "SELECT SUM(messages) FROM users"
        )

        row = await cursor.fetchone()

        return row[0] or 0


# статистика пользователя
async def get_user_stats(user_id):

    async with aiosqlite.connect(DB) as db:

        cursor = await db.execute(
            "SELECT username,messages,last_activity,warnings FROM users WHERE user_id=?",
            (user_id,)
        )

        return await cursor.fetchone()


# добавить администратора
async def add_admin(user_id, username, role):

    async with aiosqlite.connect(DB) as db:

        await db.execute("""
        INSERT OR IGNORE INTO admins(user_id, username, role)
        VALUES(?,?,?)
        """, (user_id, username, role))

        await db.commit()


# удалить администратора
async def remove_admin(user_id):

    async with aiosqlite.connect(DB) as db:

        await db.execute(
            "DELETE FROM admins WHERE user_id=?",
            (user_id,)
        )

        await db.commit()


# получить администратора
async def get_admin(user_id):

    async with aiosqlite.connect(DB) as db:

        cursor = await db.execute(
            "SELECT role FROM admins WHERE user_id=?",
            (user_id,)
        )

        return await cursor.fetchone()


# получить всех администраторов
async def get_all_admins():

    async with aiosqlite.connect(DB) as db:

        cursor = await db.execute(
            "SELECT user_id,username,role FROM admins"
        )

        return await cursor.fetchall()


# сохранить чат
async def save_chat(chat_id, title):

    async with aiosqlite.connect(DB) as db:

        await db.execute("""
        INSERT OR IGNORE INTO chats(chat_id,title)
        VALUES(?,?)
        """,(chat_id,title))

        await db.commit()


# получить список чатов
async def get_chats():

    async with aiosqlite.connect(DB) as db:

        cursor = await db.execute(
            "SELECT chat_id,title FROM chats"
        )

        return await cursor.fetchall()
