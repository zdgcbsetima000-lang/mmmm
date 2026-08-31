import os
from dotenv import load_dotenv

load_dotenv()


# =========================
# Telegram API
# =========================

API_ID = int(
    os.environ["API_ID"]
)


API_HASH = os.environ[
    "API_HASH"
]


# =========================
# Pyrogram Session
# =========================

PYROGRAM_SESSION = os.environ[
    "PYROGRAM_SESSION"
]


# =========================
# المشرفون
# =========================

ADMIN_IDS = {
    int(user_id.strip())

    for user_id in os.environ[
        "ADMIN_IDS"
    ].split(",")

    if user_id.strip().isdigit()
}


# =========================
# مجلد الملفات المؤقتة
# =========================

DOWNLOAD_DIR = os.environ.get(
    "DOWNLOAD_DIR",
    "./downloads"
)


# =========================
# التحقق من الإعدادات
# =========================

if not API_ID:
    raise RuntimeError(
        "❌ API_ID غير موجود"
    )


if not API_HASH:
    raise RuntimeError(
        "❌ API_HASH غير موجود"
    )


if not PYROGRAM_SESSION:
    raise RuntimeError(
        "❌ PYROGRAM_SESSION غير موجود"
    )


if not ADMIN_IDS:
    raise RuntimeError(
        "❌ ADMIN_IDS غير موجود"
    )
