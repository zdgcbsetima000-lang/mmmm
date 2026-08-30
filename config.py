Enterimport os

from dotenv import load_dotenv


load_dotenv()


API_ID = int(
    os.getenv(
        "API_ID",
        "0"
    )
)


API_HASH = os.getenv(
    "API_HASH",
    ""
)


SESSION_NAME = os.getenv(
    "SESSION_NAME",
    "quran_player_ar"
)


ADMIN_IDS = {
    int(x.strip())

    for x in os.getenv(
        "ADMIN_IDS",
        ""
    ).split(",")

    if x.strip().isdigit()
}


DOWNLOAD_DIR = os.getenv(
    "DOWNLOAD_DIR",
    "./downloads"
)


if not API_ID:

    raise RuntimeError(
        "ضع API_ID داخل ملف .env"
    )


if not API_HASH:

    raise RuntimeError(
        "ضع API_HASH داخل ملف .env"
    )


if not ADMIN_IDS:

    raise RuntimeError(
        "ضع Telegram User ID داخل ADMIN_IDS"
    )
