from pathlib import Path
import os
# La importación de dj_database_url debe estar comentada o eliminada si no está en requirements.txt
# import dj_database_url 

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-8i0hw4ovr8g!226b=3^b-q9e1516+c9h1#!@^1=k_*_icr$r10')

# SECURITY WARNING: don't run with debug turned on in production!
# Lee la variable de entorno DEBUG que has configurado en Azure
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# DOMINIO ACTUAL
ALLOWED_HOSTS = [
    'chaos-bsb8bjf6dkfgfhds.canadacentral-01.azurewebsites.net', 
    'localhost',
    '127.0.0.1',
]

# Application definition
INSTALLED_APPS = [
    'whitenoise.runserver_nostatic',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'main',
    'games',
    'subscriptions',
    'gaming',
    'support',
]

# Modelo de usuario personalizado
AUTH_USER_MODEL = 'accounts.CustomUser'

# URLs de autenticación
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise para servir archivos estáticos en producción
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'chaoscompany.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'chaoscompany.wsgi.application'

# --- 🎯 Database - CONFIGURACIÓN AZURE MYSQL (SSL DESACTIVADO PARA DIAGNÓSTICO) 🎯 ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'chaoscompany_db'),
        'USER': os.environ.get('DB_USER', 'admin_chaoscompany'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'ChaosCompany_2024*'),
        'HOST': os.environ.get('DB_HOST', 'mysql-chaoscompany-django.mysql.database.azure.com'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'OPTIONS': {
            # 🚨 SSL COMENTADO: Prueba para ver si el problema es la contraseña/host, no el certificado.
            # 'ssl': {'ca': os.path.join(BASE_DIR, 'DigiCertGlobalRootG2.crt.pem')},
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        }
    }
}
# -------------------------------------------------------------------

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Para desarrollo - muestra emails en consola
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@chaoscompany.com'

# Internationalization
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
# STATIC_ROOT es donde 'collectstatic' reunirá los archivos para WhiteNoise.
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise configuration
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Configuración de archivos multimedia
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
