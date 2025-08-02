import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)
from google_drive import upload_file_to_drive
from google_sheets import insert_screenshot_link

BOT_TOKEN = os.environ["BOT_TOKEN"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]
PORT = int(os.environ.get("PORT", 8443))

user_sessions = {}

# --- Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📦 Yetkazmalar", callback_data="Yetkazmalar")],
        [InlineKeyboardButton("💰 To'lovlar", callback_data="Tolovlar")]
    ]
    await update.message.reply_text(
        "Qaysi turdagi buyurtmaga screenshot yuklamoqchisiz?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.from_user.id
    user_sessions[chat_id] = {'type': query.data}
    await query.edit_message_text(f"{query.data} uchun ID raqamini kiriting (masalan: 1)")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_user.id
    if chat_id in user_sessions and 'type' in user_sessions[chat_id]:
        user_sessions[chat_id]['id'] = update.message.text.strip()
        await update.message.reply_text("✅ Endi suratni yuboring (jpg/png)")
    else:
        await update.message.reply_text("⚠️ Iltimos, avval /start buyrug'ini bosing.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_user.id
    if chat_id not in user_sessions or 'id' not in user_sessions[chat_id]:
        await update.message.reply_text("⚠️ Avval /start buyrug'ini yuboring.")
        return

    folder_type = user_sessions[chat_id]['type']
    row_id = user_sessions[chat_id]['id']
    photo = update.message.photo[-1]
    file = await photo.get_file()

    filename = f"{folder_type}_{row_id}.jpg"
    temp_path = f"/tmp/{filename}"
    await file.download_to_drive(temp_path)

    try:
        drive_link = upload_file_to_drive(folder_type, filename, temp_path)
        insert_screenshot_link(folder_type, row_id, drive_link)
        await update.message.reply_text("✅ Screenshot yuklandi va jadvalga qo'shildi.")
    except Exception as e:
        await update.message.reply_text(f"❌ Xatolik yuz berdi:\n{e}")

# --- Entry Point ---
async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    await app.bot.set_webhook(url=WEBHOOK_URL)
    print(f"✅ Webhook set at {WEBHOOK_URL}")
    await app.run_webhook(listen="0.0.0.0", port=PORT, webhook_url=WEBHOOK_URL)

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())
