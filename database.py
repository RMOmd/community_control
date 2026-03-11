import aiosqlite
from datetime import datetime

DB = "team_activity.db"


async def init_db():

    async with aiosqlite.connect(DB) as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            last_activity TEXT,
            warned INTEGER DEFAULT 0,
            warnings INTEGER DEFAULT 0
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS settings(
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """)

        await db.execute("""
        INSERT OR IGNORE INTO settings(key,value)
        VALUES
        ('warning_days','7'),
        ('kick_days','180')
        """)

        await db.commit()


async def update_activity(user_id, username):

    now = datetime.utcnow().isoformat()

    async with aiosqlite.connect(DB) as db:

        await db.execute("""
        INSERT INTO users(user_id,username,last_activity,warned)
        VALUES(?,?,?,0)

        ON CONFLICT(user_id)
        DO UPDATE SET
            last_activity=excluded.last_activity,
            username=excluded.username
        """,(user_id,username,now))

        await db.commit()


async def get_users():

    async with aiosqlite.connect(DB) as db:

        cursor = await db.execute("SELECT * FROM users")

        return await cursor.fetchall()


async def add_warning(user_id):

    async with aiosqlite.connect(DB) as db:

        await db.execute(
            "UPDATE users SET warnings = warnings + 1 WHERE user_id=?",
            (user_id,)
        )

        await db.commit()


async def set_warned(user_id):

    async with aiosqlite.connect(DB) as db:

        await db.execute(
            "UPDATE users SET warned=1 WHERE user_id=?",
            (user_id,)
        )

        await db.commit()


async def get_setting(key):

    async with aiosqlite.connect(DB) as db:

        cursor = await db.execute(
            "SELECT value FROM settings WHERE key=?",
            (key,)
        )

        row = await cursor.fetchone()

        return int(row[0])


async def set_setting(key,value):

    async with aiosqlite.connect(DB) as db:

        await db.execute(
            "UPDATE settings SET value=? WHERE key=?",
            (str(value),key)
        )

        await db.commit()


async def get_top_users(limit=10):

    async with aiosqlite.connect(DB) as db:

        cursor = await db.execute(
            "SELECT username,messages FROM users ORDER BY messages DESC LIMIT ?",
            (limit,)
        )

        return await cursor.fetchall()


async def get_total_messages():

    async with aiosqlite.connect(DB) as db:

        cursor = await db.execute(
            "SELECT SUM(messages) FROM users"
        )

        row = await cursor.fetchone()

        return row[0] or 0


async def get_user_stats(user_id):

    async with aiosqlite.connect(DB) as db:

        cursor = await db.execute(
            "SELECT username,messages,last_activity,warnings FROM users WHERE user_id=?",
            (user_id,)
        )

        return await cursor.fetchone()


async def init_admin_table():

    async with aiosqlite.connect(DB) as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS admins(
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            role TEXT
        )
        """)

        await db.commit()


async def add_admin(user_id, username, role):

    async with aiosqlite.connect(DB) as db:

        await db.execute("""
        INSERT OR REPLACE INTO admins(user_id, username, role)
        VALUES(?,?,?)
        """,(user_id,username,role))

        await db.commit()


async def remove_admin(user_id):

    async with aiosqlite.connect(DB) as db:

        await db.execute(
            "DELETE FROM admins WHERE user_id=?",
            (user_id,)
        )

        await db.commit()


async def get_admin(user_id):

    async with aiosqlite.connect(DB) as db:

        cursor = await db.execute(
            "SELECT role FROM admins WHERE user_id=?",
            (user_id,)
        )

        return await cursor.fetchone()


async def get_all_admins():

    async with aiosqlite.connect(DB) as db:

        cursor = await db.execute(
            "SELECT user_id,username,role FROM admins"
        )

        return await cursor.fetchall()


async def init_chats_table():

    async with aiosqlite.connect(DB) as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS chats(
            chat_id INTEGER PRIMARY KEY,
            title TEXT
        )
        """)

        await db.commit()


async def save_chat(chat_id, title):

    async with aiosqlite.connect(DB) as db:

        await db.execute("""
        INSERT OR IGNORE INTO chats(chat_id,title)
        VALUES(?,?)
        """,(chat_id,title))

        await db.commit()


async def get_chats():

    async with aiosqlite.connect(DB) as db:

        cursor = await db.execute(
            "SELECT chat_id,title FROM chats"
        )

        return await cursor.fetchall()


