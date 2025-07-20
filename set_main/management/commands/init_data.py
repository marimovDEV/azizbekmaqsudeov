from django.core.management.base import BaseCommand
from set_main.models import Car, Route

class Command(BaseCommand):
    help = 'Ma\'lumotlar bazasini boshlang\'ich ma\'lumotlar bilan to\'ldirish'

    def handle(self, *args, **options):
        self.stdout.write('Boshlang\'ich ma\'lumotlar qo\'shilmoqda...')
        
        # Default cars
        default_cars = [
            "Kaptiva",
            "Malibu", 
            "Cobalt",
            "Gentra",
            "Largus",
            "Lasetti"
        ]
        
        for car_name in default_cars:
            car, created = Car.objects.get_or_create(name=car_name)
            if created:
                self.stdout.write(f'  ✓ Mashina qo\'shildi: {car_name}')
            else:
                self.stdout.write(f'  - Mashina mavjud: {car_name}')
        
        # Default routes
        default_routes = [
            "Xorazmdan Buxoroga",
            "Buxorodan Xorazmga"
        ]
        
        for route_name in default_routes:
            route, created = Route.objects.get_or_create(name=route_name)
            if created:
                self.stdout.write(f'  ✓ Marshrut qo\'shildi: {route_name}')
            else:
                self.stdout.write(f'  - Marshrut mavjud: {route_name}')
        
        self.stdout.write(
            self.style.SUCCESS('Boshlang\'ich ma\'lumotlar muvaffaqiyatli qo\'shildi!')
        ) 