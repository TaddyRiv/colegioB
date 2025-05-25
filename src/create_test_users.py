import os
import django
import sys

# Configurar entorno
sys.path.append('/app/src')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'colegioB.settings.dev')
django.setup()

from apps.usuarios.models import User, Rol


def crear_roles():
    rol_docente, _ = Rol.objects.get_or_create(nombre='docente')
    rol_estudiante, _ = Rol.objects.get_or_create(nombre='estudiante')
    rol_tutor, _ = Rol.objects.get_or_create(nombre='tutor')
    return rol_docente, rol_estudiante, rol_tutor


def crear_usuarios():
    rol_docente, rol_estudiante, rol_tutor = crear_roles()

    tutor, created = User.objects.get_or_create(
        username='tutor1',
        defaults={
            'ci': '2345678',  # campo ci obligatorio
            'email': 'tutor1@colegio.com',
            'nombre': 'Laura Martínez',
            'rol': rol_tutor,
            'celular': '555123456'
        }
    )
    if created:
        tutor.set_password('tutor123')
        tutor.save()
        print("Tutor creado")
    else:
        print("Tutor ya existía")

    docente, created = User.objects.get_or_create(
        username='docente1',
        defaults={
            'ci': '12345676',  # campo ci obligatorio
            'email': 'docente1@colegio.com',
            'nombre': 'Juan Pérez',
            'rol': rol_docente,
            'celular': '123456789'
        }
    )
    if created:
        docente.set_password('docente123')
        docente.save()
        print("Docente creado")
    else:
        print("Docente ya existía")

    estudiante, created = User.objects.get_or_create(
        username='estudiante1',
        defaults={
            'ci': '12345678', 
            'email': 'estudiante1@colegio.com',
            'nombre': 'Ana Gómez',
            'rol': rol_estudiante,
            'celular': '987654321',
            'tutor': tutor
        }
    )
    if created:
        estudiante.set_password('estudiante123')
        estudiante.save()
        print("Estudiante creado con tutor asignado")
    else:
        print("Estudiante ya existía")


if __name__ == '__main__':
    crear_usuarios()
