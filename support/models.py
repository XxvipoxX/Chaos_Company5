from django.db import models
from django.conf import settings
from django.utils import timezone

class SupportTicket(models.Model):
    STATUS_CHOICES = [
        ('open', 'Abierto'),
        ('pending', 'En Proceso'),
        ('resolved', 'Resuelto'),
        ('closed', 'Cerrado'),
    ]
    
    CATEGORY_CHOICES = [
        ('technical', 'Problemas Técnicos'),
        ('billing', 'Facturación y Pagos'),
        ('game', 'Problemas con Juegos'),
        ('account', 'Cuenta y Perfil'),
        ('streaming', 'Streaming y Latencia'),
        ('membership', 'Membresía y Suscripción'),
        ('other', 'Otro'),
    ]
    
    # Usar settings.AUTH_USER_MODEL en lugar de User directo
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='support_tickets')
    subject = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='technical')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata del sistema
    priority = models.CharField(max_length=20, default='medium', choices=[
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('urgent', 'Urgente'),
    ])
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Ticket de Soporte'
        verbose_name_plural = 'Tickets de Soporte'
    
    def __str__(self):
        return f"Ticket #{self.id} - {self.subject}"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('ticket_detail', kwargs={'ticket_id': self.id})
    
    @property
    def is_open(self):
        return self.status in ['open', 'pending']
    
    @property
    def days_open(self):
        if self.closed_at:
            return (self.closed_at - self.created_at).days
        return (timezone.now() - self.created_at).days
    
    @property
    def response_count(self):
        return self.responses.count()

class TicketResponse(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='responses')
    # Usar settings.AUTH_USER_MODEL aquí también
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    is_from_support = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Para adjuntos (opcional)
    attachment = models.FileField(upload_to='support/attachments/', null=True, blank=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = 'Respuesta de Ticket'
        verbose_name_plural = 'Respuestas de Tickets'
    
    def __str__(self):
        return f"Respuesta para Ticket #{self.ticket.id}"
    
    @property
    def is_user_response(self):
        return not self.is_from_support