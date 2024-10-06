import os
import logging
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the token from environment variable
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

# Dictionary to store usage statistics
usage_stats = defaultdict(int)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Bot is running! It responds with random GIFs when "lfgg", "LFG", or "lfg" are mentioned. Try /stats to see usage statistics!')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message = update.message.text.lower()
        logger.info(f"Received message: {message}")
        if any(keyword in message for keyword in ['lfgg', 'lfg']):
            logger.info("Keyword detected, sending GIF")
            search_terms = ["celebration", "party", "excited", "let's go"]
            chosen_term = random.choice(search_terms)
            try:
                results = await context.bot.get_inline_query_results(context.bot.id, chosen_term)
                if results:
                    gif = random.choice(results[:5])  # Choose randomly from top 5 results
                    await update.message.reply_animation(gif.gif_url)
                    
                    # Update usage statistics
                    user_id = update.effective_user.id
                    usage_stats[user_id] += 1
                    logger.info(f"GIF sent successfully. User {user_id} stats updated.")
                else:
                    logger.warning("No GIF results found")
                    await update.message.reply_text("Sorry, I couldn't find a suitable GIF at the moment.")
            except Exception as e:
                logger.error(f"Error fetching GIF: {str(e)}")
                await update.message.reply_text("Oops! I encountered an error while fetching a GIF. Please try again later.")
        else:
            logger.info("No keyword detected in message")
    except Exception as e:
        logger.error(f"Error in handle_message: {str(e)}")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_count = usage_stats[user_id]
    total_count = sum(usage_stats.values())
    await update.message.reply_text(f"You've triggered {user_count} GIFs!\nTotal GIFs sent: {total_count}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
    Here are the available commands:
    /start - Start the bot
    /help - Show this help message
    /stats - View your GIF usage statistics
    
    The bot will also respond with a random celebration GIF when you say "LFG" or "LFGG" in a chat.
    """
    await update.message.reply_text(help_text)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Exception while handling an update: {context.error}")

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add error handler
    application.add_error_handler(error_handler)

    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()