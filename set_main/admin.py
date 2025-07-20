from django.contrib import admin
from .models import Car, Route, User, Order, BotSettings

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    ordering = ['name']

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    ordering = ['name']

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'full_name', 'phone', 'created_at']
    search_fields = ['user_id', 'full_name', 'phone']
    ordering = ['-created_at']
    readonly_fields = ['user_id', 'created_at']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'direction', 'date', 'trip_type', 'car', 'created_at']
    list_filter = ['trip_type', 'date', 'created_at']
    search_fields = ['user__full_name', 'direction', 'car', 'phone']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('user', 'direction', 'date', 'phone')
        }),
        ('Sayohat ma\'lumotlari', {
            'fields': ('trip_type', 'car', 'address', 'comment')
        }),
        ('Vaqt', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(BotSettings)
class BotSettingsAdmin(admin.ModelAdmin):
    list_display = ['bot_token', 'admin_id', 'webhook_url']
    fieldsets = (
        ('Bot sozlamalari', {
            'fields': ('bot_token', 'admin_id')
        }),
        ('Webhook sozlamalari', {
            'fields': ('webhook_url', 'webhook_path', 'webapp_host', 'webapp_port'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Faqat bitta sozlama bo'lishi mumkin
        return not BotSettings.objects.exists()
