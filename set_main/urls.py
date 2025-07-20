
from django.urls import path
from . import views

app_name = 'set_main'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/stats/', views.api_stats, name='api_stats'),
]
