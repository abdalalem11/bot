from telethon import TelegramClient, events
from flask import Flask
import threading
import os

# بيانات الدخول (تؤخذ من متغيرات البيئة في Render)
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
PHONE_NUMBER = os.environ.get("PHONE_NUMBER", "")
OWNER_ID = 1170411845  # ايدي المطور ثابت

client = TelegramClient("session", API_ID, API_HASH)

# أمر تشغيل البوت
@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply('🔥 البوت يعمل بكفاءة!')

# أمر حذف الرسائل (للمطور فقط)
@client.on(events.NewMessage(pattern='/clear'))
async def clear(event):
    if event.sender_id == OWNER_ID:
        async for msg in client.iter_messages(event.chat_id, limit=50):
            await msg.delete()
        await event.reply('✅ تم حذف 50 رسالة')

# أمر إرسال رسالة لكل أعضاء المجموعة (مثال خطر)
@client.on(events.NewMessage(pattern='/broadcast (.+)'))
async def broadcast(event):
    if event.sender_id == OWNER_ID:
        msg = event.pattern_match.group(1)
        async for user in client.iter_participants(event.chat_id):
            try:
                await client.send_message(user.id, msg)
            except:
                pass
        await event.reply('✅ تم الإرسال للجميع')

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/health')
def health():
    return "OK", 200

def run_bot():
    client.start(phone=PHONE_NUMBER)
    client.run_until_disconnected()

if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
