from django.contrib.auth.models import AbstractUser
from django.db import models

class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre


class User(AbstractUser):
    ci = models.PositiveIntegerField("CI", unique=True, null=False, blank=False)
    nombre = models.CharField("Nombre completo", max_length=100, null=True, blank=True)
    celular = models.CharField("Celular", max_length=20, null=True, blank=True)

    # Relación con el rol (estudiante, tutor, docente, etc.)
    rol = models.ForeignKey('Rol', on_delete=models.SET_NULL, null=True, blank=True, related_name='usuarios')

    # Relación autorreferencial: un estudiante tiene un tutor (que también es User)
    tutor = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='estudiantes'
    )

    # Recomendación: asegurar que el email también sea único
    email = models.EmailField(unique=True, null=False)

    def __str__(self):
        return self.nombre or self.username

class Curso(models.Model):
    nombre = models.CharField(max_length=100)
    nivel = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.nombre


class Gestion(models.Model):
    nombre = models.CharField(max_length=10, unique=True)
    estado = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre


class Periodo(models.Model):
    nombre = models.CharField(max_length=50)
    fecha = models.DateField(null=True, blank=True)
    estado = models.BooleanField(default=False)
    gestion = models.ForeignKey(Gestion, on_delete=models.CASCADE, related_name='periodos')

    def __str__(self):
        return f"{self.nombre} - {self.gestion.nombre}"


class Materia(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class Asignacion(models.Model):
    docente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='asignaciones')
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='asignaciones')
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name='asignaciones')
    gestion = models.ForeignKey(Gestion, on_delete=models.CASCADE, related_name='asignaciones')

    def __str__(self):
        return f"{getattr(self.docente, 'nombre', self.docente.username)} - {self.materia.nombre} - {self.curso.nombre}"


class Inscripcion(models.Model):
    estudiante = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inscripciones')
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='inscripciones')
    gestion = models.ForeignKey(Gestion, on_delete=models.CASCADE, related_name='inscripciones')

    def __str__(self):
        return f"{getattr(self.estudiante, 'nombre', self.estudiante.username)} - {self.curso.nombre} ({self.gestion.nombre})"


class Evaluacion(models.Model):
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50)  # Ej: "Tarea", "Examen"
    fecha = models.DateField(null=True, blank=True)
    valor = models.FloatField()
    asignacion = models.ForeignKey(Asignacion, on_delete=models.CASCADE, related_name='evaluaciones')
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE, related_name='evaluaciones')

    def __str__(self):
        return f"{self.nombre} - {self.asignacion.materia.nombre} - {self.periodo.nombre}"


class Nota(models.Model):
    nota = models.FloatField()
    inscripcion = models.ForeignKey(Inscripcion, on_delete=models.CASCADE, related_name='notas')
    evaluacion = models.ForeignKey(Evaluacion, on_delete=models.CASCADE, related_name='notas')

    def __str__(self):
        return f"{getattr(self.inscripcion.estudiante, 'nombre', self.inscripcion.estudiante.username)} - {self.evaluacion.nombre}: {self.nota}"
