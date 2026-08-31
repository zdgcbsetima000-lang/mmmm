import asyncio
import logging
import re
import uuid
from pathlib import Path

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
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
# Telegram Client & Voice Chat
# =========================================================

app = Client(
    "quran_player_ar",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=PYROGRAM_SESSION,
)

calls = PyTgCalls(app)

# =========================================================
# بيانات التشغيل
# =========================================================

current = {}
queues = {}
paused = set()

# =========================================================
# أدوات مساعدة
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
    if reply.audio or reply.voice or reply.document:
        return reply
    return None

def get_media_title(message: Message) -> str:
    if message.audio:
        return message.audio.file_name or "تلاوة القرآن الكريم"
    if message.document:
        return message.document.file_name or "تلاوة القرآن الكريم"
    if message.voice:
        return "تلاوة صوتية"
    return "تلاوة القرآن الكريم"

def get_media_extension(message: Message) -> str:
    if message.audio:
        filename = message.audio.file_name or "audio.mp3"
        ext = Path(filename).suffix
        return ext or ".mp3"
    if message.document:
        filename = message.document.file_name or "audio.mp3"
        ext = Path(filename).suffix
        return ext or ".mp3"
    if message.voice:
        return ".ogg"
    return ".mp3"

async def download_media(message: Message) -> Path:
    extension = get_media_extension(message)
    filename = f"{uuid.uuid4().hex}{extension}"
    destination = DOWNLOAD_PATH / filename

    result = await message.download(file_name=str(destination))
    if not result:
        raise RuntimeError("فشل تنزيل الملف.")
    return Path(result)

async def delete_file(path):
    if not path:
        return
    try:
        Path(path).unlink(missing_ok=True)
    except Exception as error:
        logger.warning("تعذر حذف الملف: %s", error)

async def play_file(chat_id: int, path: Path, title: str):
    current[chat_id] = {
        "path": str(path),
        "title": title,
    }
    paused.discard(chat_id)
    await calls.play(chat_id, MediaStream(str(path)))

async def stop_player(chat_id: int, clear_queue=True):
    try:
        await calls.leave_call(chat_id)
    except Exception:
        pass

    current_item = current.pop(chat_id, None)
    if current_item:
        await delete_file(current_item.get("path"))

    if clear_queue:
        queue = queues.pop(chat_id, [])
        for item in queue:
            await delete_file(item.get("path"))

    paused.discard(chat_id)

async def play_next(chat_id: int) -> bool:
    queue = queues.get(chat_id, [])
    if not queue:
        await stop_player(chat_id, clear_queue=False)
        return False

    old_item = current.pop(chat_id, None)
    if old_item:
        await delete_file(old_item.get("path"))

    item = queue.pop(0)
    if not queue:
        queues.pop(chat_id, None)

    await play_file(chat_id, item["path"], item["title"])
    return True

# =========================================================
# رسالة المساعدة
# =========================================================

HELP_TEXT = """
🌿 **مشغل القرآن الكريم**

━━━━━━━━━━━━━━━━━━━━

📖 **طريقة التشغيل**
أرسل ملف السورة إلى القناة أو المجموعة.
ثم قم بالرد (Reply) على الملف واكتب:
`/تشغيل`

━━━━━━━━━━━━━━━━━━━━

🎧 **الأوامر المتاحة**

▶️ `/تشغيل` - تشغيل الملف المحدد بالرد.
➕ `/إضافة` - إضافة السورة للانتظار.
⏭️ `/التالي` - تشغيل المقطع التالي.
⏸️ `/مؤقت` - إيقاف مؤقت للتشغيل.
▶️ `/استئناف` - استئناف التشغيل.
⏹️ `/إيقاف` - إيقاف التشغيل نهائياً.
📋 `/القائمة` - عرض قائمة الانتظار.
📊 `/الحالة` - عرض حالة المشغل الحالية.
🗑️ `/مسح` - تفريغ قائمة الانتظار.
❓ `/مساعدة` - عرض قائمة المساعدة.
"""

# =========================================================
# الأوامر والأزرار
# =========================================================

@app.on_message(filters.command("start", prefixes="/"))
async def start_command(client, message: Message):
    if not is_admin(message):
        return

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📖 الأوامر", callback_data="help"),
            InlineKeyboardButton("📊 الحالة", callback_data="status"),
        ]
    ])

    await message.reply_text(
        "🌿 **أهلًا بك في مشغل القرآن الكريم**\n\nقم بالرد على أي ملف صوتي بـ `/تشغيل` لبدء البث.",
        reply_markup=keyboard,
    )

@app.on_callback_query()
async def callback_handler(client, query: CallbackQuery):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("عذراً، هذا الأمر للمشرفين فقط.", show_alert=True)
        return

    if query.data == "help":
        await query.message.reply_text(HELP_TEXT)
        await query.answer()
    elif query.data == "status":
        chat_id = query.message.chat.id
        curr = current.get(chat_id)
        if curr:
            status_text = f"▶️ **يعمل حالياً:** {curr['title']}"
        else:
            status_text = "⏹️ **المشغل متوقف حالياً.**"
        await query.message.reply_text(status_text)
        await query.answer()

