from django.http import JsonResponse
from django.urls import path,include

def test_view(request):
    return JsonResponse({"message": "El backend Django está funcionando correctamente 🎉"})

urlpatterns = [
    path('', test_view),
    path('api/auth/', include('apps.usuarios.urls')),  # 👈 Aquí lo conectás
]
