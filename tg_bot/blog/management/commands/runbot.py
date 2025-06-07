from django.core.management.base import BaseCommand
from blog.bot import run_bot
import asyncio

class Command(BaseCommand):
    help = 'Запускает Telegram бота'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Запуск Telegram бота...'))
        try:
            run_bot()
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('Бот остановлен'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка при запуске бота: {str(e)}')) 