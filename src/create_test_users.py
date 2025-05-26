import os
import django
import sys

# Configurar entorno
sys.path.append('/app/src')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'colegioB.settings.dev')
django.setup()

from apps.usuarios.models import User, Rol
from django.utils.crypto import get_random_string
from django.db import transaction

def crear_roles():
    rol_docente, _ = Rol.objects.get_or_create(nombre='docente')
    rol_estudiante, _ = Rol.objects.get_or_create(nombre='estudiante')
    rol_tutor, _ = Rol.objects.get_or_create(nombre='tutor')
    return rol_docente, rol_estudiante, rol_tutor


@transaction.atomic
def crear_usuarios():
    rol_docente, rol_estudiante, rol_tutor = crear_roles()

    # Crear tutor si no existe
    tutor_ci = 2345678
    tutor, created = User.objects.get_or_create(
        ci=tutor_ci,
        defaults={ 
            'email': 'tutor1@colegio.com',
            'nombre': 'Laura Martínez',
            'rol': rol_tutor,
            'celular': '555123456'
        }
    )
    if created:
        tutor.set_password(str(tutor_ci))  # contraseña = ci
        tutor.save()
        tutor.username = f"tutor_{tutor.id}"
        tutor.save()
        print("Tutor creado:", tutor.username)
    else:
        print("Tutor ya existía:", tutor.username)

    # Crear docente
    docente_ci = 12345676
    docente, created = User.objects.get_or_create(
        ci=docente_ci,
        defaults={
            'username': 'docente1',
            'email': 'docente1@colegio.com',
            'nombre': 'Juan Pérez',
            'rol': rol_docente,
            'celular': '123456789'
        }
    )
    if created:
        docente.set_password(str(docente_ci))
        docente.save()
        print("Docente creado:", docente.username)
    else:
        print("Docente ya existía:", docente.username)

    # Crear estudiante con username tipo EST_ABC123
    estudiante_ci = 12345678
    username_codigo = get_random_string(length=6).upper()
    estudiante_username = f"EST_{username_codigo}"

    estudiante, created = User.objects.get_or_create(
        ci=estudiante_ci,
        defaults={
            'username': estudiante_username,
            'email': 'estudiante1@colegio.com',
            'nombre': 'Ana Gómez',
            'rol': rol_estudiante,
            'celular': '987654321',
            'tutor': tutor
        }
    )
    if created:
        estudiante.set_password(str(estudiante_ci))
        estudiante.save()
        print("Estudiante creado:", estudiante.username, "→ Tutor:", tutor.username)
    else:
        print("Estudiante ya existía:", estudiante.username)

if __name__ == '__main__':
    crear_usuarios()
