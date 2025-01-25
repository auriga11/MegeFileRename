import os
from pyrogram import Client, filters
from mega import Mega
from concurrent.futures import ThreadPoolExecutor
from logging import getLogger, ERROR,Formatter, FileHandler, StreamHandler, INFO, basicConfig, error as log_error, info as log_info, warning as log_warning
from uvloop import install
from asyncio import sleep as asleep


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

async def get_all_files(mega_instance):
    files = []
    all_items = mega_instance.get_files()

    for file_id, file_info in all_items.items():
        if 'a' in file_info:
            files.append(file_info)
    return files

async def rename_file_with_retry(user, name, file_info, file_number, retries=3):
    original_file_name = file_info['a']['n']
    new_name = f"@{name} {file_number}{original_file_name[original_file_name.rfind('.'):]}"
    
    for attempt in range(retries):
        try:            
            file = user.find(original_file_name)
            if file:
                user.rename(file, new_name)
                log_info(f"Renamed: '{original_file_name}' → '{new_name}'")
                return  # Exit loop if successful
            else:
                log_info(f"File '{original_file_name}' not found.")
                return
        except Exception as e:
            log_info(f"Attempt {attempt + 1} failed for '{original_file_name}': {e}")
            await asleep(2)  # Wait before retrying
    log_info(f"Failed to rename '{original_file_name}' after {retries} attempts.")

@app.on_message(filters.command("rename") & filters.private)
async def rename_files(client, message):
    if len(message.text.split()) > 1:
        user = mega_session.get(message.from_user.id)
        if not user:
            text = "You are not logged in! Use /login to log in first."
            return await sendMessage(client, message, text)
        
        user = mega_session.get(message.from_user.id)   
        if len(message.text.split()) == 2:
            telegram_name = message.text.split()[1]
            if '@' not in telegram_name:
                return await sendMessage(client, message, 'Mention thr name of Channel /username with @')
            try:
                all_files = await get_all_files(user)
                if all_files:
                    tasks = [
                        rename_file_with_retry(user, telegram_name, file_info, file_number)
                        for file_number, file_info in enumerate(all_files, start=1)
                    ]
                    await gather(*tasks)  # Use asyncio.gather to handle async tasks
                    return await client.send_message(message.chat.id, "Renaming process completed!")
                else:
                    return await client.send_message(message.chat.id, 'No files found in your Mega account.')
            except Exception as e:
                return await client.send_message(message.chat.id, f"An error occurred: {e}")
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
