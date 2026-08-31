import os
from dotenv import load_dotenv

load_dotenv()

# =========================
# Telegram API
# =========================

_api_id_env = os.environ.get("API_ID")
API_ID = int(_api_id_env) if _api_id_env and _api_id_env.isdigit() else None

API_HASH = os.environ.get("API_HASH")

# =========================
# Pyrogram Session
# =========================

PYROGRAM_SESSION = os.environ.get("PYROGRAM_SESSION")

# =========================
# المشرفون
# =========================

_admin_ids_env = os.environ.get("ADMIN_IDS", "")
ADMIN_IDS = {
    int(user_id.strip())
    for user_id in _admin_ids_env.split(",")
    if user_id.strip().isdigit()
}

# =========================
# مجلد الملفات المؤقتة
# =========================

DOWNLOAD_DIR = os.environ.get("DOWNLOAD_DIR", "./downloads")

# =========================
# التحقق من الإعدادات
# =========================

if not API_ID:
    raise RuntimeError("❌ API_ID غير موجود أو غير صحيح")

if not API_HASH:
    raise RuntimeError("❌ API_HASH غير موجود")

if not PYROGRAM_SESSION:
    raise RuntimeError("❌ PYROGRAM_SESSION غير موجود")

if not ADMIN_IDS:
    raise RuntimeError("❌ ADMIN_IDS غير موجود أو غير صحيح")
