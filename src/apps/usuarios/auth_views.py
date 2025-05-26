from rest_framework import generics
from rest_framework.permissions import AllowAny
from apps.usuarios.serializers import EstudianteRegisterSerializer

from .serializers import DocenteRegisterSerializer

class DocenteRegisterView(generics.CreateAPIView):
    serializer_class = DocenteRegisterSerializer
    permission_classes = [AllowAny]
    
    
class EstudianteRegisterView(generics.CreateAPIView):
    serializer_class = EstudianteRegisterSerializer
    permission_classes = [AllowAny]
