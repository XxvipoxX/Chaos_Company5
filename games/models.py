# games/models.py
from django.db import models

class Game(models.Model):
    GENRE_CHOICES = [
        ('accion', 'Acción'),
        ('aventura', 'Aventura'),
        ('rpg', 'RPG'),
        ('deportes', 'Deportes'),
        ('indie', 'Indie'),
        ('estrategia', 'Estrategia'),
        ('shooter', 'Shooter'),
        ('simulacion', 'Simulación'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    developer = models.CharField(max_length=100)
    publisher = models.CharField(max_length=100)
    release_date = models.DateField(null=True, blank=True)
    genre = models.CharField(max_length=50, choices=GENRE_CHOICES)
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    image_url = models.CharField(max_length=255)
    trailer_url = models.CharField(max_length=255, blank=True, null=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class GameCategory(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['game', 'category']