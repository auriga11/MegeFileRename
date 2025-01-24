import os
from pyrogram import Client, filters
from mega import Mega
from logging import getLogger, ERROR,Formatter, FileHandler, StreamHandler, INFO, basicConfig, error as log_error, info as log_info, warning as log_warning
from uvloop import install


BOT_TOKEN = "8193152124:AAHqYTYNvtSdKML6vTw5S126koR26yoUQx0"
TELEGRAM_API = 20202379
TELEGRAM_HASH = "cb1d30a2facf3a1d5691fe3dbe8e8482"

install()
basicConfig(level=INFO)
getLogger("pyrogram").setLevel(ERROR)
LOGGER = getLogger(__name__)


log_info("Creating Client from Bot Token")
app = Client(
    "mega_rename_bot",
    api_id=TELEGRAM_API,
    api_hash=TELEGRAM_HASH,
    bot_token=BOT_TOKEN
).start()

mega_session = {}

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
    if len(message.text.split()) == 3:
        arg = message.text.split()
        email, password = arg[1], arg[2]
        try:
            log_info(f"Starting Mega instance for {message.from_user.id}")
            mega_session[message.from_user.id] = Mega().login(email, password)
            text = "Login successful! Use /rename to rename files."
            await sendMessage(client, message, text)
        except Exception as e:
            text = f"Login failed: {e}"
            await sendMessage(client, message, text)
    
    else:
        text = "Please send your Mega email and password in the following format:\n`email password`"
        await sendMessage(client, message, text)

@app.on_message(filters.command("rename") & filters.private)
async def rename_files(client, message):
    if len(message.text.split()) > 1:
        user = mega_session.get(message.from_user.id)
        if not user:
            text = "You are not logged in! Use /login to log in first."
            return await sendMessage(client, message, text)
        
        user = mega_session.get(message.from_user.id)   
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
                    rename_text = f"Renamed files: \n\n" + "\n".join(renamed_files)
                    await sendMessage(client, message,rename_text)
                else:
                    no_rename_text = "No files matched the pattern."
                    await sendMessage(client, message, no_rename_text)
            except Exception as e:
                e_text = f"Error during renaming: {e}"
                await sendMessage(client, message,e_text)
    else:
        text = "Send the rename pattern as: \n`old_pattern new_pattern`"
        await sendMessage(client, message, text)
    
@app.on_message(filters.command("logout") & filters.private)
async def logout(client, message):
    if message.from_user.id in mega_session:
        del mega_session[message.from_user.id]
        text = "Logged out successfully!"
        await sendMessage(client, message,text)
    else:
        text = "You are not logged in."
        await sendMessage(client, message,text)

log_info(f"Bot Started : {app.me.username}")

app.loop.run_forever()