@app.on_message(filters.incoming | filters.outgoing)
async def command_handler(client, message: Message):
    if not is_admin(message):
        return

    text = (message.text or message.caption or "").strip()
    if not text.startswith("/"):
        return

    command = text.split()[0][1:]
    if "@" in command:
        command = command.split("@")[0]
    command = normalize(command)

    aliases = {
        "مساعدة": "help", "الاوامر": "help", "الأوامر": "help",
        "تشغيل": "play", "شغل": "play",
        "إضافة": "add", "اضافة": "add",
        "التالي": "next", "التالى": "next",
        "مؤقت": "pause",
        "استئناف": "resume",
        "إيقاف": "stop", "ايقاف": "stop",
        "القائمة": "queue",
        "الحالة": "status",
        "مسح": "clear",
    }

    command = aliases.get(command, command)
    chat_id = message.chat.id

    # 1. مساعدة
    if command == "help":
        await message.reply_text(HELP_TEXT)
        return

    # 2. تشغيل
    if command == "play":
        media_msg = get_replied_media(message)
        if not media_msg:
            await message.reply_text("❌ قم بالرد (Reply) على الملف الصوتي المراد تشغيله.")
            return

        status_msg = await message.reply_text("⏳ جاري تنزيل الملف وتشغيله...")
        try:
            file_path = await download_media(media_msg)
            title = get_media_title(media_msg)
            await play_file(chat_id, file_path, title)
            await status_msg.edit_text(f"▶️ **تم بدء التشغيل:**\n`{title}`")
        except Exception as e:
            logger.error("خطأ أثناء التشغيل: %s", e)
            await status_msg.edit_text(f"❌ حدث خطأ أثناء التشغيل: {e}")
        return

    # 3. إضافة إلى قائمة الانتظار
    if command == "add":
        media_msg = get_replied_media(message)
        if not media_msg:
            await message.reply_text("❌ قم بالرد على الملف الصوتي لإضافته للقائمة.")
            return

        status_msg = await message.reply_text("⏳ جاري التنزيل والإضافة للقائمة...")
        try:
            file_path = await download_media(media_msg)
            title = get_media_title(media_msg)
            
            if chat_id not in queues:
                queues[chat_id] = []
            
            queues[chat_id].append({"path": file_path, "title": title})
            await status_msg.edit_text(f"➕ **تمت الإضافة للقائمة:**\n`{title}`")
        except Exception as e:
            await status_msg.edit_text(f"❌ حدث خطأ: {e}")
        return

    # 4. التالي
    if command == "next":
        has_next = await play_next(chat_id)
        if has_next:
            curr = current.get(chat_id)
            await message.reply_text(f"⏭️ **تم الانتقال للـ التالي:**\n`{curr['title']}`")
        else:
            await message.reply_text("⏹️ لا توجد مقاطع أخرى في قائمة الانتظار.")
        return

    # 5. إيقاف مؤقت
    if command == "pause":
        if chat_id in current and chat_id not in paused:
            await calls.pause_stream(chat_id)
            paused.add(chat_id)
            await message.reply_text("⏸️ تم الإيقاف المؤقت.")
        else:
            await message.reply_text("⚠️ لا يوجد بث شغال أو هو متوقف بالفعل.")
        return

    # 6. استئناف
    if command == "resume":
        if chat_id in paused:
            await calls.resume_stream(chat_id)
            paused.remove(chat_id)
            await message.reply_text("▶️ تم استئناف التشغيل.")
        else:
            await message.reply_text("⚠️ البث ليس في حالة إيقاف مؤقت.")
        return

    # 7. إيقاف
    if command == "stop":
        await stop_player(chat_id)
        await message.reply_text("⏹️ تم إيقاف التشغيل وتنظيف القائمة.")
        return

    # 8. عرض القائمة
    if command == "queue":
        queue = queues.get(chat_id, [])
        if not queue:
            await message.reply_text("📋 قائمة الانتظار فارغة.")
            return

        text_out = "📋 **قائمة الانتظار:**\n\n"
        for i, item in enumerate(queue, 1):
            text_out += f"{i}. `{item['title']}`\n"
        await message.reply_text(text_out)
        return

    # 9. تفريغ القائمة
    if command == "clear":
        queue = queues.pop(chat_id, [])
        for item in queue:
            await delete_file(item.get("path"))
        await message.reply_text("🗑️ تم مسح قائمة الانتظار.")
        return

    # 10. الحالة
    if command == "status":
        curr = current.get(chat_id)
        if curr:
            is_p = " (مؤقت)" if chat_id in paused else ""
            q_len = len(queues.get(chat_id, []))
            await message.reply_text(f"📊 **الحالة:**\n▶️ يعمل: `{curr['title']}`{is_p}\n📋 في الانتظار: {q_len}")
        else:
            await message.reply_text("⏹️ لا يوجد أي مقطع يتم تشغيله الآن.")
        return

# =========================================================
# التشغيل الرئيسي
# =========================================================

async def main():
    await app.start()
    await calls.start()
    logger.info("✅ تم تشغيل البوت و PyTgCalls بنجاح.")
    await asyncio.Event().wait()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
