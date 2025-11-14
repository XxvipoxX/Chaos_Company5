from django.contrib import admin
from .models import UserAchievement, PlaySession, UserLibrary

admin.site.register(UserAchievement)
admin.site.register(PlaySession)
admin.site.register(UserLibrary)