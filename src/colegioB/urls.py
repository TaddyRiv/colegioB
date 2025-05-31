from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/usuarios/', include('apps.usuarios.api.urls')),  # 👈 Aquí debes apuntar a donde están tus views reales
]
