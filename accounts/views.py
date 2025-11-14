from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .forms import LoginForm, SignupForm, CustomUserChangeForm
from .models import CustomUser
from subscriptions.models import PaymentOrder
import secrets
import string
import uuid
from datetime import timedelta

def login_view(request):
    print("🔐 Vista login llamada")
    
    if request.method == 'POST':
        print("📨 POST recibido en login")
        form = LoginForm(request, data=request.POST)
        print(f"✅ Form login válido: {form.is_valid()}")
        
        if form.is_valid():
            print("🎯 Login válido - autenticando...")
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me', False)
            
            # Intentar autenticar con username
            user = authenticate(request, username=username, password=password)
            
            # Si falla, intentar con email
            if user is None:
                try:
                    user_obj = CustomUser.objects.get(email=username)
                    user = authenticate(request, username=user_obj.username, password=password)
                except CustomUser.DoesNotExist:
                    user = None
                    print("❌ Usuario no encontrado")

            if user is not None:
                login(request, user)
                print(f"👤 Usuario autenticado: {user.username}")
                
                if not remember_me:
                    request.session.set_expiry(0)
                    
                messages.success(request, f'¡Bienvenido de nuevo, {user.first_name or user.username}!')
                next_url = request.GET.get('next', '/')
                return redirect(next_url)
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
                print("❌ Autenticación fallida")
        else:
            print("❌ Errores en formulario login:", form.errors)
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})

def signup_view(request):
    print("🔧 Vista signup llamada")
    
    if request.method == 'POST':
        print("📨 POST recibido en signup")
        form = SignupForm(request.POST)
        print(f"✅ Form signup válido: {form.is_valid()}")
        print(f"📊 Datos recibidos: {request.POST}")
        
        if form.is_valid():
            print("🎯 Formulario ES válido - guardando usuario...")
            try:
                user = form.save()
                print(f"👤 Usuario guardado: {user.username} - Email: {user.email}")
                
                # Autenticar y hacer login
                login(request, user)
                print("🔐 Login exitoso después de registro")
                
                messages.success(request, f'¡Cuenta creada exitosamente! Bienvenido a ChaosCompany, {user.first_name or user.username}!')
                return redirect('index')
                
            except Exception as e:
                print(f"💥 Error al guardar usuario: {e}")
                messages.error(request, f'Error al crear la cuenta: {e}')
        else:
            print("❌ Errores del formulario signup:", form.errors)
            # Mostrar errores específicos
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = SignupForm()

    return render(request, 'accounts/signup.html', {'form': form})

def logout_view(request):
    print("🚪 Cerrando sesión")
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('index')

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})

@login_required
def edit_profile_view(request):
    print("✏️ Vista editar perfil llamada")
    
    if request.method == 'POST':
        print("📨 POST recibido en editar perfil")
        print(f"📊 Datos POST: {request.POST}")
        print(f"📁 Archivos FILES: {request.FILES}")
        
        # IMPORTANTE: Agregar request.FILES para manejar la imagen
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        print(f"✅ Form editar perfil válido: {form.is_valid()}")
        
        if form.is_valid():
            print("🎯 Formulario ES válido - guardando cambios...")
            try:
                # Usar commit=False para poder modificar antes de guardar
                user = form.save(commit=False)
                
                # Manejar la imagen de perfil - LÓGICA CORREGIDA
                selected_avatar = request.POST.get('selected_avatar', '')
                profile_picture_file = request.FILES.get('profile_picture')
                
                print(f"🖼️ Avatar seleccionado: {selected_avatar}")
                print(f"🖼️ Archivo subido: {profile_picture_file}")
                print(f"🖼️ User profile_picture antes: {user.profile_picture}")
                print(f"🖼️ User selected_avatar antes: {user.selected_avatar}")
                
                # LÓGICA MEJORADA PARA MANEJAR AVATARES
                if profile_picture_file:
                    # PRIMERO: Si se subió un archivo, usar esa imagen
                    print("📸 Usando archivo subido como avatar")
                    user.profile_picture = profile_picture_file
                    user.selected_avatar = ''  # Limpiar avatar del sistema
                    
                elif selected_avatar:
                    # SEGUNDO: Si se seleccionó avatar del sistema
                    print(f"🎯 Usando avatar del sistema: {selected_avatar}")
                    user.selected_avatar = selected_avatar
                    user.profile_picture = None  # Limpiar imagen subida
                
                # Si no hay ni archivo ni avatar seleccionado, mantener lo actual
                
                # GUARDAR EL USUARIO
                user.save()
                
                print(f"👤 Perfil actualizado: {user.username}")
                print(f"🖼️ User profile_picture después: {user.profile_picture}")
                print(f"🖼️ User selected_avatar después: {user.selected_avatar}")
                
                if profile_picture_file:
                    print(f"✅ Nueva foto de perfil guardada exitosamente")
                    messages.success(request, 'Foto de perfil actualizada exitosamente.')
                elif selected_avatar:
                    print(f"✅ Avatar del sistema guardado: {selected_avatar}")
                    messages.success(request, 'Avatar actualizado exitosamente.')
                else:
                    print("✅ Información del perfil actualizada")
                    messages.success(request, 'Perfil actualizado exitosamente.')
                    
                return redirect('profile')
                
            except Exception as e:
                print(f"💥 Error al actualizar perfil: {str(e)}")
                import traceback
                print(f"🔍 Traceback: {traceback.format_exc()}")
                messages.error(request, f'Error al actualizar el perfil: {str(e)}')
        else:
            print("❌ Errores del formulario editar perfil:", form.errors)
            # Mostrar errores específicos al usuario
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CustomUserChangeForm(instance=request.user)
        print("📝 Mostrando formulario de edición")

    return render(request, 'accounts/edit_profile.html', {'form': form})

