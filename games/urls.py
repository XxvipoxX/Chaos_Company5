from django.urls import path
from . import views

urlpatterns = [
    path('catalog/', views.game_catalog, name='game_catalog'),
    path('game/<int:game_id>/', views.game_detail, name='game_detail'),
]