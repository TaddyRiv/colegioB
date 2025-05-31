from .base import *

import os

# Secretos del entorno de desarrollo
SECRET_KEY = os.getenv("SECRET_KEY", "clave-desarrollo-insegura")
DEBUG = os.getenv("DEBUG", "True") == "True"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# Middleware y apps adicionales solo para desarrollo
INSTALLED_APPS += [
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    *MIDDLEWARE  # conserva el resto del base.py
]

# CORS solo para desarrollo
CORS_ALLOWED_ORIGINS = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
]
CORS_ALLOW_CREDENTIALS = True
