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
    DOWNLOAD_DIR
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

log = logging.getLogger("مشغل-القرآن")


# =========================
# إعداد حساب تيليجرام
# =========================

app = Client(
    "quran_player_ar",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=PYROGRAM_SESSION
)


calls = PyTgCalls(app)


DOWNLOAD_DIR = Path(
    DOWNLOAD_DIR
)

DOWNLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# =========================
# البيانات المؤقتة
# =========================

queues = {}

current = {}

paused = set()


# =========================
# أدوات
# =========================

def normalize(text):

    return re.sub(
        r"\s+",
        " ",
        (text or "").strip().lower()
    ).replace("ـ", "")


def is_admin(message):

    return bool(
        message.from_user
        and message.from_user.id in ADMIN_IDS
    )


def get_replied_media(message):

    reply = message.reply_to_message

    if not reply:
        return None

    if (
        reply.audio
        or reply.voice
        or reply.document
    ):
        return reply

    return None


def get_title(message):

    if message.audio:

        return (
            message.audio.file_name
            or "تلاوة"
        )

    if message.document:

        return (
            message.document.file_name
            or "تلاوة"
        )

    return "تلاوة"


# =========================
# تنزيل ملف الصوت
# =========================

async def download_media(message):

    extension = ".mp3"

    if message.audio:

        extension = (
            Path(
                message.audio.file_name
                or "audio.mp3"
            ).suffix
            or ".mp3"
        )

    elif message.document:

        extension = (
            Path(
                message.document.file_name
                or "audio.mp3"
            ).suffix
            or ".mp3"
        )

    elif message.voice:

        extension = ".ogg"


    path = (
        DOWNLOAD_DIR
        /
        f"{uuid.uuid4().hex}{extension}"
    )


    result = await message.download(
        file_name=str(path)
    )


    if not result:

        raise RuntimeError(
            "تعذر تنزيل الملف من تيليجرام."
        )


    return Path(result)


# =========================
# حذف ملف
# =========================

async def delete_file(path):

    try:

        Path(path).unlink(
            missing_ok=True
        )

    except Exception:

        pass


# =========================
# تشغيل ملف
# =========================

async def play_file(
    chat_id,
