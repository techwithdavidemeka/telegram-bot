import os
import logging
import random
from telegram import Update, InlineQueryResultGif
from telegram.ext import Application, CommandHandler, MessageHandler, filters, InlineQueryHandler
from collections import defaultdict

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the token from environment variable
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

# Dictionary to store usage statistics
usage_stats = defaultdict(int)

async def start(update: Update, context):
    await update.message.reply_text('Bot is running! It responds with random GIFs when "lfgg", "LFG", or "lfg" are mentioned. Try /stats to see usage statistics!')

async def handle_message(update: Update, context):
    message = update.message.text.lower()
    if any(keyword in message for keyword in ['lfgg', 'lfg']):
        search_terms = ["celebration", "party", "excited", "let's go"]
        chosen_term = random.choice(search_terms)
        results = await context.bot.get_inline_query_results(context.bot.id, chosen_term)
        if results:
            gif = random.choice(results[:5])  # Choose randomly from top 5 results
            await update.message.reply_animation(gif.gif_url)
            
            # Update usage statistics
            user_id = update.effective_user.id
            usage_stats[user_id] += 1

async def inline_query(update: Update, context):
    query = update.inline_query.query
    if not query:
        query = "celebration"  # Default search term
    results = await context.bot.get_inline_query_results(context.bot.id, query)
    await update.inline_query.answer(results[:10])  # Return up to 10 results

async def stats(update: Update, context):
    user_id = update.effective_user.id
    user_count = usage_stats[user_id]
    total_count = sum(usage_stats.values())
    await update.message.reply_text(f"You've triggered {user_count} GIFs!\nTotal GIFs sent: {total_count}")

async def help_command(update: Update, context):
    help_text = """
    Here are the available commands:
    /start - Start the bot
    /help - Show this help message
    /stats - View your GIF usage statistics
    
    The bot will also respond with a random celebration GIF when you say "LFG" or "LFGG" in a chat.
    """
    await update.message.reply_text(help_text)

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(InlineQueryHandler(inline_query))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()