def forgot_password_view(request):
    print("🔑 Vista recuperación de contraseña llamada")
    
    if request.method == 'POST':
        email = request.POST.get('email')
        print(f"📧 Email recibido: {email}")
        
        if not email:
            messages.error(request, 'Por favor, ingresa tu correo electrónico.')
            return render(request, 'accounts/forgot_password.html')
        
        try:
            user = CustomUser.objects.get(email=email)
            print(f"👤 Usuario encontrado: {user.username}")
            
            # Generar token temporal
            token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
            print(f"🔐 Token generado: {token}")
            
            # Guardar el token en la sesión
            request.session['reset_token'] = token
            request.session['reset_user_id'] = user.id
            request.session.set_expiry(3600)  # Expira en 1 hora
            print("💾 Token guardado en sesión")
            
            # Enviar correo electrónico
            subject = 'Recuperación de contraseña - ChaosCompany'
            message = f'''
            Hola {user.username},
            
            Has solicitado recuperar tu contraseña. 
            Para restablecer tu contraseña, haz clic en el siguiente enlace:
            
            http://127.0.0.1:8000/accounts/reset-password/{token}/
            
            Este enlace expirará en 1 hora.
            
            Si no solicitaste este cambio, ignora este correo.
            
            Saludos,
            Equipo ChaosCompany
            '''
            
            try:
                print("📤 Enviando correo electrónico...")
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                print("✅ Correo enviado exitosamente")
                messages.success(request, 'Se ha enviado un enlace de recuperación a tu correo electrónico.')
            except Exception as e:
                print(f"💥 Error enviando correo: {e}")
                messages.error(request, 'Error al enviar el correo. Intenta nuevamente.')
            
            return redirect('forgot_password')
            
        except CustomUser.DoesNotExist:
            print("❌ Usuario no encontrado")
            # Por seguridad, no reveles si el email existe o no
            messages.success(request, 'Si el correo existe en nuestro sistema, recibirás un enlace de recuperación.')
            return redirect('forgot_password')
        except Exception as e:
            print(f"💥 Error inesperado: {e}")
            messages.error(request, 'Error al procesar la solicitud. Intenta nuevamente.')
    
    return render(request, 'accounts/forgot_password.html')

def reset_password_view(request, token):
    print(f"🔄 Vista restablecer contraseña llamada con token: {token}")
    
    # Verificar token y usuario
    session_token = request.session.get('reset_token')
    user_id = request.session.get('reset_user_id')
    
    print(f"🔍 Token en sesión: {session_token}")
    print(f"🔍 User ID en sesión: {user_id}")
    
    if not session_token or session_token != token or not user_id:
        print("❌ Token inválido o expirado")
        messages.error(request, 'El enlace de recuperación es inválido o ha expirado.')
        return redirect('login')
    
    try:
        user = CustomUser.objects.get(id=user_id)
        print(f"👤 Usuario válido: {user.username}")
        
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            print("📨 POST recibido en reset password")
            
            if new_password == confirm_password:
                if len(new_password) >= 8:
                    user.set_password(new_password)
                    user.save()
                    print("✅ Contraseña actualizada exitosamente")
                    
                    # Limpiar la sesión
                    if 'reset_token' in request.session:
                        del request.session['reset_token']
                    if 'reset_user_id' in request.session:
                        del request.session['reset_user_id']
                    print("🧹 Sesión limpiada")
                    
                    messages.success(request, 'Contraseña restablecida correctamente. Ahora puedes iniciar sesión.')
                    return redirect('login')
                else:
                    messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
            else:
                messages.error(request, 'Las contraseñas no coinciden.')
        
        return render(request, 'accounts/reset_password.html', {'token': token})
    
    except CustomUser.DoesNotExist:
        print("❌ Usuario no encontrado")
        messages.error(request, 'Usuario no encontrado.')
        return redirect('login')

