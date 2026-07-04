import logging
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from src.database.client import DatabaseClient

load_dotenv()
logger = logging.getLogger("telegram_bot")


async def pause_platform(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /pause <platform>")
        return

    platform = context.args[0].lower()
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        # Check if platform exists
        exists = await conn.fetchval(
            "SELECT 1 FROM platform_health WHERE platform_name = $1", platform
        )
        if not exists:
            await update.message.reply_text(f"Platform {platform} not found.")
            return

        await conn.execute(
            "UPDATE platform_health SET status = 'halted' WHERE platform_name = $1",
            platform,
        )
        await update.message.reply_text(
            f"🛑 Platform {platform} has been HALTED. Manual resume required."
        )


async def resume_platform(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /resume <platform>")
        return

    platform = context.args[0].lower()
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE platform_health SET status = 'healthy' WHERE platform_name = $1",
            platform,
        )
        await update.message.reply_text(f"✅ Platform {platform} is now active.")


class TelegramNotifier:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.application = None
        if self.token:
            self.application = ApplicationBuilder().token(self.token).build()
            self.application.add_handler(CommandHandler("pause", pause_platform))
            self.application.add_handler(CommandHandler("resume", resume_platform))

    async def start_polling(self):
        if not self.application:
            return
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        logger.info("Telegram bot polling started.")

    async def notify(self, message: str):
        if not self.application or not self.chat_id:
            logger.warning("Telegram not configured, skipping notification.")
            return

        try:
            await self.application.bot.send_message(
                chat_id=self.chat_id,
                text=f"🤖 *Autonomedia Alert*\n\n{message}",
                parse_mode="Markdown",
            )
        except Exception as e:
            logger.error(f"Telegram notification failed: {e}")


notifier = TelegramNotifier()
