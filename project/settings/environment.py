import os
from pathlib import Path
import environ

env = environ.Env()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

environ.Env.read_env(BASE_DIR / '.env')
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'INSECURE')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if os.environ.get('DEBUG') == '1' else False

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS")

ROOT_URLCONF = 'project.urls'

WSGI_APPLICATION = 'project.wsgi.application'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
