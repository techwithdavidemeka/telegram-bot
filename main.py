import os
import logging
import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from collections import defaultdict
import json
import datetime

activity_stats = defaultdict(int)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the token from environment variable
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

# Dictionary to store usage statistics
usage_stats = defaultdict(int)
gm_stats = defaultdict(int)

# List of meme coin related GIF URLs
GIF_URLS = [
    "https://media.giphy.com/media/b7G6XGYnsTZsxgo11z/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZmI5Mm4xYWhoZGxjcngzYXBxamNxMjl0YTFvaGxsM3B6ZWVseHp1aSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/sl1zfWPqlozOgquzuE/giphy.gif",
    "https://media.giphy.com/media/0IWeBirDeRK4dG0Egl/giphy.gif?cid=790b7611kpgr4b0wbzpc5mvp8yk7ce4vuo2m65cdou5schfi&ep=v1_gifs_search&rid=giphy.gif&ct=g",
    "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExa20wa3QwZmw5dndta2Vibm9oYTd2b2R2bGQxb2V6bWI2NDl2eXU4bSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/4Ivaq5OHdKovVV9KCz/giphy.gif",
    "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExaDBiNjcwODV0dnE1eTl2OWh3bms3cmR2bTkxaGN3M3ExeGxjMnR2diZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/tyxovVLbfZdok/giphy.gif",
    "https://media.giphy.com/media/LEdz8xl9uFxKw/giphy.gif?cid=ecf05e47r110os066y43ac5ognfx5i28yoxu47ohska5li1l&ep=v1_gifs_search&rid=giphy.gif&ct=g",
    "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcHJoYzh0NWZiamdkdWpmanEyYjdwa3pjczcxa3Vka2tyNzZqb2FvbSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/3ohhwfAa9rbXaZe86c/giphy.gif"
]

# Custom exceptions
class InvalidTimerDuration(Exception):
    pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Start command received")
    await update.message.reply_text('ATH Bot is live! Respond with "lfgg", "LFG", or "lfg" to summon a GIF. Use /help for more commands!')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Help command received")
    help_text = """
    🚀 ATH (All Time Happiness) Bot Commands 🚀
    /start - Activate the bot
    /help - Display this help message
    /stats - Check your LFG count
    /athfact - Random ATH fact
    /timer <minutes> - Set a countdown timer
    /memeforecast - Get a meme market forecast
    /athmath - Calculate potential ATH gains
    /gmrank - See the GM leaderboard
    /activityrank - See the most active members leaderboard
    
    The bot responds with a random GIF when you say "LFG" or "LFGG" in the chat.
    Don't forget to say "GM" to climb the leaderboard!
    """
    await update.message.reply_text(help_text)

