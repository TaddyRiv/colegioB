from django.urls import path
from apps.usuarios.auth_views import EstudianteRegisterView, DocenteRegisterView


urlpatterns = [
   path('registrar-estudiante/', EstudianteRegisterView.as_view(), name='registrar-estudiante'),
   path('registrar-docente/', DocenteRegisterView.as_view(), name='registrar-docente'),
]
