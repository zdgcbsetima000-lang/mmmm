import asyncio
import logging
import re
import uuid
from pathlib import Path

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream

from config import API_ID, API_HASH, SESSION_NAME, ADMIN_IDS, DOWNLOAD_DIR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

app = Client(
    SESSION_NAME,
    api_id=API_ID,
    api_hash=API_HASH
)

calls = PyTgCalls(app)

DOWNLOAD_DIR = Path(DOWNLOAD_DIR)
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

queues = {}
current = {}
paused = set()


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

    if reply.audio or reply.voice or reply.document:
        return reply

    return None


def get_title(message):
    if message.audio:
        return message.audio.file_name or "تلاوة"

    if message.document:
        return message.document.file_name or "تلاوة"

    return "تلاوة"


async def download_media(message):
    extension = ".mp3"

    if message.audio:
        extension = (
            Path(message.audio.file_name or "audio.mp3").suffix
            or ".mp3"
        )

    elif message.document:
        extension = (
            Path(message.document.file_name or "audio.mp3").suffix
            or ".mp3"
        )

    elif message.voice:
        extension = ".ogg"

    path = DOWNLOAD_DIR / f"{uuid.uuid4().hex}{extension}"

    result = await message.download(
        file_name=str(path)
    )

    if not result:
        raise RuntimeError(
            "تعذر تنزيل الملف من تيليجرام."
        )

    return Path(result)


async def delete_file(path):
    try:
        Path(path).unlink(missing_ok=True)
    except Exception:
        pass


async def play_file(chat_id, path, title):
    current[chat_id] = {
        "path": str(path),
        "title": title
    }

    paused.discard(chat_id)

    await calls.play(
        chat_id,
        MediaStream(str(path))
    )


async def stop_player(chat_id, clear_queue=True):

    try:
        await calls.leave_call(chat_id)
    except Exception:
        pass

    item = current.pop(
        chat_id,
        None
    )

    if item:
        await delete_file(
            item["path"]
        )

    if clear_queue:

        queue = queues.pop(
            chat_id,
            []
        )

        for item in queue:
            await delete_file(
                item["path"]
            )

    paused.discard(chat_id)


async def play_next(chat_id):

    queue = queues.get(
        chat_id,
        []
    )

    if not queue:
        return False

    old = current.pop(
        chat_id,
        None
    )

    if old:
        await delete_file(
            old["path"]
        )

    item = queue.pop(0)

    await play_file(
        chat_id,
        item["path"],
        item["title"]
    )

    return True


def help_text():

    return """
🌿 **مشغل القرآن الكريم**

📌 اعمل Reply على ملف السورة ثم استخدم:

▶️ `/تشغيل`
تشغيل السورة

➕ `/إضافة`
إضافة السورة لقائمة الانتظار

⏭️ `/التالي`
تشغيل السورة التالية

⏸️ `/مؤقت`
إيقاف مؤقت

▶️ `/استئناف`
استئناف التشغيل

⏹️ `/إيقاف`
إيقاف التشغيل

📋 `/القائمة`
عرض قائمة الانتظار

📊 `/الحالة`
عرض حالة المشغل

🗑️ `/مسح`
مسح قائمة الانتظار

❓ `/مساعدة`
عرض الأوامر

🎧 ملفات الصوت تبقى على تيليجرام.
لا تحتاج إلى رفع سور القرآن على GitHub.
"""


@app.on_message(
    filters.command(
        "start",
        prefixes="/"
    )
)
async def start_command(_, message):

    if not is_admin(message):
        return

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "📖 الأوامر",
                    callback_data="help"
                )
            ],
            [
                InlineKeyboardButton(
                    "📊 الحالة",
                    callback_data="status"
                )
            ]
        ]
    )

    await message.reply_text(
        """
🌿 **أهلًا بك في مشغل القرآن الكريم**

اعمل Reply على ملف MP3
ثم اكتب:

`/تشغيل`
""",
        reply_markup=keyboard
    )


