import os
import logging
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from collections import defaultdict

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the token from environment variable
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

# Dictionary to store usage statistics
usage_stats = defaultdict(int)

# List of predefined GIF URLs
GIF_URLS = [
    "https://media.giphy.com/media/b7G6XGYnsTZsxgo11z/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZmI5Mm4xYWhoZGxjcngzYXBxamNxMjl0YTFvaGxsM3B6ZWVseHp1aSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/sl1zfWPqlozOgquzuE/giphy.gif",
    "https://media.giphy.com/media/0IWeBirDeRK4dG0Egl/giphy.gif?cid=790b7611kpgr4b0wbzpc5mvp8yk7ce4vuo2m65cdou5schfi&ep=v1_gifs_search&rid=giphy.gif&ct=g",
    "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExa20wa3QwZmw5dndta2Vibm9oYTd2b2R2bGQxb2V6bWI2NDl2eXU4bSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/4Ivaq5OHdKovVV9KCz/giphy.gif",
    "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExaDBiNjcwODV0dnE1eTl2OWh3bms3cmR2bTkxaGN3M3ExeGxjMnR2diZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/tyxovVLbfZdok/giphy.gif"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Start command received")
    await update.message.reply_text('Bot is running! It responds with random GIFs when "lfgg", "LFG", or "lfg" are mentioned. Try /stats to see usage statistics!')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Help command received")
    help_text = """
    Here are the available commands:
    /start - Start the bot
    /help - Show this help message
    /stats - View your GIF usage statistics
    
    The bot will respond with a random celebration GIF when you say "LFG" or "LFGG" in a chat.
    """
    await update.message.reply_text(help_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message = update.message.text.lower()
        logger.info(f"Received message: {message}")
        if any(keyword in message for keyword in ['lfgg', 'lfg']):
            logger.info("Keyword detected, sending GIF")
            gif_url = random.choice(GIF_URLS)
            await update.message.reply_animation(gif_url)
            
            # Update usage statistics
            user_id = update.effective_user.id
            usage_stats[user_id] += 1
            logger.info(f"GIF sent successfully. User {user_id} stats updated.")
    except Exception as e:
        logger.error(f"Error in handle_message: {str(e)}")
        await update.message.reply_text("Oops! I encountered an error while sending a GIF. Please try again later.")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_count = usage_stats[user_id]
    total_count = sum(usage_stats.values())
    await update.message.reply_text(f"You've triggered {user_count} GIFs!\nTotal GIFs sent: {total_count}")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Exception while handling an update: {context.error}")

def main():
    try:
        logger.info("Starting bot initialization...")
        application = Application.builder().token(TOKEN).build()

        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("stats", stats))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        application.add_error_handler(error_handler)

        logger.info("Handlers added, starting polling...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.critical(f"Critical error during bot startup: {str(e)}")

if __name__ == '__main__':
    main()