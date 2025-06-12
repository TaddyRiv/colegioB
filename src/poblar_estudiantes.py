import os
import django
import sys
import random
from django.utils.crypto import get_random_string
from django.db import transaction

# Configuración de entorno Django
sys.path.append('/app/src')  # Ajusta si es necesario
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'colegioB.settings.dev')
django.setup()

from apps.usuarios.models import User, Rol, Curso, Gestion, Inscripcion

@transaction.atomic
def poblar_estudiantes():
    rol_estudiante = Rol.objects.get(nombre='estudiante')
    rol_tutor = Rol.objects.get(nombre='tutor')
    gestion_2024 = Gestion.objects.get(id=2)
    gestion_2025 = Gestion.objects.get(id=3)

    cursos = Curso.objects.filter(nivel='Secundaria')
    ci_counter = 30000

    for curso in cursos:
        # Tutor único por curso
        tutor, _ = User.objects.get_or_create(
            ci=ci_counter,
            defaults={
                'username': f'tutor_{curso.id}',
                'nombre': f'Tutor Curso {curso.nombre}',
                'email': f'tutor{curso.id}@colegio.com',
                'celular': f'7{ci_counter}',
                'rol': rol_tutor
            }
        )
        tutor.set_password(str(ci_counter))
        tutor.save()
        ci_counter += 1

        for i in range(30):
            username = f"EST_{get_random_string(6).upper()}"
            estudiante = User.objects.create(
                username=username,
                nombre=f"Estudiante {curso.nombre} - {i+1}",
                ci=ci_counter,
                email=f"est{curso.id}_{i}@colegio.com",
                celular=f"77{ci_counter}",
                rol=rol_estudiante,
                tutor=tutor
            )
            estudiante.set_password(str(ci_counter))
            estudiante.save()

            for gestion in [gestion_2024, gestion_2025]:
                Inscripcion.objects.get_or_create(
                    estudiante=estudiante,
                    curso=curso,
                    gestion=gestion
                )
            ci_counter += 1

    print("✅ Estudiantes, tutores e inscripciones creados correctamente.")

if __name__ == '__main__':
    poblar_estudiantes()
