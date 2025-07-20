import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'SQLite ma\'lumotlar bazasini zaxira fayldan tiklash'

    def add_arguments(self, parser):
        parser.add_argument(
            'backup_file',
            type=str,
            help='Zaxira fayl nomi',
        )

    def handle(self, *args, **options):
        backup_file = options['backup_file']
        db_path = settings.DATABASES['default']['NAME']
        
        # Zaxira fayl yo'lini tekshirish
        if not os.path.isabs(backup_file):
            backup_file = os.path.join(settings.BASE_DIR, backup_file)
        
        if not os.path.exists(backup_file):
            self.stdout.write(
                self.style.ERROR(f'Zaxira fayli topilmadi: {backup_file}')
            )
            return
        
        # Joriy ma'lumotlar bazasini zaxiraga olish
        current_backup = None
        if os.path.exists(db_path):
            current_backup = f'current_backup_{os.path.basename(db_path)}'
            current_backup_path = os.path.join(settings.BASE_DIR, current_backup)
            shutil.copy2(db_path, current_backup_path)
            self.stdout.write(f'Joriy ma\'lumotlar bazasi zaxiraga olindi: {current_backup}')
        
        try:
            # Zaxira fayldan tiklash
            shutil.copy2(backup_file, db_path)
            
            # Fayl hajmini olish
            size = os.path.getsize(db_path)
            size_mb = size / (1024 * 1024)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Ma\'lumotlar bazasi muvaffaqiyatli tiklandi!\n'
                    f'Fayl: {os.path.basename(backup_file)}\n'
                    f'Hajm: {size_mb:.2f} MB'
                )
            )
            
            if current_backup:
                self.stdout.write(
                    self.style.WARNING(
                        f'Eslatma: Joriy ma\'lumotlar bazasi {current_backup} faylida saqlandi'
                    )
                )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Tiklashda xatolik: {e}')
            )
            
            # Xatolik bo'lsa, joriy ma'lumotlar bazasini tiklash
            if current_backup and os.path.exists(current_backup_path):
                try:
                    shutil.copy2(current_backup_path, db_path)
                    self.stdout.write(
                        self.style.SUCCESS('Joriy ma\'lumotlar bazasi tiklandi')
                    )
                except Exception as restore_error:
                    self.stdout.write(
                        self.style.ERROR(f'Joriy ma\'lumotlar bazasini tiklashda xatolik: {restore_error}')
                    ) 