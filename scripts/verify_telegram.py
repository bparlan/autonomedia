import asyncio
from dotenv import load_dotenv
load_dotenv()

from src.autonomedia.core.observability.telegram import notifier

async def test_telegram():
    print("Sending test notification...")
    await notifier.notify("🚀 **Autonomedia Telegram Bot:** Integration verified and operational.")
    print("Sent.")

asyncio.run(test_telegram())
