from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from main import views as main_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', main_views.index, name='index'),
    path('gamepass/', main_views.gamepass, name='gamepass'),
    path('membresias/', main_views.membresias, name='membresias'),
    path('ventajas/', main_views.ventajas, name='ventajas'),
    
    # URLs de las nuevas apps
    path('games/', include('games.urls')),
    path('gaming/', include('gaming.urls')),
    path('support/', include('support.urls')),
    path('subscriptions/', include('subscriptions.urls')),
    
    # URLs existentes
    path('accounts/', include('accounts.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)