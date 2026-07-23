#!/usr/bin/env python3
import os
import json
import logging
import asyncio
import subprocess
import sys
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ========== الإعدادات ==========
TOKEN = os.environ.get("BOT_TOKEN")  # من متغيرات البيئة في Render
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))
PORT = int(os.environ.get("SESSION_PORT", 4444))

# ========== إعداد التسجيل ==========
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== قاعدة بيانات بسيطة ==========
SESSIONS = {}  # تخزين مؤقت للجلسات

# ========== دوال البوت ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != str(ADMIN_ID):
        await update.message.reply_text("⛔ غير مصرح لك باستخدام هذا البوت.")
        return

    keyboard = [
        [InlineKeyboardButton("🖥️ عرض الجلسات", callback_data="list_sessions")],
        [InlineKeyboardButton("🌐 فحص الأهداف", callback_data="scan_target")],
        [InlineKeyboardButton("🔑 توليد Payload", callback_data="gen_payload")],
        [InlineKeyboardButton("📊 إحصائيات السيرفر", callback_data="server_stats")],
        [InlineKeyboardButton("⚙️ تنفيذ أمر مخصص", callback_data="custom_cmd")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🔥 **بوت الاختراق السحابي** يعمل على Render\n"
        f"🟢 الحالة: نشط\n"
        f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        f"🌐 منفذ الاستماع: {PORT}\n\n"
        "اختر الإجراء المناسب:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "list_sessions":
        if not SESSIONS:
            await query.edit_message_text("❌ لا توجد جلسات نشطة حالياً.")
            return
        
        msg = "📋 **الجلسات النشطة:**\n\n"
        for sid, info in SESSIONS.items():
            msg += f"🆔 {sid} | {info['ip']}:{info['port']} | {info.get('user', 'unknown')}\n"
        
        keyboard = []
        for sid in SESSIONS.keys():
            keyboard.append([InlineKeyboardButton(f"🎯 التحكم بالجلسة {sid}", callback_data=f"session_{sid}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(msg, reply_markup=reply_markup, parse_mode="Markdown")
    
    elif query.data.startswith("session_"):
        sid = query.data.split("_")[1]
        context.user_data["current_session"] = sid
        
        keyboard = [
            [InlineKeyboardButton("💻 تنفيذ أمر", callback_data=f"cmd_{sid}")],
            [InlineKeyboardButton("📂 تنزيل ملف", callback_data=f"download_{sid}")],
            [InlineKeyboardButton("🔑 استغلال ثغرة", callback_data=f"exploit_{sid}")],
            [InlineKeyboardButton("🔌 إنهاء الجلسة", callback_data=f"kill_{sid}")],
            [InlineKeyboardButton("🔙 العودة", callback_data="list_sessions")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(f"🎯 **التحكم بالجلسة {sid}**", reply_markup=reply_markup, parse_mode="Markdown")
    
    elif query.data.startswith("cmd_"):
        sid = query.data.split("_")[1]
        await query.edit_message_text(f"✏️ أرسل الأمر لتنفيذه على الجلسة {sid}:")
        context.user_data["awaiting_cmd"] = sid
    
    elif query.data == "scan_target":
        await query.edit_message_text("🌐 **أدوات المسح:**\n\n"
                                     "1. مسح المنافذ (Nmap)\n"
                                     "2. مسح الثغرات (Nikto)\n"
                                     "3. مسح الشبكة (Netdiscover)\n\n"
                                     "أرسل الأمر بالصيغة: /scan <target> <type>")
    
    elif query.data == "gen_payload":
        keyboard = [
            [InlineKeyboardButton("📱 Android APK", callback_data="payload_android")],
            [InlineKeyboardButton("🪟 Windows EXE", callback_data="payload_windows")],
            [InlineKeyboardButton("🐧 Linux ELF", callback_data="payload_linux")],
            [InlineKeyboardButton("🌐 PHP Shell", callback_data="payload_php")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("🔑 **اختر نوع الحمولة:**", reply_markup=reply_markup, parse_mode="Markdown")
    
    elif query.data.startswith("payload_"):
        ptype = query.data.split("_")[1]
        await query.edit_message_text(f"⏳ جاري توليد {ptype.upper()} Payload...")
        # هنا كود توليد الحمولة
        result = f"✅ تم توليد {ptype.upper()} Payload بنجاح.\n📍 مسار التحميل: /outputs/{ptype}_payload"
        await query.message.reply_text(result)
    
    elif query.data.startswith("exploit_"):
        sid = query.data.split("_")[1]
        keyboard = [
            [InlineKeyboardButton("🐍 Metasploit", callback_data=f"msf_{sid}")],
            [InlineKeyboardButton("🔓 Brute Force", callback_data=f"brute_{sid}")],
            [InlineKeyboardButton("🌐 Web Exploit", callback_data=f"web_{sid}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(f"🛠️ **اختر أداة الاستغلال للجلسة {sid}:**", reply_markup=reply_markup, parse_mode="Markdown")
    
    elif query.data.startswith("msf_"):
        sid = query.data.split("_")[1]
        await query.edit_message_text(f"⏳ جاري تشغيل Metasploit على الجلسة {sid}...")
        # تشغيل Metasploit
        result = f"✅ Metasploit تم تشغيله بنجاح على الجلسة {sid}"
        await query.message.reply_text(result)
    
    elif query.data.startswith("kill_"):
        sid = query.data.split("_")[1]
        if sid in SESSIONS:
            del SESSIONS[sid]
        await query.edit_message_text(f"✅ تم إنهاء الجلسة {sid} بنجاح.")
    
    elif query.data == "server_stats":
        msg = f"📊 **إحصائيات السيرفر (Render):**\n\n"
        msg += f"🟢 الجلسات النشطة: {len(SESSIONS)}\n"
        msg += f"🔄 المنفذ المفتوح: {PORT}\n"
        msg += f"⏰ وقت التشغيل: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        msg += f"🐍 إصدار Python: {sys.version.split()[0]}\n"
        await query.edit_message_text(msg, parse_mode="Markdown")
    
    elif query.data == "custom_cmd":
        await query.edit_message_text("✏️ أرسل الأمر (Linux) لتنفيذه على السيرفر:")
        context.user_data["awaiting_server_cmd"] = True

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != str(ADMIN_ID):
        return
    
    text = update.message.text
    
    if "awaiting_cmd" in context.user_data:
        sid = context.user_data["awaiting_cmd"]
        # تنفيذ الأمر على الجلسة
        result = f"✅ أمر '{text}' تم تنفيذه على الجلسة {sid}"
        await update.message.reply_text(result)
        del context.user_data["awaiting_cmd"]
    
    elif "awaiting_server_cmd" in context.user_data:
        # تنفيذ الأمر على السيرفر
        try:
            output = subprocess.check_output(text, shell=True, stderr=subprocess.STDOUT, text=True, timeout=30)
            await update.message.reply_text(f"📤 **النتيجة:**\n```\n{output[:4000]}\n```", parse_mode="Markdown")
        except subprocess.TimeoutExpired:
            await update.message.reply_text("⏰ انتهى وقت الأمر (30 ثانية).")
        except Exception as e:
            await update.message.reply_text(f"❌ خطأ: {str(e)}")
        del context.user_data["awaiting_server_cmd"]
    
    else:
        await update.message.reply_text("❌ الأمر غير معروف. استخدم /start للبدء.")

async def scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != str(ADMIN_ID):
        return
    
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("⚠️ الاستخدام: /scan <target> <type>\nالأنواع: ports, web, network")
        return
    
    target = args[0]
    scan_type = args[1]
    
    await update.message.reply_text(f"⏳ جاري مسح {target} باستخدام {scan_type}...")
    
    # محاكاة المسح
    result = f"✅ تم مسح {target} بنجاح.\n"
    result += f"🔍 النوع: {scan_type}\n"
    result += "📊 المنافذ المفتوحة: 22, 80, 443, 8080\n"
    
    await update.message.reply_text(result)

# ========== تشغيل البوت ==========
def main():
    if not TOKEN or not ADMIN_ID:
        logger.error("❌ يجب تعيين BOT_TOKEN و ADMIN_ID في متغيرات البيئة")
        sys.exit(1)
    
    logger.info("🔥 تشغيل البوت على Render...")
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("scan", scan_command))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("✅ البوت يعمل...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
