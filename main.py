import os
import logging
import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from collections import defaultdict
import json
import datetime

# User ID to exclude
EXCLUDED_USER_ID = 6474981575

# Dictionary to store usage statistics
usage_stats = defaultdict(int)
gm_stats = defaultdict(int)

# Dictionary to store user activity, initialized with 0 for all users
activity_stats = defaultdict(int)

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
    await update.message.reply_text('bagy Bot is live! Respond with "lfgg", "LFG", or "lfg" to summon a GIF. Use /help for more commands!')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Help command received")
    help_text = """
    🚀 BAGY Bot Commands 🚀
    /start - Activate the bot
    /help - Display this help message
    /stats - Check your LFG count
    /bagyfact - Random bagy fact
    /timer <minutes> - Set a countdown timer
    /memeforecast - Get a meme market forecast
    /bagymath - Calculate potential bagy gains
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

    sorted_activity = sorted(activity_stats.items(), key=lambda x: x[1], reverse=True)[:10]
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
        
        # Track activity for group messages, excluding the specified user
        if update.effective_chat.type in ['group', 'supergroup']:
            user_id = update.effective_user.id
            if user_id != EXCLUDED_USER_ID:
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

async def bagyfact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    facts = [
        "🐸 BAGY is the froggiest meme coin around!",
        "🐸 Did you know there are over 5,000 species of frogs?",
        "🐸 BAGY holders are known for their long, sticky tongues... for catching gains!",
        "🐸 The BAGY community is hopping mad for memes!",
        "🐸 Frogs can leap over 20 times their body length. BAGY to the moon!",
        "🐸 BAGY's mascot is a rare Pepe the Frog with diamond eyes.",
        "🐸 The BAGY team is dedicated to amphibian awareness and blockchain innovation.",
        "🐸 Ribbit! Ribbit! That's the sound of BAGY mooning!",
        "🐸 BAGY holders never have to worry about FUD. They're always chill.",
        "🐸 Join the BAGY community and leap into the future of finance!",
        "🐸 BAGY is decentralized and community-driven. It's controlled by the frogs!",
        "🐸 The BAGY ecosystem is built on a swamp of liquidity.",
        "🐸 BAGY is deflationary. With every transaction, some BAGY tokens disappear into the swamp.",
        "🐸 BAGY is the future of meme coins. It's not just a meme, it's a movement!",
        "🐸 The BAGY community is always happy to welcome new froglings!",
        "🐸 BAGY is the most ribbiting community in the crypto space!",
        "🐸 BAGY is here to stay. It's not just a flash in the pan.",
        "🐸 The BAGY team is always working hard to bring new and innovative features to the community.",
        "🐸 BAGY is more than just a meme coin. It's a way of life.",
        "🐸 Join the BAGY revolution and let's make some noise!",
        "🐸 BAGY is the sound of a thousand frogs cheering for your success!",
        "🐸 The BAGY community is always there to support you, no matter what.",
        "🐸 BAGY is the key to unlocking your financial freedom.",
        "🐸 With BAGY, the sky's the limit. Or should we say, the moon's the limit!",
        "🐸 BAGY is the meme coin that's making a real difference in the world.",
        "🐸 Join the BAGY family and let's make history together!"
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
        "🐸📈 Froggy memes are trending upwards! Bullish on amphibians!",
        "🐸🌪️ Meme monsoon incoming! Prepare your rarest Pepes.",
        "🐸🌡️ Meme temperature: Hot and swampy! Handle with care.",
        "🐸🌈 Double rainbow frog spotted! Extremely rare!",
        "🐸🌙 Lunar leap cycle beginning. Expect ribbiting gains.",
        "🐸🌋 Meme eruption imminent! Brace for viral impact.",
        "🐸🌠 Shooting star meme predicted. Make a wish!",
        "🐸🌪️ Category 5 meme hurricane approaching. Secure your lily pads.",
        "🐸🏜️ Meme drought forecasted. Conserve your froggy GIFs.",
        "🐸🌊 Tsunami of fresh memes incoming. Surf's up!",
        "🐸💎 Froggy diamonds in the rough! Rare Pepes are on the rise.",
        "🐸🐸🐸 Triple froggy moon alignment! Expect astronomical gains.",
        "🐸🚀 Launching to the moon! BAGY is about to blast off.",
        "🐸🌕 Full moon tonight! The frogs are feeling extra bullish.",
        "🐸💰 Golden frog spotted! Get ready for a wave of prosperity.",
        "🐸📈 Upward trend! BAGY is defying gravity.",
        "🐸👑 The frog king has spoken! BAGY is the chosen one.",
        "🐸🔮 The froggy oracle predicts a bright future for BAGY.",
        "🐸🌌 The stars are aligned for BAGY's success.",
        "🐸🌈 A rainbow of gains is appearing on the horizon."
    ]
    await update.message.reply_text(random.choice(forecasts))

async def bagymath(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) != 2:
            raise ValueError("Provide your bagy bag size and a random number for maximum meme accuracy.")
        
        bag_size = float(args[0])
        random_number = float(args[1])
        
        meme_multiplier = random.uniform(1, 1000)
        potential_gain = bag_size * meme_multiplier
        
        await update.message.reply_text(f"🧮 BAGY Math Results:\n"
                                        f"💼 Your BAGY bag: {bag_size}\n"
                                        f"🔢 Your lucky number: {random_number}\n"
                                        f"🚀 Potential BAGY: {potential_gain:.2f}\n"
                                        f"📈 Meme Multiplier: {meme_multiplier:.2f}x\n\n"
                                        f"Disclaimer: This is not financial advice. It's not even advice.")
    except ValueError as e:
        await update.message.reply_text(str(e))
    except Exception as e:
        logger.error(f"Error in bagymath: {str(e)}")
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

# Railway.app specific modifications
def save_stats():
    logger.info(f"Current usage stats: {json.dumps(usage_stats)}")
    logger.info(f"Current GM stats: {json.dumps(gm_stats)}")
    logger.info(f"Current activity stats: {json.dumps(activity_stats)}")

def load_stats():
    global usage_stats, gm_stats, activity_stats
    usage_stats = defaultdict(int)
    gm_stats = defaultdict(int)
    activity_stats = defaultdict(int)

async def webhook(request):
    update = Update.de_json(await request.json(), application.bot)
    await application.process_update(update)
    return 'OK'

if __name__ == '__main__':
    try:
        logger.info("Starting bagy bot initialization...")
        load_stats()
        application = Application.builder().token(TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("stats", stats))
        application.add_handler(CommandHandler("bagyfact", bagyfact))
        application.add_handler(CommandHandler("timer", set_timer))
        application.add_handler(CommandHandler("memeforecast", memeforecast))
        application.add_handler(CommandHandler("bagymath", bagymath))
        application.add_handler(CommandHandler("gmrank", gmrank))
        application.add_handler(CommandHandler("activityrank", activity_rank))  # Updated command
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_error_handler(error_handler)
        
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