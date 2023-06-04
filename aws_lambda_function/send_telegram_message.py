from telegram import Bot
import asyncio
from dotenv import load_dotenv
import os
load_dotenv()

def send_telegram_message(message):
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

    telegram_bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    async def send_message():
        await telegram_bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    # Create a new event loop
    loop = asyncio.get_event_loop()
    
    retry_count = 1
    while(retry_count<=3):
        try:
            loop.run_until_complete(send_message())
            print("Sent TELEGRAM successfully")
            return True
        except Exception as e:
            print("TELEGRAM SEND FAILED ")
            print(f"try count is {_retry_count}/3")
            retry_count += 1
            time.sleep(3)
            if retry_count==4:
                print(e)
                print("CONNECTION FAILED, ALL THREE ATTEMPTS FAILED.")
            continue
    loop.close()

send_telegram_message("heelo!!")