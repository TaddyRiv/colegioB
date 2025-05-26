from django.urls import path,include

urlpatterns = [
  path('', include('apps.usuarios.api.urls')),  # 👈 importante
]
