from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from apps.usuarios.models import User
from rest_framework import generics
from .serializers import TutorSerializer
from rest_framework.permissions import IsAuthenticated  # o AllowAny si querés
from rest_framework.permissions import AllowAny
from .serializers import UserRegisterSerializer


class TutorListView(generics.ListAPIView):
    serializer_class = TutorSerializer

    def get_queryset(self):
        return User.objects.filter(rol__nombre='tutor')


class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]



#login
class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'username': user.username,
                'rol': user.rol.nombre if user.rol else None,
                'nombre': user.nombre
            })
        else:
            return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)
