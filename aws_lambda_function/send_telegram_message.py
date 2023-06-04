from telegram import Bot
import asyncio
from dotenv import load_dotenv
import os

def send_telegram_message(message):
    load_dotenv()
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    async def send_message():
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

    # Create a new event loop
    loop = asyncio.get_event_loop()

    try:
        # Run the async function
        loop.run_until_complete(send_message())
    finally:
        # Close the loop
        loop.close()