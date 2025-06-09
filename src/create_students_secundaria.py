import os
import sys
import django

# Setup entorno
sys.path.append('/app/src')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'colegioB.settings.dev')
django.setup()

from apps.usuarios.models import User, Rol, Curso, Gestion, Inscripcion
from django.utils.crypto import get_random_string
from django.db import transaction

@transaction.atomic
def crear_estudiantes_secundaria():
    rol_estudiante = Rol.objects.get(nombre='estudiante')
    tutor = User.objects.get(ci=9999999)  # Asumiendo que ya lo creaste con este CI
    gestion = Gestion.objects.get(nombre='2025')

    cursos_secundaria = Curso.objects.filter(nivel__iexact='Secundaria')
    ci_base = 20001  # CI inicial para los estudiantes

    for curso in cursos_secundaria:
        print(f"\n📘 Curso: {curso.nombre}")

        for i in range(10):
            ci = ci_base + i
            username = f"EST_{get_random_string(6).upper()}"
            email = f"{curso.nombre.lower().replace(' ', '')}_est{i+1}@colegio.com"

            estudiante, created = User.objects.get_or_create(
                ci=ci,
                defaults={
                    'username': username,
                    'email': email,
                    'nombre': f"{curso.nombre} Estudiante {i+1}",
                    'celular': f"760{ci}",
                    'rol': rol_estudiante,
                    'tutor': tutor
                }
            )
            if created:
                estudiante.set_password(str(ci))
                estudiante.save()
                print(f"✅ {username} creado con CI {ci}")
            else:
                print(f"⏩ {estudiante.username} ya existía")

            Inscripcion.objects.get_or_create(
                estudiante=estudiante,
                curso=curso,
                gestion=gestion
            )

        ci_base += 10  # Salto para el siguiente curso

if __name__ == '__main__':
    crear_estudiantes_secundaria()
