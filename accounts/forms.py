from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import CustomUser

class SignupForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input-field', 
            'placeholder': 'Correo electrónico',
            'required': 'true'
        })
    )
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input-field', 
            'placeholder': 'Nombre',
            'required': 'true'
        })
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input-field', 
            'placeholder': 'Apellido',
            'required': 'true'
        })
    )
    
    # Campo membership_type con las opciones correctas del modelo
    membership_type = forms.ChoiceField(
        required=True,
        choices=CustomUser._meta.get_field('membership_type').choices,
        widget=forms.Select(attrs={
            'class': 'form-input-field',
            'required': 'true'
        })
    )
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'membership_type', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input-field', 
                'placeholder': 'Nombre de usuario',
                'required': 'true'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar campos de contraseña
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input-field', 
            'placeholder': 'Contraseña',
            'required': 'true'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-input-field', 
            'placeholder': 'Confirmar contraseña',
            'required': 'true'
        })
        
        # Remover textos de ayuda
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''
        self.fields['username'].help_text = ''

    # VALIDACIÓN PARA USUARIO EXISTENTE
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username__iexact=username).exists():
            raise ValidationError('Este nombre de usuario ya está registrado. Por favor elige otro.')
        return username

    # VALIDACIÓN PARA CORREO EXISTENTE
    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise ValidationError('Este correo electrónico ya está registrado. ¿Ya tienes una cuenta?')
        return email

    # VALIDACIÓN PARA CONTRASEÑAS
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError('Las contraseñas no coinciden. Por favor verifica.')
        
        if len(password1) < 8:
            raise ValidationError('La contraseña debe tener al menos 8 caracteres.')
        
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email'].lower()
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input-field', 
            'placeholder': 'Usuario o correo electrónico',
            'required': 'true',
            'autocomplete': 'off'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input-field', 
            'placeholder': 'Contraseña',
            'required': 'true'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'remember-checkbox'})
    )

    # PERMITIR LOGIN CON EMAIL O USERNAME
    def clean_username(self):
        username = self.cleaned_data.get('username')
        # El AuthenticationForm original manejará la autenticación
        return username

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'membership_type', 'password1', 'password2')

class CustomUserChangeForm(UserChangeForm):
    # Eliminar el campo de contraseña del formulario de edición
    password = None
    
    # Campo para subir imagen personalizada
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'file-input-hidden',
            'accept': 'image/*'
        })
    )
    
    birth_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-input-field',
            'type': 'date'
        })
    )
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'membership_type', 'profile_picture', 'birth_date')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Añadir clases CSS y placeholders a los campos
        self.fields['username'].widget.attrs.update({
            'class': 'form-input-field',
            'placeholder': 'Nombre de usuario'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-input-field',
            'placeholder': 'Correo electrónico'
        })
        self.fields['first_name'].widget.attrs.update({
            'class': 'form-input-field',
            'placeholder': 'Nombre'
        })
        self.fields['last_name'].widget.attrs.update({
            'class': 'form-input-field',
            'placeholder': 'Apellido'
        })
        self.fields['membership_type'].widget.attrs.update({
            'class': 'form-input-field'
        })
        self.fields['birth_date'].widget.attrs.update({
            'class': 'form-input-field'
        })
        
        # Personalizar las opciones del membership_type
        self.fields['membership_type'].choices = CustomUser._meta.get_field('membership_type').choices
    
    # VALIDACIÓN PARA CORREO EXISTENTE (excluyendo el usuario actual)
    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if CustomUser.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Este correo electrónico ya está registrado por otro usuario.')
        return email
    
    # VALIDACIÓN PARA USUARIO EXISTENTE (excluyendo el usuario actual)
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username__iexact=username).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Este nombre de usuario ya está registrado. Por favor elige otro.')
        return username
    
    # VALIDACIÓN PARA LA IMAGEN DE PERFIL
    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            # Validar tamaño del archivo (máximo 5MB)
            if profile_picture.size > 5 * 1024 * 1024:
                raise ValidationError('La imagen debe ser menor a 5MB.')
            
            # Validar tipo de archivo
            valid_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
            extension = profile_picture.name.split('.')[-1].lower()
            if extension not in valid_extensions:
                raise ValidationError('Formato de imagen no válido. Use JPG, PNG, GIF o WebP.')
        
        return profile_picture