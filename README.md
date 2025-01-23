# Mega Rename Bot

A Telegram bot that helps you bulk rename files in your Mega account.

## Features

- Secure login to Mega account
- Bulk rename files with customizable format
- Concurrent processing for faster renaming
- Detailed status updates and error reporting
- Easy deployment to Koyeb

## Setup

1. Clone this repository
2. Create a new Telegram bot using [@BotFather](https://t.me/botfather) and get the bot token
3. Copy `.env.example` to `.env` and add your Telegram bot token
4. Install dependencies: `pip install -r requirements.txt`
5. Run the bot: `python bot.py`

## Deployment to Koyeb

1. Create a Koyeb account at [koyeb.com](https://koyeb.com)
2. Install the Koyeb CLI
3. Build and push the Docker image:
   ```bash
   docker build -t mega-rename-bot .
   ```
4. Deploy to Koyeb:
   ```bash
   koyeb app init mega-rename-bot
   ```
5. Set the environment variable:
   ```bash
   koyeb app set-env mega-rename-bot TELEGRAM_BOT_TOKEN=your_token_here
   ```

## Usage

1. Start the bot in Telegram
2. Use `/login email password` to connect your Mega account
3. Use `/rename` to start the renaming process
4. Use `/logout` to disconnect your Mega account

## Security Note

- The bot stores login sessions in memory only
- Credentials are not persisted
- Each user's session is isolated
- The bot automatically logs out when stopped

## License

MIT License