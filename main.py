import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the token from environment variable
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Start command received")
    await update.message.reply_text('Bot is running! Use /help for more information.')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Help command received")
    help_text = """
    Here are the available commands:
    /start - Start the bot
    /help - Show this help message
    
    The bot will respond to messages containing "lfg" or "lfgg".
    """
    await update.message.reply_text(help_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message = update.message.text.lower()
        logger.info(f"Received message: {message}")
        if any(keyword in message for keyword in ['lfgg', 'lfg']):
            logger.info("Keyword detected, sending response")
            await update.message.reply_text("LFG! 🎉")
    except Exception as e:
        logger.error(f"Error in handle_message: {str(e)}")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Exception while handling an update: {context.error}")

def main():
    try:
        logger.info("Starting bot initialization...")
        application = Application.builder().token(TOKEN).build()

        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        application.add_error_handler(error_handler)

        logger.info("Handlers added, starting polling...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.critical(f"Critical error during bot startup: {str(e)}")

if __name__ == '__main__':
    main()