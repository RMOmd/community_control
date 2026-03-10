import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

CHAT_ID = int(os.getenv("CHAT_ID"))

ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS").split(",")]
