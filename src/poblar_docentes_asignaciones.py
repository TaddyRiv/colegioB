import os
import django
import sys
import random
from django.db import transaction

sys.path.append('/app/src')  # Ajusta si es necesario
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'colegioB.settings.dev')
django.setup()

from apps.usuarios.models import User, Rol, Curso, Gestion, Materia, Asignacion

@transaction.atomic
def poblar_docentes():
    rol_docente = Rol.objects.get(nombre='docente')
    gestion = Gestion.objects.get(id=3)
    materias = list(Materia.objects.all())
    cursos = list(Curso.objects.filter(nivel='Secundaria'))

    docente_ci = 40000

    for d in range(5):  # 5 docentes
        docente = User.objects.create(
            username=f"docente_{d+1}",
            nombre=f"Docente {d+1}",
            email=f"doc{d+1}@colegio.com",
            celular=f"70{docente_ci}",
            ci=docente_ci,
            rol=rol_docente
        )
        docente.set_password(str(docente_ci))
        docente.save()
        docente_ci += 1

        cursos_sample = random.sample(cursos, 4)
        materias_sample = random.sample(materias, 3)

        for curso in cursos_sample:
            for materia in materias_sample:
                Asignacion.objects.get_or_create(
                    docente=docente,
                    materia=materia,
                    curso=curso,
                    gestion=gestion
                )

    print("✅ Docentes y asignaciones creados correctamente.")

if __name__ == '__main__':
    poblar_docentes()
