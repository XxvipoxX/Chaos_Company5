from django.urls import path
from . import views

urlpatterns = [
    path('library/', views.user_library, name='user_library'),
    path('library/add/<int:game_id>/', views.add_to_library, name='add_to_library'),
    path('play/<int:game_id>/', views.play_game, name='play_game'),
    path('session/end/<int:session_id>/', views.end_play_session, name='end_play_session'),
    path('achievements/', views.user_achievements, name='user_achievements'),
]