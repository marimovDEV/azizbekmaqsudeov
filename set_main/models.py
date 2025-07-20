from django.db import models
from django.utils import timezone

class Car(models.Model):
    name = models.CharField(max_length=100, verbose_name='Mashina nomi', unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return self.name
    
    class Meta:
        verbose_name = 'Mashina'
        verbose_name_plural = 'Mashinalar'

class Route(models.Model):
    name = models.CharField(max_length=200, verbose_name='Marshrut nomi', unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return self.name
    
    class Meta:
        verbose_name = 'Marshrut'
        verbose_name_plural = 'Marshrutlar'

class User(models.Model):
    user_id = models.BigIntegerField(verbose_name='Telegram ID', unique=True)
    full_name = models.CharField(max_length=200, verbose_name='To\'liq ism')
    phone = models.CharField(max_length=20, verbose_name='Telefon raqam', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return f"{self.full_name} ({self.user_id})"
    
    class Meta:
        verbose_name = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'

class Order(models.Model):
    TRIP_TYPE_CHOICES = [
        ('person', 'Odam'),
        ('cargo', 'Pochta'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Foydalanuvchi')
    direction = models.CharField(max_length=200, verbose_name='Yo\'nalish')
    date = models.DateField(verbose_name='Sana')
    phone = models.CharField(max_length=20, verbose_name='Telefon raqam')
    trip_type = models.CharField(max_length=10, choices=TRIP_TYPE_CHOICES, verbose_name='Sayohat turi')
    car = models.CharField(max_length=100, verbose_name='Mashina')
    address = models.TextField(verbose_name='Manzil')
    comment = models.TextField(verbose_name='Izoh', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return f"Buyurtma #{self.id} - {self.user.full_name}"
    
    class Meta:
        verbose_name = 'Buyurtma'
        verbose_name_plural = 'Buyurtmalar'
        ordering = ['-created_at']

class BotSettings(models.Model):
    bot_token = models.CharField(max_length=200, verbose_name='Bot Token')
    admin_id = models.BigIntegerField(verbose_name='Admin ID')
    webhook_url = models.CharField(max_length=200, verbose_name='Webhook URL', blank=True, null=True)
    webhook_path = models.CharField(max_length=50, verbose_name='Webhook Path', default='/webhook')
    webapp_host = models.CharField(max_length=50, verbose_name='WebApp Host', default='0.0.0.0')
    webapp_port = models.IntegerField(verbose_name='WebApp Port', default=8080)
    
    def __str__(self) -> str:
        return f"Bot Settings"
    
    class Meta:
        verbose_name = 'Bot sozlamalari'
        verbose_name_plural = 'Bot sozlamalari'