async def activity_rank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    # Check if the user is an admin
    try:
        user_status = await context.bot.get_chat_member(chat.id, user.id)
        if user_status.status not in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
            await update.message.reply_text("Umm, you don't seem to be an admin. This command is for admins only!")
            return
    except Exception as e:
        logger.error(f"Error checking admin status: {str(e)}")
        await update.message.reply_text("An error occurred while checking your permissions. Please try again later.")
        return

    # Filter out the specified user ID and sort the activity stats
    filtered_activity = {user_id: count for user_id, count in activity_stats.items() if user_id != 6474981575}
    sorted_activity = sorted(filtered_activity.items(), key=lambda x: x[1], reverse=True)[:10]
    
    leaderboard = "🏆 Most Active Members Leaderboard 🏆\n\n"
    for i, (user_id, count) in enumerate(sorted_activity, 1):
        try:
            user = await context.bot.get_chat(user_id)
            name = user.first_name or f"User {user_id}"
        except Exception:
            name = f"User {user_id}"
        leaderboard += f"{i}. {name}: {count} messages\n"
    await update.message.reply_text(leaderboard)


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_count = usage_stats[user_id]
    total_count = sum(usage_stats.values())
    await update.message.reply_text(f"🚀 Your LFG count: {user_count}\n💎 Community LFG total: {total_count}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message = update.message.text.lower()
        logger.info(f"Received message: {message}")
        
        # Track activity for group messages
        if update.effective_chat.type in ['group', 'supergroup']:
            user_id = update.effective_user.id
            activity_stats[user_id] += 1
            logger.info(f"Activity recorded for user {user_id} in group chat")
        
        if any(keyword in message for keyword in ['lfgg', 'lfg']):
            logger.info("Keyword detected, sending GIF")
            gif_url = random.choice(GIF_URLS)
            await update.message.reply_animation(gif_url)
            
            # Update usage statistics
            user_id = update.effective_user.id
            usage_stats[user_id] += 1
            logger.info(f"GIF sent successfully. User {user_id} stats updated.")
        elif message == 'gm' and update.effective_chat.type in ['group', 'supergroup']:
            user_id = update.effective_user.id
            gm_stats[user_id] += 1
            logger.info(f"GM recorded for user {user_id} in group chat")
    except Exception as e:
        logger.error(f"Error in handle_message: {str(e)}")
        await update.message.reply_text("Oops! Error processing message. Try again later.")

async def athfact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    facts = [
        "ATH stands for All Time Happiness, not All Time High!",
        "ATH was created by a team of meme enthusiasts.",
        "ATH's whitepaper was written entirely in emojis.",
        "The first ATH transaction was to buy a virtual pet rock.",
        "ATH's blockchain runs on the power of memes.",
        "In the ATH ecosystem, 1 ATH will always equal 1 ATH.",
        "ATH's logo was designed by a blind artist for maximum randomness.",
        "The ATH team promises to never take themselves too seriously.",
        "ATH's market cap is measured in units of pure vibes."
    ]
    await update.message.reply_text(random.choice(facts))

async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if not args or len(args) != 1:
            raise InvalidTimerDuration("Provide a single number for the timer in minutes.")
        
        duration = int(args[0]) * 60  # Convert to seconds
        if duration <= 0:
            raise InvalidTimerDuration("Timer duration must be positive.")
        
        await update.message.reply_text(f"⏰ Timer set for {args[0]} minutes. HODL tight!")
        await asyncio.sleep(duration)
        await update.message.reply_text("⏰ Time's up! LFG! 🚀")
    except InvalidTimerDuration as e:
        await update.message.reply_text(str(e))
    except ValueError:
        await update.message.reply_text("Please provide a valid number for the timer duration.")
    except Exception as e:
        logger.error(f"Error in set_timer: {str(e)}")
        await update.message.reply_text("Timer error. Devs probably fell asleep.")

async def memeforecast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    forecasts = [
        "📈 ATH memes trending upward. Bullish on laughter.",
        "🌪️ Meme storm incoming. Prepare your best GIFs.",
        "🌡️ Meme temperature: Spicy. Handle with care.",
        "🌈 Double rainbow meme spotted. Extremely rare!",
        "🌙 Lunar meme cycle beginning. Expect howling.",
        "🌋 Meme eruption imminent. Brace for viral impact.",
        "🌠 Shooting star meme predicted. Make a wish.",
        "🌪️ Category 5 meme hurricane approaching. Secure your bags.",
        "🏜️ Meme drought forecasted. Conserve your rare Pepes.",
        "🌊 Tsunami of fresh memes incoming. Surf's up!"
    ]
    await update.message.reply_text(random.choice(forecasts))

async def athmath(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) != 2:
            raise ValueError("Provide your ATH bag size and a random number for maximum meme accuracy.")
        
        bag_size = float(args[0])
        random_number = float(args[1])
        
        meme_multiplier = random.uniform(1, 1000)
        potential_gain = bag_size * meme_multiplier
        
        await update.message.reply_text(f"🧮 ATH Math Results:\n"
                                        f"💼 Your ATH bag: {bag_size}\n"
                                        f"🔢 Your lucky number: {random_number}\n"
                                        f"🚀 Potential ATH: {potential_gain:.2f}\n"
                                        f"📈 Meme Multiplier: {meme_multiplier:.2f}x\n\n"
                                        f"Disclaimer: This is not financial advice. It's not even advice.")
    except ValueError as e:
        await update.message.reply_text(str(e))
    except Exception as e:
        logger.error(f"Error in athmath: {str(e)}")
        await update.message.reply_text("Math error. Looks like we divided by zero.")

async def gmrank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sorted_gm = sorted(gm_stats.items(), key=lambda x: x[1], reverse=True)[:10]
    leaderboard = "🌅 GM Leaderboard 🌅\n\n"
    for i, (user_id, count) in enumerate(sorted_gm, 1):
        try:
            user = await context.bot.get_chat(user_id)
            name = user.first_name or f"User {user_id}"
        except Exception:
            name = f"User {user_id}"
        leaderboard += f"{i}. {name}: {count} GMs\n"
    await update.message.reply_text(leaderboard)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Exception while handling an update: {context.error}")

# File paths for storing stats
PERSISTENT_STORAGE_PATH = os.environ.get('RAILWAY_VOLUME_MOUNT_PATH', '')
USAGE_STATS_FILE = os.path.join(PERSISTENT_STORAGE_PATH, 'usage_stats.json')
GM_STATS_FILE = os.path.join(PERSISTENT_STORAGE_PATH, 'gm_stats.json')
ACTIVITY_STATS_FILE = os.path.join(PERSISTENT_STORAGE_PATH, 'activity_stats.json')

# Function to save stats to file
def save_stats_to_file(stats, filename):
    with open(filename, 'w') as f:
        json.dump(stats, f)

# Function to load stats from file
def load_stats_from_file(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return defaultdict(int, json.load(f))
    return defaultdict(int)

# Function to periodically save stats
async def periodic_save(interval=300):  # Save every 5 minutes
    while True:
        await asyncio.sleep(interval)
        save_stats()

# Railway.app specific modifications
def save_stats():
    save_stats_to_file(usage_stats, USAGE_STATS_FILE)
    save_stats_to_file(gm_stats, GM_STATS_FILE)
    save_stats_to_file(activity_stats, ACTIVITY_STATS_FILE)
    logger.info("Stats saved to files")

# Updated load_stats function
def load_stats():
    global usage_stats, gm_stats, activity_stats
    usage_stats = load_stats_from_file(USAGE_STATS_FILE)
    gm_stats = load_stats_from_file(GM_STATS_FILE)
    activity_stats = load_stats_from_file(ACTIVITY_STATS_FILE)
    logger.info("Stats loaded from files")


async def webhook(request):
    update = Update.de_json(await request.json(), application.bot)
    await application.process_update(update)
    return 'OK'

if __name__ == '__main__':
    try:
        logger.info("Starting ATH bot initialization...")
        load_stats()
        application = Application.builder().token(TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("stats", stats))
        application.add_handler(CommandHandler("athfact", athfact))
        application.add_handler(CommandHandler("timer", set_timer))
        application.add_handler(CommandHandler("memeforecast", memeforecast))
        application.add_handler(CommandHandler("athmath", athmath))
        application.add_handler(CommandHandler("gmrank", gmrank))
        application.add_handler(CommandHandler("activityrank", activity_rank))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_error_handler(error_handler)
        
        # Set up periodic save
        application.create_task(periodic_save())
        
        # Set up webhook
        PORT = int(os.environ.get('PORT', '8080'))
        WEBHOOK_URL = os.environ.get('WEBHOOK_URL')
        
        if WEBHOOK_URL:
            application.run_webhook(listen="0.0.0.0", port=PORT, webhook_url=WEBHOOK_URL)
        else:
            logger.info("WEBHOOK_URL not set. Running in polling mode...")
            application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.critical(f"Critical error during bot startup: {str(e)}")
    finally:
        save_stats()