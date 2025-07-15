from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from google_drive import upload_file_to_drive
import os
from google_sheets import insert_screenshot_link
import traceback

TOKEN = "7958303937:AAFt0srBeyPyvX0Gsp7MAyaFChlYWvfK9Io"

# START command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["📦 Yetkazmalar", "💰 To‘lovlar"]]
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Qaysi turdagi screenshot yuboriladi?", reply_markup=markup)
    context.user_data.clear()

# Handle text inputs (type + ID)
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text in ["📦 Yetkazmalar", "💰 To‘lovlar"]:
        context.user_data['type'] = 'Yetkazmalar' if "Yetkazmalar" in text else "To'lovlar"
        await update.message.reply_text("ID raqamini yuboring (faqat raqam):")
    
    elif text.isdigit() and 'type' in context.user_data:
        context.user_data['id'] = text
        await update.message.reply_text("✅ Qabul qilindi!\nEndi screenshot rasmni yuboring.")
    
    else:
        await update.message.reply_text("Noto‘g‘ri format. Iltimos, /start buyrug‘i bilan qayta urinib ko‘ring.")

# Handle photo uploads
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()

    folder_type = context.user_data.get("type")
    row_id = context.user_data.get("id")

    if not folder_type or not row_id:
        await update.message.reply_text("Avval /start orqali tur va ID yuboring.")
        return

    filename = f"{folder_type}_{row_id}.jpg"
    temp_path = f"/tmp/{filename}"

    await file.download_to_drive(custom_path=temp_path)

    try:
        from google_drive import upload_file_to_drive
        from google_sheets import insert_screenshot_link

        drive_link = upload_file_to_drive(temp_path, filename, folder_type)
        insert_screenshot_link(folder_type, row_id, drive_link)

        await update.message.reply_text(f"📎 Screenshot saqlandi:\n{drive_link}")
    except Exception as e:
        print(traceback.format_exc())  # 👈 print full stack trace to terminal
        await update.message.reply_text(f"Xatolik yuz berdi:\n{e}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
# Main runner
if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("Bot is running...")
    app.run_polling()
