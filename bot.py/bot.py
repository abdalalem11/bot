from telethon import TelegramClient, events
from flask import Flask
import threading
import os
import asyncio

# بيانات الدخول (مباشرة في الكود)
API_ID = 38532428
API_HASH = "bd13b721c96184649dbbce14de78147d"
PHONE_NUMBER = "+966540049081"
OWNER_ID = 1170411845

client = TelegramClient("session", API_ID, API_HASH)

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply('🔥 البوت يعمل بكفاءة!')

@client.on(events.NewMessage(pattern='/clear'))
async def clear(event):
    if event.sender_id == OWNER_ID:
        async for msg in client.iter_messages(event.chat_id, limit=50):
            await msg.delete()
        await event.reply('✅ تم حذف 50 رسالة')

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
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        client.start(phone=PHONE_NUMBER)
        print("✅ البوت متصل بنجاح!")
        client.run_until_disconnected()
    except Exception as e:
        print(f"❌ خطأ: {e}")
        threading.Timer(5, run_bot).start()

if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