# ===== VISTAS DEL CARRITO DE COMPRAS =====

def add_to_cart(request):
    print("🛒 Vista agregar al carrito llamada")
    
    if request.method == 'POST':
        plan_type = request.POST.get('plan_type')
        price = request.POST.get('price')
        
        print(f"📦 Plan seleccionado: {plan_type}, Precio: ${price}")
        
        # Inicializar carrito en sesión si no existe
        if 'cart' not in request.session:
            request.session['cart'] = []
            print("🆕 Carrito inicializado en sesión")
        
        # Agregar item al carrito
        cart_item = {
            'plan_type': plan_type,
            'price': price,
            'name': f'Plan {plan_type.title()}'
        }
        
        # Limpiar carrito anterior y agregar nuevo item (solo un plan a la vez)
        request.session['cart'] = [cart_item]
        request.session.modified = True
        
        print(f"✅ Plan {plan_type} agregado al carrito: {request.session['cart']}")
        messages.success(request, f'Plan {plan_type.title()} agregado al carrito')
        return redirect('cart')
    
    print("❌ Método no permitido")
    return redirect('membresias')

def remove_from_cart(request):
    print("🗑️ Vista remover del carrito llamada")
    
    if request.method == 'POST':
        plan_type = request.POST.get('plan_type')
        print(f"📦 Removiendo plan: {plan_type}")
        
        if 'cart' in request.session:
            # Eliminar el item del carrito
            request.session['cart'] = [
                item for item in request.session['cart'] 
                if item['plan_type'] != plan_type
            ]
            request.session.modified = True
            print(f"✅ Plan {plan_type} removido del carrito")
            messages.success(request, 'Plan removido del carrito')
        
        return redirect('cart')
    
    print("❌ Método no permitido")
    return redirect('cart')

def cart_view(request):
    print("🛍️ Vista carrito llamada")
    
    cart_items = request.session.get('cart', [])
    print(f"📦 Items en carrito: {cart_items}")
    
    # Calcular totales
    total_price = sum(float(item['price']) for item in cart_items)
    tax_amount = total_price * 0.16  # 16% de IVA
    grand_total = total_price + tax_amount
    
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'tax_amount': round(tax_amount, 2),
        'grand_total': round(grand_total, 2),
    }
    
    print(f"💰 Totales calculados - Subtotal: ${total_price}, Impuestos: ${tax_amount}, Total: ${grand_total}")
    return render(request, 'main/carrito.html', context)

@login_required
def checkout_view(request):
    """Redirigir al formulario de pago en lugar de procesar directamente"""
    print("💳 Vista checkout llamada - redirigiendo a formulario de pago")
    
    cart_items = request.session.get('cart', [])
    print(f"📦 Items en carrito para checkout: {cart_items}")
    
    if not cart_items:
        print("❌ Carrito vacío")
        messages.error(request, 'Tu carrito está vacío')
        return redirect('cart')
    
    # En lugar de procesar directamente, redirigir al formulario de pago
    print("🔄 Redirigiendo al formulario de pago")
    return redirect('payment_page')

# ===== VISTAS DE PAGO =====

@login_required
def payment_page(request):
    """Página del formulario de pago"""
    print("💳 Vista payment_page llamada")
    
    # Obtener datos del carrito
    cart_items = request.session.get('cart', [])
    if not cart_items:
        messages.error(request, 'No hay items en el carrito')
        return redirect('cart')
    
    item = cart_items[0]
    plan_type = item.get('plan_type')
    base_price = float(item.get('price', 0))
    
    # Calcular impuestos y total
    tax_amount = base_price * 0.16 if base_price > 0 else 0
    total_amount = base_price + tax_amount
    
    print(f"💰 Procesando pago - Plan: {plan_type}, Total: ${total_amount}")
    
    return render(request, 'main/payment.html', {
        'plan_type': plan_type,
        'base_price': base_price,
        'tax_amount': round(tax_amount, 2),
        'amount': round(total_amount, 2),
        'title': 'Proceso de Pago'
    })