@app.on_message(
    filters.incoming | filters.outgoing
)
async def command_handler(_, message: Message):

    if not is_admin(message):
        return

    text = (
        message.text
        or message.caption
        or ""
    )

    if not text.startswith("/"):
        return

    command = normalize(
        text.split()[0][1:]
    )

    if "@" in command:
        command = command.split("@")[0]

    chat_id = message.chat.id

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

        "إيقاف": "stop",
        "ايقاف": "stop",

        "مؤقت": "pause",

        "استئناف": "resume",

        "القائمة": "queue",

        "الحالة": "status",

        "مسح": "clear"
    }

    command = aliases.get(
        command,
        command
    )

    # -------------------------
    # المساعدة
    # -------------------------

    if command == "help":

        await message.reply_text(
            help_text()
        )

    # -------------------------
    # تشغيل
    # -------------------------

    elif command == "play":

        media = get_replied_media(
            message
        )

        if not media:

            await message.reply_text(
                "❌ اعمل Reply على ملف MP3 ثم اكتب `/تشغيل`."
            )

            return

        status = await message.reply_text(
            "⏳ جاري تجهيز السورة..."
        )

        path = None

        try:

            path = await download_media(
                media
            )

            await stop_player(
                chat_id
            )

            await play_file(
                chat_id,
                path,
                get_title(media)
            )

            await status.edit_text(
                f"""
▶️ **تم تشغيل التلاوة**

🎙️ {get_title(media)}
"""
            )

        except Exception as error:

            if path:
                await delete_file(
                    path
                )

            await status.edit_text(
                f"""
❌ تعذر تشغيل التلاوة.

الخطأ:
`{type(error).__name__}: {error}`
"""
            )

    # -------------------------
    # إضافة
    # -------------------------

    elif command == "add":

        media = get_replied_media(
            message
        )

        if not media:

            await message.reply_text(
                "❌ اعمل Reply على ملف MP3 ثم اكتب `/إضافة`."
            )

            return

        try:

            path = await download_media(
                media
            )

            queue = queues.setdefault(
                chat_id,
                []
            )

            queue.append(
                {
                    "path": str(path),
                    "title": get_title(media)
                }
            )

            await message.reply_text(
                f"""
➕ **تمت إضافة التلاوة**

📌 الترتيب: {len(queue)}
🎙️ {get_title(media)}
"""
            )

        except Exception as error:

            await message.reply_text(
                f"❌ تعذر إضافة الملف:\n{error}"
            )

    # -------------------------
    # التالي
    # -------------------------

    elif command == "next":

        result = await play_next(
            chat_id
        )

        if result:

            await message.reply_text(
                "⏭️ تم تشغيل التلاوة التالية."
            )

        else:

            await message.reply_text(
                "📭 لا توجد تلاوة تالية."
            )

    # -------------------------
    # إيقاف
    # -------------------------

    elif command == "stop":

        await stop_player(
            chat_id
        )

        await message.reply_text(
            "⏹️ تم إيقاف التشغيل ومسح القائمة."
        )

    # -------------------------
    # إيقاف مؤقت
    # -------------------------

    elif command == "pause":

        try:

            await calls.pause(
                chat_id
            )

            paused.add(
                chat_id
            )

            await message.reply_text(
                "⏸️ تم الإيقاف المؤقت."
            )

        except Exception as error:

            await message.reply_text(
                f"❌ تعذر الإيقاف المؤقت:\n{error}"
            )

    # -------------------------
    # استئناف
    # -------------------------

    elif command == "resume":

        try:

            await calls.resume(
                chat_id
            )

            paused.discard(
                chat_id
            )

            await message.reply_text(
                "▶️ تم استئناف التلاوة."
            )

        except Exception as error:

            await message.reply_text(
                f"❌ تعذر الاستئناف:\n{error}"
            )

    # -------------------------
    # القائمة
    # -------------------------

    elif command == "queue":

        queue = queues.get(
            chat_id,
            []
        )

        if not queue:

            await message.reply_text(
                "📭 قائمة الانتظار فارغة."
            )

            return

        text = [
            "📋 **قائمة الانتظار:**"
        ]

        for number, item in enumerate(
            queue,
            1
        ):

            text.append(
                f"{number}. {item['title']}"
            )

        await message.reply_text(
            "\n".join(text)
        )

    # -------------------------
    # الحالة
    # -------------------------

    elif command == "status":

        item = current.get(
            chat_id
        )

        queue_size = len(
            queues.get(
                chat_id,
                []
            )
        )

        if not item:

            state = "⏹️ متوقف"
            title = "لا توجد تلاوة"

        elif chat_id in paused:

            state = "⏸️ متوقف مؤقتًا"
            title = item["title"]

        else:

            state = "▶️ يعمل"
            title = item["title"]

        await message.reply_text(
            f"""
📊 **حالة مشغل القرآن**

{state}

🎙️ التلاوة:
{title}

📋 في الانتظار:
{queue_size}
"""
        )

    # -------------------------
    # مسح القائمة
    # -------------------------

    elif command == "clear":

        queue = queues.pop(
            chat_id,
            []
        )

        for item in queue:

            await delete_file(
                item["path"]
            )

        await message.reply_text(
            f"🗑️ تم مسح {len(queue)} ملف من قائمة الانتظار."
        )


@app.on_callback_query()
async def callback_handler(_, query):

    if query.from_user.id not in ADMIN_IDS:

        await query.answer(
            "❌ غير مصرح لك.",
            show_alert=True
        )

        return

    if query.data == "help":

        await query.message.reply_text(
            help_text()
        )

    elif query.data == "status":

        chat_id = query.message.chat.id

        item = current.get(
            chat_id
        )

        if item:

            await query.message.reply_text(
                f"▶️ يعمل الآن:\n🎙️ {item['title']}"
            )

        else:

            await query.message.reply_text(
                "⏹️ لا توجد تلاوة تعمل الآن."
            )

    await query.answer()


async def main():

    await app.start()

    await calls.start()

    me = await app.get_me()

    log.info(
        "تم تسجيل الدخول: %s",
        me.first_name
    )

    log.info(
        "🌿 مشغل القرآن الكريم يعمل الآن."
    )

    await asyncio.Event().wait()


if __name__ == "__main__":

    asyncio.run(
        main()
    )
