from django.urls import path
from apps.usuarios.auth_views import (
    EstudianteRegisterView,
    DocenteRegisterView,
    InscripcionCreateView,
    EstudianteListView,
    CursoListView,
    GestionListView,
    LoginView,
    TutorListByCIView,
)

urlpatterns = [
    path('registrar-estudiante/', EstudianteRegisterView.as_view(), name='registrar-estudiante'),
    path('registrar-docente/', DocenteRegisterView.as_view(), name='registrar-docente'),
    path('inscribir/', InscripcionCreateView.as_view(), name='crear-inscripcion'),
    path('estudiantes/', EstudianteListView.as_view(), name='listar-estudiantes'),
    path('cursos/', CursoListView.as_view(), name='listar-cursos'),
    path('gestiones/', GestionListView.as_view(), name='listar-gestiones'),
    path('login/', LoginView.as_view(), name='login'),
    path('tutores/', TutorListByCIView.as_view(), name='listar-tutores'),
]
