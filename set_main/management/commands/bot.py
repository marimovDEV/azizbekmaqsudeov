import asyncio
import logging
from django.core.management.base import BaseCommand
from bot.loader import main

class Command(BaseCommand):
    help = 'Telegram botni ishga tushirish'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Bot ishga tushmoqda...')
        )
        
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('Bot to\'xtatildi')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Xatolik: {e}')
            )