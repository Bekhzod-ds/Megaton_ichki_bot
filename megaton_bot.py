import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)
from google_drive import upload_file_to_drive
from google_sheets import insert_screenshot_link

BOT_TOKEN = os.environ.get("BOT_TOKEN")

user_sessions = {}

# --- Start command ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📦 Yetkazmalar", callback_data="Yetkazmalar")],
        [InlineKeyboardButton("💰 To'lovlar", callback_data="Tolovlar")]
    ]
    await update.message.reply_text(
        "Qaysi turdagi buyurtmaga screenshot yuklamoqchisiz?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# --- Handle buttons ---
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.from_user.id

    sheet_type = query.data
    user_sessions[chat_id] = {'type': sheet_type}

    await query.edit_message_text(
        f"{sheet_type} uchun ID raqamini kiriting (masalan: 1)"
    )

# --- Handle text (Order ID input) ---
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_user.id
    if chat_id in user_sessions and 'type' in user_sessions[chat_id]:
        user_sessions[chat_id]['id'] = update.message.text.strip()
        await update.message.reply_text("Endi suratni yuboring (jpg/png)")
    else:
        await update.message.reply_text("/start tugmasini bosib qayta urinib ko'ring.")

# --- Handle photo ---
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_user.id
    if chat_id not in user_sessions or 'id' not in user_sessions[chat_id]:
        await update.message.reply_text("Avval /start buyrug'ini yuboring.")
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
        await update.message.reply_text(f"Xatolik yuz berdi:\n{e}")

# --- Main ---
if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("✅ Bot is running on Render...")
    app.run_polling()
