import os
import django
import sys
import random
from datetime import datetime, timedelta

# Configurar entorno
sys.path.append('/app/src')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'colegioB.settings.dev')
django.setup()

from apps.usuarios.models import Asignacion, Inscripcion, User
from apps.usuarios.models import Evaluacion, Nota, Periodo, Asignacion, Inscripcion, User

# Generar fecha aleatoria
def fecha_random():
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 6, 30)
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)

# Crear evaluaciones y subir notas
def poblar_evaluaciones_y_notas():
    asignaciones = Asignacion.objects.select_related('materia', 'curso', 'gestion').all()
    periodo_activo = Periodo.objects.filter(estado=True).first()

    for asignacion in asignaciones:
        for i in range(1, 4):
            Evaluacion.objects.get_or_create(
                nombre=f"Examen {i}",
                tipo="Examen",
                valor=30 if i == 3 else 20,
                fecha=fecha_random(),
                asignacion=asignacion,
                periodo=periodo_activo
            )
        for i in range(1, 6):
            Evaluacion.objects.get_or_create(
                nombre=f"Práctico {i}",
                tipo="Práctico",
                valor=20,
                fecha=fecha_random(),
                asignacion=asignacion,
                periodo=periodo_activo
            )

        evaluaciones = Evaluacion.objects.filter(asignacion=asignacion)

        for evaluacion in evaluaciones:
            inscripciones = Inscripcion.objects.filter(
                curso=asignacion.curso,
                gestion=asignacion.gestion
            )
            for inscripcion in inscripciones:
                Nota.objects.update_or_create(
                    evaluacion=evaluacion,
                    inscripcion=inscripcion,
                    defaults={'nota': round(random.uniform(35, 100), 2)}
                )

poblar_evaluaciones_y_notas()
