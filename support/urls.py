from django.urls import path
from . import views

urlpatterns = [
    # URLs para usuarios normales
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('ticket/create/', views.create_ticket, name='create_ticket'),
    path('ticket/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    path('ticket/<int:ticket_id>/response/', views.add_ticket_response, name='add_ticket_response'),
    path('ticket/<int:ticket_id>/close/', views.close_ticket, name='close_ticket'),
    path('ticket/<int:ticket_id>/reopen/', views.reopen_ticket, name='reopen_ticket'),
    path('ticket/<int:ticket_id>/delete/', views.delete_ticket, name='delete_ticket'),
    path('ticket/stats/', views.ticket_stats, name='ticket_stats'),
]