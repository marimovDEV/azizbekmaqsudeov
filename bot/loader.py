import logging
import os
import django
from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from asgiref.sync import sync_to_async

from set_main.models import BotSettings
from bot.handler.users.private_user import router

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'set_app.settings')
django.setup()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

async def get_bot_settings():
    try:
        settings = await sync_to_async(BotSettings.objects.first)()
        if not settings:
            raise ValueError("Bot sozlamalari topilmadi. Iltimos, admin panelida sozlamalarni kiriting.")
        return settings
    except Exception as e:
        raise ValueError(f"Bot sozlamalarini o'qishda xatolik: {e}")

async def on_startup(bot: Bot):
    logging.info("Bot ishga tushdi!")
    try:
        settings = await get_bot_settings()
        if settings.webhook_url:
            await bot.set_webhook(settings.webhook_url)
            logging.info(f"Webhook o'rnatildi: {settings.webhook_url}")
    except Exception as e:
        logging.error(f"Webhook o'rnatishda xatolik: {e}")

async def on_shutdown(bot: Bot):
    logging.info("Bot to'xtatildi!")
    try:
        await bot.delete_webhook()
        logging.info("Webhook o'chirildi")
    except Exception as e:
        logging.error(f"Webhook o'chirishda xatolik: {e}")

async def set_bot_commands(bot: Bot):
    commands = [
        ("start", "Buyurtma berishni boshlash"),
        ("help", "Yordam"),
        ("cancel", "Jarayonni bekor qilish"),
        ("admin", "Admin panel (faqat admin uchun)"),
        ("stats", "Statistika (faqat admin uchun)"),
        ("users", "Foydalanuvchilar soni (faqat admin uchun)")
    ]
    
    from aiogram.types import BotCommand
    bot_commands = [BotCommand(command=cmd[0], description=cmd[1]) for cmd in commands]
    await bot.set_my_commands(bot_commands)

async def main():
    try:
        settings = await get_bot_settings()
        bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode='HTML'))
        dp = Dispatcher()

        dp.include_router(router)

        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        
        # Set bot commands
        await set_bot_commands(bot)
        
        logging.info("Bot polling rejimida ishga tushmoqda...")
        await dp.start_polling(bot)
        
    except Exception as e:
        logging.error(f"Bot ishga tushirishda xatolik: {e}")
        raise