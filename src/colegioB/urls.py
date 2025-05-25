from django.http import JsonResponse
from django.urls import path,include
from django.contrib import admin

def test_view(request):
    return JsonResponse({"message": "El backend Django está funcionando correctamente 🎉"})

urlpatterns = [
    path('', test_view),
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.usuarios.urls')),  # 👈 Aquí lo conectás
]
