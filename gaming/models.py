# gaming/models.py
from django.db import models
from django.conf import settings

class UserAchievement(models.Model):
    TIER_CHOICES = [
        ('bronze', 'Bronce'),
        ('silver', 'Plata'),
        ('gold', 'Oro'),
        ('platinum', 'Platino'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    game = models.ForeignKey('games.Game', on_delete=models.CASCADE)
    achievement_name = models.CharField(max_length=100)
    achievement_description = models.TextField()
    points = models.IntegerField()
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='bronze')
    unlocked_at = models.DateTimeField(auto_now_add=True)
    icon_url = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.achievement_name}"

class PlaySession(models.Model):
    PLATFORM_CHOICES = [
        ('pc', 'PC'),
        ('mobile', 'Móvil'),
        ('tablet', 'Tablet'),
        ('tv', 'Smart TV'),
        ('console', 'Consola'),
    ]
    
    QUALITY_CHOICES = [
        ('720p', '720p HD'),
        ('1080p', '1080p Full HD'),
        ('1440p', '1440p QHD'),
        ('4k', '4K Ultra HD'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    game = models.ForeignKey('games.Game', on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(null=True, blank=True)
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES)
    stream_quality = models.CharField(max_length=20, choices=QUALITY_CHOICES)

    def save(self, *args, **kwargs):
        if self.end_time and self.start_time:
            duration = self.end_time - self.start_time
            self.duration_minutes = int(duration.total_seconds() / 60)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.user.username} - {self.game.title} - {self.start_time}"

class UserLibrary(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    game = models.ForeignKey('games.Game', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    last_played = models.DateTimeField(null=True, blank=True)
    play_count = models.IntegerField(default=0)
    total_play_time = models.IntegerField(default=0)
    is_favorite = models.BooleanField(default=False)

    class Meta:
        unique_together = ['user', 'game']
        
    def __str__(self):
        return f"{self.user.username} - {self.game.title}"