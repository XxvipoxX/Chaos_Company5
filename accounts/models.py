from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.templatetags.static import static

class CustomUser(AbstractUser):
    MEMBERSHIP_CHOICES = [
        ('free', 'Gratis'),
        ('standard', 'Estándar'),
        ('ultimate', 'Ultimate')
    ]
    
    # Información básica del usuario
    membership_type = models.CharField(
        max_length=20,
        choices=MEMBERSHIP_CHOICES,
        default='free'
    )
    
    # Información de perfil
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        null=True,
        blank=True
    )
    
    # NUEVO CAMPO: Para avatares del sistema
    selected_avatar = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default='avatar_default.jpg'
    )
    
    birth_date = models.DateField(null=True, blank=True)
    
    # Sistema de membresía y pagos
    membership_start = models.DateTimeField(null=True, blank=True)
    membership_expiry = models.DateTimeField(null=True, blank=True)
    is_active_member = models.BooleanField(default=False)
    
    # Información de pago
    default_payment_method = models.CharField(max_length=50, blank=True, null=True)
    card_last_four = models.CharField(max_length=4, blank=True, null=True)

    def __str__(self):
        return self.username
    
    def get_profile_picture_url(self):
        """Retorna la URL del avatar con prioridad correcta"""
        # PRIMERO: Si hay imagen subida, usarla
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            return self.profile_picture.url
        
        # SEGUNDO: Si hay avatar del sistema seleccionado
        elif self.selected_avatar:
            return static(f'assets/{self.selected_avatar}')
        
        # TERCERO: Avatar por defecto
        else:
            return static('assets/avatar_default.jpg')
    
    @property
    def get_membership_type_display(self):
        """Método para obtener el nombre legible de la membresía"""
        return dict(self.MEMBERSHIP_CHOICES).get(self.membership_type, 'Gratis')
    
    @property
    def is_membership_active(self):
        """Verificar si la membresía está activa"""
        if self.membership_expiry:
            return timezone.now() < self.membership_expiry
        return self.is_active_member
    
    def activate_membership(self, plan_type, duration_days=30):
        """Activar o renovar membresía"""
        self.membership_type = plan_type
        self.membership_start = timezone.now()
        self.membership_expiry = timezone.now() + timezone.timedelta(days=duration_days)
        self.is_active_member = True
        self.save()
    
    def get_remaining_days(self):
        """Obtener días restantes de membresía"""
        if self.membership_expiry and self.is_membership_active:
            remaining = self.membership_expiry - timezone.now()
            return max(0, remaining.days)
        return 0

# ⚠️ IMPORTANTE: La clase PaymentOrder ha sido ELIMINADA de aquí
# y movida a subscriptions/models.py para mejor organización.