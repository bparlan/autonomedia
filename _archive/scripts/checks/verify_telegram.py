import asyncio

from dotenv import load_dotenv

from src.autonomedia.core.observability.telegram import notifier

load_dotenv()


async def test_telegram():

    message = "🚀 **Autonomedia Telegram Bot:** Integration verified and operational."
    await notifier.notify(message)


asyncio.run(test_telegram())
