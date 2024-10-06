import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the token from environment variable
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

# Get the GIF URL from environment variable
GIF_URL = os.environ.get('GIF_URL')

async def start(update: Update, context):
    await update.message.reply_text('Bot is running! It will respond with a GIF when "lfgg", "LFG", or "lfg" are mentioned in the group.')

async def handle_message(update: Update, context):
    message = update.message.text.lower()
    if any(keyword in message for keyword in ['lfgg', 'lfg']):
        await update.message.reply_animation(GIF_URL)

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
