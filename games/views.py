from django.shortcuts import render, get_object_or_404
from .models import Game, Category

def game_catalog(request):
    """Catálogo completo de juegos"""
    games = Game.objects.filter(is_available=True)
    categories = Category.objects.all()
    
    # Filtrar por categoría si se especifica
    category_filter = request.GET.get('category')
    if category_filter:
        games = games.filter(genres__name=category_filter)
    
    context = {
        'games': games,
        'categories': categories,
        'selected_category': category_filter,
        'title': 'Catálogo de Juegos'
    }
    return render(request, 'games/catalog.html', context)

def game_detail(request, game_id):
    """Detalle de un juego específico"""
    game = get_object_or_404(Game, id=game_id, is_available=True)
    
    context = {
        'game': game,
        'title': game.title
    }
    return render(request, 'games/game_detail.html', context)