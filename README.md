# 🌿 مشغل القرآن الكريم

مشغل تلاوات من ملفات Telegram.

## طريقة التشغيل

أرسل ملف سورة MP3 في القناة أو المجموعة.

اعمل Reply على الملف.

ثم اكتب:

/تشغيل

سيتم تشغيل نفس الملف في Voice Chat.

## الأوامر

/تشغيل
/إضافة
/التالي
/مؤقت
/استئناف
/إيقاف
/القائمة
/الحالة
/مسح
/مساعدة

## الإعدادات

يتم وضع بيانات Telegram وSession في ملف `.env` على السيرفر.

مثال:

API_ID=12345678
API_HASH=xxxxxxxx
PYROGRAM_SESSION=xxxxxxxx
ADMIN_IDS=123456789
DOWNLOAD_DIR=./downloads

## التثبيت

sudo apt update

sudo apt install -y python3 python3-venv ffmpeg

python3 -m venv venv

source venv/bin/activate

pip install -U pip wheel

pip install -r requirements.txt

cp env.txt .env

nano .env

python3 main.py

## الأمان

لا ترفع `.env` أو Session String إلى GitHub.

لا تشارك Session String مع أي شخص.

ملفات القرآن لا يتم تخزينها داخل GitHub.
يتم تنزيل الملف المطلوب مؤقتًا على السيرفر أثناء التشغيل.
