from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from apps.usuarios.serializers import EstudianteRegisterSerializer,EstudianteSerializer ,CursoSerializer, GestionSerializer
from rest_framework.response import Response
from rest_framework import status
from .models import Inscripcion, User, Curso, Gestion
from .serializers import InscripcionSerializer
from .serializers import DocenteRegisterSerializer
from .serializers import TutorSerializer

class DocenteRegisterView(generics.CreateAPIView):
    serializer_class = DocenteRegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.docente_info, status=status.HTTP_201_CREATED)
 
    
class EstudianteRegisterView(generics.CreateAPIView):
    serializer_class = EstudianteRegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.estudiante_info, status=status.HTTP_201_CREATED)
    

class InscripcionCreateView(generics.CreateAPIView):
    queryset = Inscripcion.objects.all()
    serializer_class = InscripcionSerializer
    permission_classes = [AllowAny]
    
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "id": user.id,
                "username": user.username,
                "rol": user.rol.nombre if user.rol else None,
                "nombre": user.nombre
            })
        else:
            return Response({"error": "Credenciales inválidas"}, status=status.HTTP_401_UNAUTHORIZED)   
    
############pruebas###########

class EstudianteListView(generics.ListAPIView):
    queryset = User.objects.filter(rol__nombre='estudiante')
    serializer_class = EstudianteSerializer
    permission_classes = [AllowAny]

class CursoListView(generics.ListAPIView):
    queryset = Curso.objects.all()
    serializer_class = CursoSerializer
    permission_classes = [AllowAny]

class GestionListView(generics.ListAPIView):
    queryset = Gestion.objects.all()
    serializer_class = GestionSerializer
    permission_classes = [AllowAny]
    
class TutorListByCIView(APIView):
    def get(self, request):
        ci = request.query_params.get('ci')

        if ci:
            tutores = User.objects.filter(rol__nombre='tutor', ci=ci)
        else:
            tutores = User.objects.filter(rol__nombre='tutor')

        serializer = TutorSerializer(tutores, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)