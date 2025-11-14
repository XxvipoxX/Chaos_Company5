from django.contrib import admin
from .models import SubscriptionPlan, PaymentOrder

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'price', 'duration_days', 'is_active']
    list_filter = ['is_active']

@admin.register(PaymentOrder)
class PaymentOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'plan_type', 'amount', 'status', 'created_at']
    list_filter = ['status', 'plan_type']