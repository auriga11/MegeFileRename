import os
from pyrogram import Client, filters
from mega import Mega
from logging import info as log_info
from logging import getLogger, ERROR,Formatter, FileHandler, StreamHandler, INFO, basicConfig, error as log_error, info as log_info, warning as log_warning
from uvloop import install


BOT_TOKEN = "8193152124:AAHqYTYNvtSdKML6vTw5S126koR26yoUQx0"
TELEGRAM_API = 20202379
TELEGRAM_HASH = "cb1d30a2facf3a1d5691fe3dbe8e8482"

install()

getLogger("pyrogram").setLevel(ERROR)
LOGGER = getLogger(__name__)

# Initialize Mega instance
log_info("Starting Mega instance")
mega = Mega()

log_info("Creating Client from Bot Token")
app = Client(
    "mega_rename_bot",
    api_id=TELEGRAM_API,
    api_hash=TELEGRAM_HASH,
    bot_token=BOT_TOKEN)
).start()

temp_sessions = {}

async def sendMessage(client, message, text):
    return await client.send_message(
        chat_id=message.chat.id,
        text=text,
        reply_to_message_id=message.id
    )

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    welcome_message = """
Welcome to the Mega Rename Bot! 🎉

Commands:
/login - Log in to your Mega account
/rename - Rename files in your Mega account
/logout - Log out from your session
"""
    await sendMessage(client, message, welcome_message)

@app.on_message(filters.command("login") & filters.private)
async def login(client, message):
    text = "Please send your Mega email and password in the following format:\n`email password`"
    await sendMessage(client, message, text)

@app.on_message(filters.text & filters.private)
async def handle_login(client, message):
    if "@" in message.text and len(message.text.split()) == 2:
        email, password = message.text.split()
        try:
            user = mega.login(email, password)
            temp_sessions[message.from_user.id] = user
            await sendMessage(client, message, "Login successful! Use /rename to rename files.")
        except Exception as e:
            await sendMessage(client, message, f"Login failed: {e}")

@app.on_message(filters.command("rename") & filters.private)
async def rename_files(client, message):
    user = temp_sessions.get(message.from_user.id)
    if not user:
        await sendMessage(client, message,"You are not logged in! Use /login to log in first.")
        return

    await sendMessage(client, message,"Send the rename pattern as: \n`old_pattern new_pattern`")

@app.on_message(filters.text & filters.private)
async def handle_rename(client, message):
    user = temp_sessions.get(message.from_user.id)
    if not user:
        await sendMessage(client, message, "You are not logged in! Use /login to log in first.")
        return

    if len(message.text.split()) == 2:
        old_pattern, new_pattern = message.text.split()
        try:
            files = user.get_files()
            renamed_files = []
            for file_id, file_data in files.items():
                if old_pattern in file_data['name']:
                    new_name = file_data['name'].replace(old_pattern, new_pattern)
                    user.rename(file_id, new_name)
                    renamed_files.append(new_name)

            if renamed_files:
                await sendMessage(client, message,f"Renamed files: \n\n" + "\n".join(renamed_files))
            else:
                await sendMessage(client, message, "No files matched the pattern.")
        except Exception as e:
            await sendMessage(client, message,f"Error during renaming: {e}")

@app.on_message(filters.command("logout") & filters.private)
async def logout(client, message):
    if message.from_user.id in temp_sessions:
        del temp_sessions[message.from_user.id]
        await sendMessage(client, message,"Logged out successfully!")
    else:
        await sendMessage(client, message,"You are not logged in.")

log_info(f"Bot Started : {app.me.usename}")
         
