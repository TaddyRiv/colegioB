import os
import django

# Configurar entorno
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.colegioB.settings.dev')
django.setup()

from apps.usuarios.models import User

# Crear usuario docente
docente, created = User.objects.get_or_create(
    username='doc',
    defaults={
        'nombre': 'raul ortiz',
        'ci': '12345678',
        'rol': 'docente',
        'email': 'docente1@ejemplo.com',
    }
)
if created:
    docente.set_password('123456')
    docente.save()
    print("✅ Usuario docente creado")
else:
    print("🔁 Usuario docente ya existe")

# Crear usuario estudiante
estudiante, created = User.objects.get_or_create(
    username='estudiante1',
    defaults={
        'nombre': 'taddy riveros',
        'ci': '6991496',
        'rol': 'estudiante',
        'email': 'estudiante1@ejemplo.com',
    }
)
if created:
    estudiante.set_password('123456')
    estudiante.save()
    print("✅ Usuario estudiante creado")
else:
    print("🔁 Usuario estudiante ya existe")
