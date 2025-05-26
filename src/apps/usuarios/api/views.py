from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.usuarios.serializers import EstudianteRegisterSerializer 

class EstudianteRegisterView(APIView):
    def post(self, request):
        serializer = EstudianteRegisterSerializer(data=request.data)
        if serializer.is_valid():
            estudiante = serializer.save()
            return Response({
                "mensaje": "Estudiante registrado exitosamente.",
                "username": estudiante.username,
                "tutor": estudiante.tutor.username
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
