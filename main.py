import asyncio
import logging
import re
import uuid
from pathlib import Path

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream

from config import (
    API_ID,
    API_HASH,
    PYROGRAM_SESSION,
    ADMIN_IDS,
    DOWNLOAD_DIR,
)


# ============================================================
# إعداد التسجيل
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("QuranPlayer")


# ============================================================
# إعداد مجلد التحميل
# ============================================================

DOWNLOAD_PATH = Path(DOWNLOAD_DIR)
DOWNLOAD_PATH.mkdir(parents=True, exist_ok=True)


# ============================================================
# Pyrogram
# ============================================================

app = Client(
    "quran_player_ar",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=PYROGRAM_SESSION,
)


# ============================================================
# PyTgCalls
# ============================================================

calls = PyTgCalls(app)


# ============================================================
# بيانات المشغل
# ============================================================

current = {}

queues = {}

paused = set()


# ============================================================
# أدوات مساعدة
# ============================================================

def normalize(text: str) -> str:
    """
    تنظيف النص وتحويله إلى صيغة سهلة للمقارنة.
    """
    return re.sub(
        r"\s+",
        " ",
        (text or "").strip().lower(),
    ).replace("ـ", "")


def is_admin(message: Message
