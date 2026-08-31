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


# =========================================================
# إعدادات
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("QuranPlayer")

DOWNLOAD_PATH = Path(DOWNLOAD_DIR)
DOWNLOAD_PATH.mkdir(parents=True, exist_ok=True)


# =========================================================
# Telegram
# =========================================================

app = Client(
    "quran_player_ar",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=PYROGRAM_SESSION,
)


# =========================================================
# Voice Chat
# =========================================================

calls = PyTgCalls(app)


# =========================================================
# بيانات التشغيل
# =========================================================

current = {}
queues = {}
paused = set()


# =========================================================
# أدوات
# =========================================================

def normalize(text: str) -> str:
    text = text or ""
    text = text.strip().lower()
    text = text.replace("ـ", "")
    text = re.sub(r"\s+", " ", text)
    return text


def is_admin(message: Message) -> bool:
    if not message.from_user:
        return False

    return message.from_user.id in ADMIN_IDS


def get_replied_media(message: Message):
    reply = message.reply_to_message

    if not reply:
        return None

    if reply.audio:
        return reply

    if reply.voice:
        return reply

    if reply.document:
        return reply

    return None


def get_media_title(message: Message) -> str:
    if message.audio:
        return (
            message.audio.file_name
            or "تلاوة القرآن الكريم"
        )

    if message.document:
        return (
            message.document.file_name
            or "تلاوة القرآن الكريم"
        )

    if message.voice:
        return "تلاوة القرآن الكريم"

    return "تلاوة القرآن الكريم"


def get_media_extension(message: Message) -> str:
    if message.audio:
        filename = message.audio.file_name or "audio.mp3"
        extension = Path(filename).suffix
        return extension or ".mp3"

    if message.document:
        filename = message.document.file_name or "audio.mp3"
        extension = Path(filename).suffix
        return extension or ".mp3"

    if message.voice:
        return ".ogg"

    return ".mp3"


# =========================================================
# تنزيل الملف
# =========================================================

async def download_media(message: Message) -> Path:
    extension = get_media_extension(message)

    filename = f"{uuid.uuid4().hex}{extension}"

    destination = DOWNLOAD_PATH / filename

    result = await message.download(
        file_name=str(destination)
    )

    if not result:
        raise RuntimeError(
            "فشل تنزيل الملف."
        )

    return Path(result)


# =========================================================
# حذف ملف
# =========================================================

async def delete_file(path):
    if not path:
        return

    try:
        Path(path).unlink(
            missing_ok=True
        )
    except Exception as error:
        logger.warning(
            "تعذر حذف الملف: %s",
            error,
        )


# =========================================================
# تشغيل ملف
# =========================================================

async def play_file(
    chat_id,
    path,
    title,
):
    current[chat_id] = {
        "path": str(path),
        "title": title,
    }

    paused.discard(chat_id)

    await calls.play(
        chat_id,
        MediaStream(
            str(path)
        ),
    )


# =========================================================
# إيقاف التشغيل
# =========================================================

async def stop_player(
    chat_id,
    clear_queue=True,
):
    try:
        await calls.leave_call(
            chat_id
        )
    except Exception:
        pass

    current_item = current.pop(
        chat_id,
        None,
    )

    if current_item:
        await delete_file(
            current_item.get("path")
        )

    if clear_queue:
        queue = queues.pop(
            chat_id,
            [],
        )

        for item in queue:
            await delete_file(
                item.get("path")
            )

    paused.discard(chat_id)


# =========================================================
# تشغيل التالي
# =========================================================

async def play_next(chat_id):
    queue = queues.get(
        chat_id,
        [],
    )

    if not queue:
        return False

    old_item = current.pop(
        chat_id,
        None,
    )

    if old_item:
        await delete_file(
            old_item.get("path")
        )

    item = queue.pop(0)

    if not queue:
        queues.pop(
            chat_id,
            None,
        )

    await play_file(
        chat_id,
        item["path"],
        item["title"],
    )

    return True


# =========================================================
# رسالة المساعدة
# =========================================================

HELP_TEXT = """
🌿 **مشغل القرآن الكريم**

━━━━━━━━━━━━━━━━━━━━

📖 **طريقة التشغيل**

أرسل ملف السورة إلى القناة.

ثم اعمل Reply على الملف واكتب:

`/تشغيل`

وسيتم تشغيل الملف في الـ Voice Chat.

━━━━━━━━━━━━━━━━━━━━

🎧 **الأوامر**

▶️ `/تشغيل`
تشغيل ملف السورة.

➕ `/إضافة`
إضافة السورة إلى قائمة الانتظار.

⏭️ `/التالي`
تشغيل السورة التالية.

⏸️ `/مؤقت`
إيقاف مؤقت.

▶️ `/استئناف`
استئناف التشغيل.

⏹️ `/إيقاف`
إيقاف التشغيل.

📋 `/القائمة`
عرض قائمة الانتظار.

📊 `/الحالة`
عرض حالة المشغل.

🗑️ `/مسح`
مسح قائمة الانتظار.

❓ `/مساعدة`
عرض المساعدة.

━━━━━━━━━━━━━━━━━━━━

🌿 **مشغل القرآن الكريم**
"""


# =========================================================
# /start
# =========================================================

@app.on_message(
    filters.command(
        "start",
        prefixes="/",
    )
)
async def start_command(
    client,
    message: Message,
):
    if not is_admin(message):
        return

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "📖 الأوامر",
                    callback_data="help",
                ),
                InlineKeyboardButton(
                    "📊 الحالة",
                    callback_data="status",
                ),
            ]
        ]
    )

    await message.reply_text(
        """
🌿 **أهلًا بك في مشغل القرآن الكريم**

🎧 مشغل تلاوات Telegram

اعمل Reply على ملف السورة ثم اكتب:

`/تشغيل`

وسيتم تشغيله داخل الـ Voice Chat.
""",
        reply_markup=keyboard,
    )


# =========================================================
# الأوامر
# =========================================================

@app.on_message(
    filters.incoming | filters.outgoing
)
async def command_handler(
    client,
    message: Message,
):
    if not is_admin(message):
        return

    text = (
        message.text
        or message.caption
        or ""
    ).strip()

    if not text.startswith("/"):
        return

    command = text.split()[0][1:]

    if "@" in command:
        command = command.split("@")[0]

    command = normalize(command)

    aliases = {
        "مساعدة": "help",
        "الاوامر": "help",
        "الأوامر": "help",

        "تشغيل": "play",
        "شغل": "play",

        "إضافة": "add",
        "اضافة": "add",

        "التالي": "next",
        "التالى": "next",

        "مؤقت": "pause",

        "استئناف": "resume",

        "إيقاف": "stop",
        "ايقاف": "stop",

        "القائمة": "queue",

        "الحالة": "status",

        "مسح": "clear",
    }

    command = aliases.get(
        command,
        command,
    )

    chat_id = message.chat.id

    # -----------------------------------------------------
    # مساعدة
    # -----------------------------------------------------

    if command == "help":
        await message.reply_text(
            HELP_TEXT
        )
        return

    # -----------------------------------------------------
    # تشغيل
    # -----------------------------------------------------

    if command == "play":
        media
