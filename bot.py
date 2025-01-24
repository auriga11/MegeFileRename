import os
from pyrogram import Client, filters
from mega import Mega

# Initialize Mega instance
mega = Mega()

# Create Pyrogram client
app = Client(
    "mega_rename_bot",
    api_id=os.getenv("20202379"),
    api_hash=os.getenv("cb1d30a2facf3a1d5691fe3dbe8e8482"),
    bot_token=os.getenv("8193152124:AAHqYTYNvtSdKML6vTw5S126koR26yoUQx0")
)

# Dictionary to store user sessions
temp_sessions = {}

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    welcome_message = """
Welcome to the Mega Rename Bot! 🎉

Commands:
/login - Log in to your Mega account
/rename - Rename files in your Mega account
/logout - Log out from your session
"""
    await client.send_message(chat_id=message.chat.id, text=text, reply_to_message_id=message.id)
    

@app.on_message(filters.command("login") & filters.private)
def login(client, message):
    message.reply_text("Please send your Mega email and password in the following format:\n`email password`")

@app.on_message(filters.text & filters.private)
def handle_login(client, message):
    if "@" in message.text and len(message.text.split()) == 2:
        email, password = message.text.split()
        try:
            user = mega.login(email, password)
            temp_sessions[message.chat.id] = user
            await message.reply_text("Login successful! Use /rename to rename files.")
        except Exception as e:
            await message.reply_text(f"Login failed: {e}")

@app.on_message(filters.command("rename") & filters.private)
def rename_files(client, message):
    user = temp_sessions.get(message.from_user.id)
    if not user:
        await message.reply_text("You are not logged in! Use /login to log in first.")
        return

    message.reply_text("Send the rename pattern as: \n`old_pattern new_pattern`")

@app.on_message(filters.text & filters.private)
def handle_rename(client, message):
    user = temp_sessions.get(message.chat.id)
    if not user:
        message.reply_text("You are not logged in! Use /login to log in first.")
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
                message.reply_text(f"Renamed files: \n\n" + "\n".join(renamed_files))
            else:
                message.reply_text("No files matched the pattern.")
        except Exception as e:
            message.reply_text(f"Error during renaming: {e}")

@app.on_message(filters.command("logout") & filters.private)
def logout(client, message):
    if message.chat.id in temp_sessions:
        del temp_sessions[message.chat.id]
        message.reply_text("Logged out successfully!")
    else:
        message.reply_text("You are not logged in.")

# Run the bot
app.run()