@login_required
def process_payment(request):
    """Procesar el pago del usuario"""
    print("💳 Vista process_payment llamada")
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            plan_type = request.POST.get('plan_type')
            amount_str = request.POST.get('amount', '0')
            card_holder = request.POST.get('card_holder', '').strip()
            card_number = request.POST.get('card_number', '').replace(' ', '')
            expiry_date = request.POST.get('expiry_date')
            cvv = request.POST.get('cvv')
            email = request.POST.get('email', request.user.email)
            
            # CORRECCIÓN: Manejar formato de número con coma decimal
            print(f"💰 Monto recibido como string: '{amount_str}'")
            
            # Reemplazar coma por punto para conversión a float
            amount_str = amount_str.replace(',', '.')
            amount = float(amount_str)
            
            print(f"📨 Datos de pago recibidos - Plan: {plan_type}, Monto: ${amount}")
            
            # Validaciones básicas
            if not all([card_holder, card_number, expiry_date, cvv]):
                messages.error(request, 'Todos los campos son obligatorios')
                return redirect('payment_page')
            
            if len(card_number) < 13:
                messages.error(request, 'Número de tarjeta inválido')
                return redirect('payment_page')
            
            if len(cvv) != 3:
                messages.error(request, 'CVV inválido')
                return redirect('payment_page')
            
            # Validar fecha de expiración
            try:
                month, year = expiry_date.split('/')
                month = int(month)
                year = int('20' + year)  # Asumimos años 2000+
                
                current_date = timezone.now()
                if year < current_date.year or (year == current_date.year and month < current_date.month):
                    messages.error(request, 'La tarjeta ha expirado')
                    return redirect('payment_page')
            except ValueError:
                messages.error(request, 'Formato de fecha inválido (MM/AA)')
                return redirect('payment_page')
            
            # SIMULAR PROCESAMIENTO DE PAGO EXITOSO
            transaction_id = str(uuid.uuid4())[:8].upper()
            print(f"🔐 Transacción simulada: {transaction_id}")
            
            # Crear orden de compra - AHORA VIENE DE SUBSCRIPTIONS
            order = PaymentOrder.objects.create(
                user=request.user,
                plan_type=plan_type,
                amount=amount,
                status='completed',
                payment_method='credit_card',
                transaction_id=transaction_id,
                card_last_four=card_number[-4:],
                customer_email=email
            )
            
            # Actualizar membresía del usuario
            user_profile = request.user
            user_profile.membership_type = plan_type
            user_profile.membership_start = timezone.now()
            user_profile.membership_expiry = timezone.now() + timedelta(days=30)  # 1 mes
            user_profile.is_active_member = True
            user_profile.save()
            
            print(f"✅ Membresía actualizada para {user_profile.username}: {plan_type}")
            
            # Limpiar carrito
            if 'cart' in request.session:
                del request.session['cart']
                print("🧹 Carrito limpiado")
            
            messages.success(request, f'¡Pago exitoso! Tu suscripción {plan_type} ha sido activada.')
            return redirect('payment_success', order_id=order.id)
            
        except ValueError as e:
            print(f"💥 Error de conversión numérica: {e}")
            messages.error(request, 'Error en el formato del monto. Contacta al soporte.')
            return redirect('payment_page')
        except Exception as e:
            print(f"💥 Error procesando el pago: {e}")
            messages.error(request, f'Error procesando el pago: {str(e)}')
            return redirect('payment_page')
    
    return redirect('cart')

@login_required
def payment_success(request, order_id):
    """Página de confirmación de pago exitoso"""
    print(f"🎉 Vista payment_success llamada - Orden: {order_id}")
    
    order = get_object_or_404(PaymentOrder, id=order_id, user=request.user)
    
    return render(request, 'main/payment_success.html', {
        'order': order,
        'title': 'Pago Exitoso'
    })

@login_required
def payment_cancel(request):
    """Página para pagos cancelados"""
    print("❌ Pago cancelado")
    messages.info(request, 'El pago fue cancelado. Puedes intentarlo nuevamente.')
    return redirect('cart')

def send_confirmation_email(user, order, email):
    """Función para enviar email de confirmación (simulada)"""
    print(f"📧 Email simulado enviado a {email}: Confirmación de orden #{order.id}")