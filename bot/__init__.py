import os
from time import time, sleep
import logging
from bot.config import TG_CONFIG
from pyrogram import Client, enums, filters
from pyrogram.errors import RPCError

# Constants
LOG_FILE = 'log.txt'
USER_SESSION_STRING_KEY = 'stringhi'
user_data = {}

# Set up logging
logging.basicConfig(
    format="[%(asctime)s] [%(levelname)s] - %(message)s",
    datefmt="%d-%b-%y %I:%M:%S %p",
    level=logging.INFO,
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
)
app = Client(
    TG_CONFIG.session,
    bot_token=TG_CONFIG.bot_token,
    api_id=TG_CONFIG.api_id,
    api_hash=TG_CONFIG.api_hash,
    sleep_threshold=30
)
# Set logging level for pyrogram
logging.getLogger("pyrogram").setLevel(logging.WARNING)
def create_client() -> Client:
    try:
        app1 = Client(
            'user',
            api_id=TG_CONFIG.api_id,
            api_hash=TG_CONFIG.api_hash,
            session_string=TG_CONFIG.stringhi,
            parse_mode=enums.ParseMode.HTML,
            no_updates=True
        )
        logging.info("Client created successfully")
        return app
    except RPCError as e:
        logging.error(f"Failed making client from USER_SESSION_STRING ({TG_CONFIG.stringhi}): {e}")
        return None
from aiohttp import web
from bot.route import routes


async def web_server():
    web_app = web.Application(client_max_size=30000000)
    web_app.add_routes(routes)
    return web_app


botStartTime = time()
def main():
    if TG_CONFIG.stringhi:
        app1 = create_client()
        if app1:
            logging.info("Bot is running")

            @app1.on_message(filters.private & filters.command("start"))
            def start_command(client: Client, message):
                logging.info(f"Received /start command from {message.from_user.username}")
                message.reply("Hello! I'm a bot.")

            @app1.on_message(filters.private & filters.command("help"))
            def help_command(client: Client, message):
                logging.info(f"Received /help command from {message.from_user.username}")
                message.reply("This is a help message.")

            @app1.on_message(filters.private & filters.text)
            def text_message(client: Client, message):
                logging.info(f"Received message: {message.text}")
                message.reply("You sent: " + message.text)

            app1.run()
        else:
            logging.error("Bot is not running")
    else:
        logging.error("USER_SESSION_STRING is empty")

if __name__ == '__main__':
    main()
