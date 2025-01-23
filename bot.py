import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from mega_handler import MegaHandler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Store user sessions
user_sessions = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        "👋 Welcome to Mega Rename Bot!\n\n"
        "Use /login email password to connect your Mega account.\n"
        "After logging in, use /rename to start the renaming process."
    )

async def login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the login command."""
    if len(context.args) != 2:
        await update.message.reply_text(
            "❌ Please provide both email and password.\n"
            "Usage: /login email password"
        )
        return

    email, password = context.args
    
    try:
        mega_handler = MegaHandler(email, password)
        user_sessions[update.effective_user.id] = mega_handler
        await update.message.reply_text(
            "✅ Successfully logged in to Mega!\n"
            "Use /rename to start renaming your files."
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Login failed: {str(e)}")

async def rename(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start the rename process."""
    user_id = update.effective_user.id
    if user_id not in user_sessions:
        await update.message.reply_text(
            "❌ Please login first using /login email password"
        )
        return

    mega_handler = user_sessions[user_id]
    try:
        await update.message.reply_text("🔄 Starting rename process...")
        result = mega_handler.rename_all_files()
        await update.message.reply_text(f"✅ Rename complete!\n\n{result}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error during rename: {str(e)}")

async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the logout command."""
    user_id = update.effective_user.id
    if user_id in user_sessions:
        del user_sessions[user_id]
        await update.message.reply_text("👋 Successfully logged out!")
    else:
        await update.message.reply_text("❌ You're not logged in!")

def main() -> None:
    """Start the bot."""
    # Get bot token from environment variable
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("No bot token provided!")
        return

    application = Application.builder().token(token).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("login", login))
    application.add_handler(CommandHandler("rename", rename))
    application.add_handler(CommandHandler("logout", logout))

    # Start the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()