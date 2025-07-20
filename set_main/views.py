from django.shortcuts import render
from django.http import JsonResponse
from .models import Order, User, Car, Route

# Create your views here.

def index(request):
    """Asosiy sahifa"""
    context = {
        'total_orders': Order.objects.count(),
        'total_users': User.objects.count(),
        'total_cars': Car.objects.count(),
        'total_routes': Route.objects.count(),
    }
    return render(request, 'set_main/index.html', context)

def api_stats(request):
    """API endpoint for statistics"""
    stats = {
        'orders': Order.objects.count(),
        'users': User.objects.count(),
        'cars': Car.objects.count(),
        'routes': Route.objects.count(),
    }
    return JsonResponse(stats)
