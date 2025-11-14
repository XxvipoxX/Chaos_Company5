from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.conf import settings
from .models import SupportTicket, TicketResponse

@login_required
def create_ticket(request):
    """Crear nuevo ticket de soporte"""
    if request.method == 'POST':
        subject = request.POST.get('subject')
        description = request.POST.get('description')
        category = request.POST.get('category')
        
        if subject and description:
            ticket = SupportTicket.objects.create(
                user=request.user,
                subject=subject,
                description=description,
                category=category
            )
            messages.success(request, 'Ticket creado exitosamente. Te contactaremos pronto.')
            return redirect('ticket_detail', ticket_id=ticket.id)
        else:
            messages.error(request, 'Por favor completa todos los campos.')
    
    return render(request, 'support/create_ticket.html', {'title': 'Crear Ticket'})

@login_required
def ticket_list(request):
    """Lista de tickets del usuario"""
    tickets = SupportTicket.objects.filter(user=request.user).order_by('-created_at')
    
    # Estadísticas para el template
    open_tickets = tickets.filter(status='open').count()
    pending_tickets = tickets.filter(status='pending').count()
    resolved_tickets = tickets.filter(status='resolved').count()
    
    context = {
        'tickets': tickets,
        'open_tickets': open_tickets,
        'pending_tickets': pending_tickets,
        'resolved_tickets': resolved_tickets,
        'avg_response_time': '2h',  # Puedes calcular esto basado en datos reales
        'title': 'Mis Tickets de Soporte'
    }
    return render(request, 'support/ticket_list.html', context)

@login_required
def ticket_detail(request, ticket_id):
    """Detalle de un ticket específico"""
    ticket = get_object_or_404(SupportTicket, id=ticket_id, user=request.user)
    
    # Obtener respuestas del ticket
    responses = TicketResponse.objects.filter(ticket=ticket).order_by('created_at')
    
    context = {
        'ticket': ticket,
        'responses': responses,
        'title': f'Ticket #{ticket.id}'
    }
    return render(request, 'support/ticket_detail.html', context)

@login_required
def add_ticket_response(request, ticket_id):
    """Agregar respuesta a un ticket"""
    ticket = get_object_or_404(SupportTicket, id=ticket_id, user=request.user)
    
    # Verificar que el ticket esté abierto o en proceso
    if ticket.status not in ['open', 'pending']:
        messages.error(request, 'No puedes agregar comentarios a un ticket cerrado o resuelto.')
        return redirect('ticket_detail', ticket_id=ticket.id)
    
    if request.method == 'POST':
        message = request.POST.get('message', '').strip()
        
        if message:
            # Crear la respuesta
            TicketResponse.objects.create(
                ticket=ticket,
                user=request.user,
                message=message,
                is_from_support=False
            )
            
            # Actualizar timestamp del ticket
            ticket.updated_at = timezone.now()
            ticket.save()
            
            messages.success(request, 'Comentario agregado exitosamente.')
        else:
            messages.error(request, 'El mensaje no puede estar vacío.')
    
    return redirect('ticket_detail', ticket_id=ticket.id)

@login_required
def close_ticket(request, ticket_id):
    """Cerrar un ticket"""
    ticket = get_object_or_404(SupportTicket, id=ticket_id, user=request.user)
    
    if ticket.status == 'resolved':
        ticket.status = 'closed'
        ticket.updated_at = timezone.now()
        ticket.closed_at = timezone.now()
        ticket.save()
        
        messages.success(request, 'Ticket cerrado exitosamente.')
    else:
        messages.error(request, 'Solo puedes cerrar tickets que estén resueltos.')
    
    return redirect('ticket_detail', ticket_id=ticket.id)

@login_required
def reopen_ticket(request, ticket_id):
    """Reabrir un ticket cerrado"""
    ticket = get_object_or_404(SupportTicket, id=ticket_id, user=request.user)
    
    if ticket.status == 'closed':
        ticket.status = 'open'
        ticket.updated_at = timezone.now()
        ticket.closed_at = None
        ticket.save()
        
        messages.success(request, 'Ticket reabierto exitosamente.')
    else:
        messages.error(request, 'Solo puedes reabrir tickets cerrados.')
    
    return redirect('ticket_detail', ticket_id=ticket.id)

@login_required
def delete_ticket(request, ticket_id):
    """Eliminar un ticket (solo si está cerrado)"""
    ticket = get_object_or_404(SupportTicket, id=ticket_id, user=request.user)
    
    if ticket.status == 'closed':
        ticket.delete()
        messages.success(request, 'Ticket eliminado exitosamente.')
        return redirect('ticket_list')
    else:
        messages.error(request, 'Solo puedes eliminar tickets cerrados.')
        return redirect('ticket_detail', ticket_id=ticket.id)

@login_required
def ticket_stats(request):
    """Estadísticas de tickets del usuario"""
    tickets = SupportTicket.objects.filter(user=request.user)
    
    stats = {
        'total_tickets': tickets.count(),
        'open_tickets': tickets.filter(status='open').count(),
        'pending_tickets': tickets.filter(status='pending').count(),
        'resolved_tickets': tickets.filter(status='resolved').count(),
        'closed_tickets': tickets.filter(status='closed').count(),
    }
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(stats)
    
    return JsonResponse(stats)