from django.http import JsonResponse
from django.urls import path

def test_view(request):
    return JsonResponse({"message": "El backend Django está funcionando correctamente 🎉"})

urlpatterns = [
    path('', test_view),
]
