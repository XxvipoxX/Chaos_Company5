from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from .models import UserLibrary, PlaySession, UserAchievement
from games.models import Game

@login_required
def user_library(request):
    """Biblioteca personal del usuario"""
    user_library = UserLibrary.objects.filter(user=request.user)
    
    context = {
        'user_library': user_library,
        'title': 'Mi Biblioteca'
    }
    return render(request, 'gaming/library.html', context)

@login_required
def add_to_library(request, game_id):
    """Agregar juego a la biblioteca"""
    game = get_object_or_404(Game, id=game_id)
    
    # Verificar si ya está en la biblioteca
    if UserLibrary.objects.filter(user=request.user, game=game).exists():
        messages.info(request, f'"{game.title}" ya está en tu biblioteca.')
    else:
        UserLibrary.objects.create(user=request.user, game=game)
        messages.success(request, f'"{game.title}" agregado a tu biblioteca.')
    
    return redirect('user_library')

@login_required
def play_game(request, game_id):
    """Iniciar sesión de juego"""
    game = get_object_or_404(Game, id=game_id)
    
    # Verificar membresía
    if not request.user.is_membership_active:
        messages.error(request, 'Necesitas una membresía activa para jugar.')
        return redirect('membresias')
    
    # Crear sesión de juego
    play_session = PlaySession.objects.create(
        user=request.user,
        game=game,
        start_time=timezone.now(),
        platform='pc',  # Puedes detectar la plataforma
        stream_quality='1080p'  # Depende de la membresía
    )
    
    context = {
        'game': game,
        'play_session': play_session,
        'title': f'Jugando {game.title}'
    }
    return render(request, 'gaming/play_session.html', context)

@login_required
def end_play_session(request, session_id):
    """Finalizar sesión de juego"""
    play_session = get_object_or_404(PlaySession, id=session_id, user=request.user)
    play_session.end_time = timezone.now()
    play_session.save()
    
    # Actualizar biblioteca
    user_library, created = UserLibrary.objects.get_or_create(
        user=request.user, 
        game=play_session.game
    )
    user_library.play_count += 1
    user_library.total_play_time += play_session.duration_minutes or 0
    user_library.last_played = timezone.now()
    user_library.save()
    
    messages.success(request, f'Sesión de {play_session.game.title} finalizada.')
    return redirect('user_library')

@login_required
def user_achievements(request):
    """Logros del usuario"""
    achievements = UserAchievement.objects.filter(user=request.user)
    
    context = {
        'achievements': achievements,
        'title': 'Mis Logros'
    }
    return render(request, 'gaming/achievements.html', context)