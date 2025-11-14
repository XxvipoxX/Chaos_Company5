# subscriptions/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=20, unique=True)  # free, standard, ultimate
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.IntegerField()
    max_resolution = models.CharField(max_length=20)
    max_fps = models.IntegerField()
    concurrent_streams = models.IntegerField()
    game_library_access = models.JSONField(default=dict)
    features = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class PaymentOrder(models.Model):
    PLAN_CHOICES = [
        ('free', 'Gratis'),
        ('standard', 'Estándar'),
        ('ultimate', 'Ultimate'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('completed', 'Completado'),
        ('failed', 'Fallido'),
        ('cancelled', 'Cancelado'),
        ('refunded', 'Reembolsado'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Tarjeta de Crédito'),
        ('debit_card', 'Tarjeta de Débito'),
        ('paypal', 'PayPal'),
        ('apple_pay', 'Apple Pay'),
        ('google_pay', 'Google Pay'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    plan_type = models.CharField(max_length=20, choices=PLAN_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, unique=True)
    card_last_four = models.CharField(max_length=4, blank=True, null=True)
    customer_email = models.EmailField()
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    # Información de suscripción
    subscription_start = models.DateTimeField(null=True, blank=True)
    subscription_end = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Orden #{self.id} - {self.user.username} - {self.get_plan_type_display()}"
    
    def save(self, *args, **kwargs):
        if self.status == 'completed' and not self.paid_at:
            self.paid_at = timezone.now()
            if not self.subscription_start:
                self.subscription_start = timezone.now()
            if not self.subscription_end:
                self.subscription_end = timezone.now() + timezone.timedelta(days=30)
        super().save(*args, **kwargs)
    
    @property
    def is_active(self):
        if self.subscription_end:
            return timezone.now() < self.subscription_end
        return self.status == 'completed'
    
    def get_plan_display_name(self):
        return dict(self.PLAN_CHOICES).get(self.plan_type, self.plan_type)