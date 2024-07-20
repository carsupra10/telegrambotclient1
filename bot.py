import logging
import json
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.error import TelegramError

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Replace with your actual bot token
BOT_TOKEN = '7004322427:AAHJJ_On93IGS5IlYIWXjm1Nj1zN8K7FzQQ'
USER_IDS_FILE = 'user_ids.json'
ADMIN_USER_ID = 6583101990  # Replace with the admin's user ID

# Load user IDs from file
def load_user_ids():
    try:
        with open(USER_IDS_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Save user IDs to file
def save_user_ids(user_ids):
    with open(USER_IDS_FILE, 'w') as file:
        json.dump(user_ids, file)

user_ids = load_user_ids()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_ids:
        user_ids.append(user_id)
        save_user_ids(user_ids)

    kb = [
        [KeyboardButton("Show me Chatwell!", web_app=WebAppInfo("https://chatwell-beta.onrender.com/"))]
    ]
    await update.message.reply_text("Let's do this...", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def notify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_USER_ID:
        await update.message.reply_text("You are not authorized to send notifications.")
        return

    args = context.args
    if not args:
        await update.message.reply_text("Usage: /notify <text|photo|video> <content>")
        return

    message_type = args[0].lower()
    content = ' '.join(args[1:])

    for user_id in user_ids:
        try:
            if message_type == 'text':
                await context.bot.send_message(chat_id=user_id, text=content)

            elif message_type == 'photo':
                await context.bot.send_photo(chat_id=user_id, photo=content, caption="Photo notification")

            elif message_type == 'video':
                await context.bot.send_video(chat_id=user_id, video=content, caption="Video notification")

            else:
                await update.message.reply_text("Unknown type. Use text, photo, or video.")

        except TelegramError as e:
            logger.error(f"Failed to send message to {user_id}: {e}")
            # Optionally remove user_id from the list if needed
            # user_ids.remove(user_id)
            # save_user_ids(user_ids)

async def handle_errors(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")
    await update.message.reply_text("An error occurred. Please try again later.")

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("notify", notify))
    application.add_error_handler(handle_errors)

    application.run_polling()

if __name__ == '__main__':
    main()
