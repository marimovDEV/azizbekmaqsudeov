import os
import shutil
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'SQLite ma\'lumotlar bazasini zaxiraga olish'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            help='Zaxira fayl nomi (ixtiyoriy)',
        )

    def handle(self, *args, **options):
        db_path = settings.DATABASES['default']['NAME']
        
        if not os.path.exists(db_path):
            self.stdout.write(
                self.style.ERROR('Ma\'lumotlar bazasi fayli topilmadi!')
            )
            return
        
        # Zaxira fayl nomini belgilash
        if options['output']:
            backup_name = options['output']
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f'backup_{timestamp}.sqlite3'
        
        # Zaxira fayl yo'lini belgilash
        backup_path = os.path.join(settings.BASE_DIR, backup_name)
        
        try:
            # Ma'lumotlar bazasini nusxalash
            shutil.copy2(db_path, backup_path)
            
            # Fayl hajmini olish
            size = os.path.getsize(backup_path)
            size_mb = size / (1024 * 1024)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Ma\'lumotlar bazasi muvaffaqiyatli zaxiraga olindi!\n'
                    f'Fayl: {backup_name}\n'
                    f'Hajm: {size_mb:.2f} MB'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Zaxiraga olishda xatolik: {e}')
            ) 