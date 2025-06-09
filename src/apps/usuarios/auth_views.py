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
from rest_framework.generics import ListAPIView
from apps.usuarios.models import User
from apps.usuarios.serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated
from apps.usuarios.models import Materia, Evaluacion, Nota, Asignacion
from django.db import IntegrityError
from rest_framework import serializers
from apps.usuarios.serializers import MateriaSerializer
from apps.usuarios.models import Periodo
from apps.usuarios.serializers import RegistrarNotasSerializer


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
            rol_nombre = user.rol.nombre if user.rol else None

            response_data = {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "id": user.id,
                "username": user.username,
                "rol": rol_nombre,
                "nombre": user.nombre,
            }

            # Añadir el ID del estudiante si aplica
            if rol_nombre == "estudiante":
                response_data["estudiante"] = { "id": user.id }

            return Response(response_data)

        return Response({"error": "Credenciales inválidas"}, status=status.HTTP_401_UNAUTHORIZED)


class MateriasCursoEstudianteView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        estudiante = request.user
        inscripciones = Inscripcion.objects.filter(estudiante=estudiante)
        materias = []

        for inscripcion in inscripciones:
            asignaciones = Asignacion.objects.filter(
                curso=inscripcion.curso,
                gestion=inscripcion.gestion
            ).select_related('materia')

            for asignacion in asignaciones:
                materias.append({
                    "materia_id": asignacion.materia.id,
                    "materia_nombre": asignacion.materia.nombre,
                    "curso": inscripcion.curso.nombre,
                    "gestion": inscripcion.gestion.nombre
                })

        return Response({"materias": materias})

    
class EvaluacionesMateriaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, materia_id):
        try:
            # Obtener la materia
            materia = Materia.objects.get(id=materia_id)
            
            # Obtener todas las evaluaciones relacionadas con esta materia
            evaluaciones = Evaluacion.objects.filter(asignacion__materia=materia)
            
            # Obtenemos las notas de cada evaluación
            evaluaciones_con_notas = []
            for evaluacion in evaluaciones:
                notas = Nota.objects.filter(evaluacion=evaluacion)
                notas_data = [{"estudiante": nota.inscripcion.estudiante.nombre, "nota": nota.nota} for nota in notas]
                evaluaciones_con_notas.append({
                    "evaluacion": evaluacion.nombre,
                    "tipo": evaluacion.tipo,
                    "fecha": evaluacion.fecha,
                    "notas": notas_data
                })
            
            return Response({"evaluaciones": evaluaciones_con_notas})
        
        except Materia.DoesNotExist:
            return Response({"error": "Materia no encontrada"}, status=404)


class RegistrarAsignacionesDocenteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # Validar rol Docente (puedes ajustar el nombre exacto si usas ID también)
        if not user.rol or user.rol.nombre.lower() != "docente":
            return Response({"error": "Solo los docentes pueden registrar asignaciones."}, status=status.HTTP_403_FORBIDDEN)

        materia_id = request.data.get("materia_id")
        curso_ids = request.data.get("curso_ids")

        if not materia_id or not curso_ids:
            return Response({"error": "materia_id y curso_ids son requeridos."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            materia = Materia.objects.get(id=materia_id)
        except Materia.DoesNotExist:
            return Response({"error": "Materia no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        gestion_id = 3  # Gestión 2025
        gestion = Gestion.objects.get(id=gestion_id)

        asignaciones_creadas = []
        asignaciones_existentes = []

        for curso_id in curso_ids:
            try:
                curso = Curso.objects.get(id=curso_id)
                asignacion, created = Asignacion.objects.get_or_create(
                    docente=user,
                    curso=curso,
                    materia=materia,
                    gestion=gestion
                )
                if created:
                    asignaciones_creadas.append(curso.nombre)
                else:
                    asignaciones_existentes.append(curso.nombre)
            except Curso.DoesNotExist:
                continue

        return Response({
            "creadas": asignaciones_creadas,
            "existentes": asignaciones_existentes
        }, status=status.HTTP_201_CREATED)


class MateriasDocenteView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Validar que el usuario sea un docente
        if not request.user.rol or request.user.rol.nombre.lower() != "docente":
            return Response({"error": "Acceso solo para docentes."}, status=403)

        # Obtener todas las materias disponibles
        materias = Materia.objects.all()
        serializer = MateriaSerializer(materias, many=True)

        return Response({"materias": serializer.data}, status=200)


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
    

class UsuarioListView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RegistrarEvaluacionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # Verificar si es docente
        if not user.rol or user.rol.nombre.lower() != "docente":
            return Response({"error": "Acceso restringido a docentes."}, status=403)

        data = request.data
        asignacion_id = data.get('asignacion_id')
        nombre = data.get('nombre')
        tipo = data.get('tipo')
        fecha = data.get('fecha')
        valor = data.get('valor')

        # Validar campos requeridos
        if not all([asignacion_id, nombre, tipo, valor]):
            return Response({"error": "Faltan campos obligatorios."}, status=400)

        try:
            asignacion = Asignacion.objects.get(id=asignacion_id, docente=user)
        except Asignacion.DoesNotExist:
            return Response({"error": "Asignación no encontrada o no pertenece al docente."}, status=404)

        # Buscar el periodo activo de la gestión de la asignación
        periodo_activo = Periodo.objects.filter(
            gestion=asignacion.gestion,
            estado=True
        ).first()

        if not periodo_activo:
            return Response({"error": "No hay un periodo activo en esta gestión."}, status=400)

        # Crear evaluación
        evaluacion = Evaluacion.objects.create(
            nombre=nombre,
            tipo=tipo,
            fecha=fecha,
            valor=valor,
            asignacion=asignacion,
            periodo=periodo_activo
        )

        return Response({
            "mensaje": "Evaluación registrada exitosamente.",
            "evaluacion": {
                "id": evaluacion.id,
                "nombre": evaluacion.nombre,
                "tipo": evaluacion.tipo,
                "fecha": evaluacion.fecha,
                "valor": evaluacion.valor,
                "materia": asignacion.materia.nombre,
                "curso": asignacion.curso.nombre,
                "gestion": asignacion.gestion.nombre,
                "periodo": periodo_activo.nombre,
            }
        }, status=201)


class MisAsignacionesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Validar que sea docente
        if not user.rol or user.rol.nombre.lower() != "docente":
            return Response({"error": "Acceso solo para docentes."}, status=403)

        asignaciones = Asignacion.objects.filter(docente=user).select_related("materia", "curso", "gestion")

        data = []
        for asignacion in asignaciones:
            data.append({
                "asignacion_id": asignacion.id,
                "materia": asignacion.materia.nombre,
                "curso": asignacion.curso.nombre,
                "nivel": asignacion.curso.nivel,
                "gestion": asignacion.gestion.nombre
            })

        return Response({"asignaciones": data}, status=200)


class EstudiantesPorAsignacionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, asignacion_id):
        user = request.user

        # Verificar que sea docente
        if not user.rol or user.rol.nombre.lower() != "docente":
            return Response({"error": "Acceso solo para docentes."}, status=403)

        try:
            asignacion = Asignacion.objects.get(id=asignacion_id, docente=user)
        except Asignacion.DoesNotExist:
            return Response({"error": "Asignación no encontrada o no pertenece al docente."}, status=404)

        inscripciones = Inscripcion.objects.filter(
            curso=asignacion.curso,
            gestion=asignacion.gestion
        ).select_related("estudiante")

        estudiantes = []
        for inscripcion in inscripciones:
            estudiante = inscripcion.estudiante
            estudiantes.append({
                "inscripcion_id": inscripcion.id,
                "estudiante_id": estudiante.id,
                "nombre": estudiante.nombre,
                "ci": estudiante.ci,
                "email": estudiante.email
            })

        return Response({"estudiantes": estudiantes}, status=200)


class EstudiantesPorMateriaCursoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, asignacion_id):
        user = request.user

        # Verifica que el usuario es docente
        if not user.rol or user.rol.nombre.lower() != "docente":
            return Response({"error": "Acceso restringido a docentes."}, status=403)

        # Verifica que la asignación le pertenece
        try:
            asignacion = Asignacion.objects.select_related('curso', 'gestion').get(id=asignacion_id, docente=user)
        except Asignacion.DoesNotExist:
            return Response({"error": "Asignación no válida o no pertenece al docente."}, status=404)

        # Buscar estudiantes inscritos en ese curso y gestión
        inscripciones = Inscripcion.objects.filter(
            curso=asignacion.curso,
            gestion=asignacion.gestion
        ).select_related('estudiante')

        estudiantes = []
        for inscripcion in inscripciones:
            estudiante = inscripcion.estudiante
            estudiantes.append({
                "inscripcion_id": inscripcion.id,
                "estudiante_id": estudiante.id,
                "nombre": estudiante.nombre,
                "ci": estudiante.ci,
                "email": estudiante.email
            })

        return Response({
            "curso": asignacion.curso.nombre,
            "materia": asignacion.materia.nombre,
            "gestion": asignacion.gestion.nombre,
            "estudiantes": estudiantes
        }, status=200)


class EvaluacionesPorAsignacionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, asignacion_id):
        user = request.user

        if not user.rol or user.rol.nombre.lower() != "docente":
            return Response({"error": "Acceso restringido a docentes."}, status=403)

        try:
            asignacion = Asignacion.objects.get(id=asignacion_id, docente=user)
        except Asignacion.DoesNotExist:
            return Response({"error": "Asignación no válida o no pertenece al docente."}, status=404)

        evaluaciones = Evaluacion.objects.filter(asignacion=asignacion)

        data = []
        for evaluacion in evaluaciones:
            data.append({
                "id": evaluacion.id,
                "nombre": evaluacion.nombre,
                "tipo": evaluacion.tipo,
                "fecha": evaluacion.fecha,
                "valor": evaluacion.valor
            })

        return Response({"evaluaciones": data}, status=200)


class EstudiantesPorAsignacionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, asignacion_id):
        user = request.user

        # Validar que sea docente
        if not user.rol or user.rol.nombre.lower() != "docente":
            return Response({"error": "Acceso restringido a docentes."}, status=403)

        try:
            asignacion = Asignacion.objects.select_related('curso', 'gestion').get(id=asignacion_id, docente=user)
        except Asignacion.DoesNotExist:
            return Response({"error": "Asignación no válida o no pertenece al docente."}, status=404)

        inscripciones = Inscripcion.objects.filter(
            curso=asignacion.curso,
            gestion=asignacion.gestion
        ).select_related("estudiante")

        estudiantes = []
        for inscripcion in inscripciones:
            estudiante = inscripcion.estudiante
            estudiantes.append({
                "inscripcion_id": inscripcion.id,
                "estudiante_id": estudiante.id,
                "nombre": estudiante.nombre,
                "ci": estudiante.ci,
                "email": estudiante.email
            })

        return Response({
            "curso": asignacion.curso.nombre,
            "materia": asignacion.materia.nombre,
            "gestion": asignacion.gestion.nombre,
            "estudiantes": estudiantes
        }, status=200)


class EvaluacionesPorAsignacionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, asignacion_id):
        user = request.user

        # Verificar que sea docente
        if not user.rol or user.rol.nombre.lower() != "docente":
            return Response({"error": "Acceso restringido a docentes."}, status=403)

        try:
            asignacion = Asignacion.objects.get(id=asignacion_id, docente=user)
        except Asignacion.DoesNotExist:
            return Response({"error": "Asignación no válida o no pertenece al docente."}, status=404)

        evaluaciones = Evaluacion.objects.filter(asignacion=asignacion)

        data = []
        for ev in evaluaciones:
            data.append({
                "evaluacion_id": ev.id,
                "nombre": ev.nombre,
                "tipo": ev.tipo,
                "fecha": ev.fecha,
                "valor": ev.valor,
                "periodo": ev.periodo.nombre
            })

        return Response({
            "materia": asignacion.materia.nombre,
            "curso": asignacion.curso.nombre,
            "gestion": asignacion.gestion.nombre,
            "evaluaciones": data
        }, status=200)

class EstudiantesPorAsignacionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, asignacion_id):
        user = request.user

        # Validar que sea docente
        if not user.rol or user.rol.nombre.lower() != "docente":
            return Response({"error": "Acceso restringido a docentes."}, status=403)

        try:
            asignacion = Asignacion.objects.select_related('curso', 'gestion').get(id=asignacion_id, docente=user)
        except Asignacion.DoesNotExist:
            return Response({"error": "Asignación no válida o no pertenece al docente."}, status=404)

        inscripciones = Inscripcion.objects.filter(
            curso=asignacion.curso,
            gestion=asignacion.gestion
        ).select_related("estudiante")

        estudiantes = []
        for inscripcion in inscripciones:
            estudiante = inscripcion.estudiante
            estudiantes.append({
                "inscripcion_id": inscripcion.id,
                "estudiante_id": estudiante.id,
                "nombre": estudiante.nombre,
                "ci": estudiante.ci,
                "email": estudiante.email
            })

        return Response({
            "materia": asignacion.materia.nombre,
            "curso": asignacion.curso.nombre,
            "gestion": asignacion.gestion.nombre,
            "estudiantes": estudiantes
        }, status=200)


class RegistrarNotasEvaluacionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RegistrarNotasSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        resultados = serializer.save()
        return Response({
            "mensaje": "Notas procesadas correctamente.",
            "resultados": resultados
        })
        
class CerrarEvaluacionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, evaluacion_id):
        try:
            evaluacion = Evaluacion.objects.get(id=evaluacion_id)
            evaluacion.cerrado = True
            evaluacion.save()
            return Response({"mensaje": "Evaluación cerrada exitosamente."}, status=200)
        except Evaluacion.DoesNotExist:
            return Response({"error": "Evaluación no encontrada."}, status=404)
        
        
class VerNotasMateriaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, materia_id):
        estudiante = request.user

        # Obtener inscripciones del estudiante
        inscripciones = Inscripcion.objects.filter(estudiante=estudiante)

        # Buscar asignaciones donde esa materia está ligada al curso y gestión del estudiante
        resultados = []

        for inscripcion in inscripciones:
            asignaciones = Asignacion.objects.filter(
                materia_id=materia_id,
                curso=inscripcion.curso,
                gestion=inscripcion.gestion
            )

            for asignacion in asignaciones:
                evaluaciones = Evaluacion.objects.filter(asignacion=asignacion)
                lista_notas = []

                for evaluacion in evaluaciones:
                    nota = Nota.objects.filter(
                        inscripcion=inscripcion,
                        evaluacion=evaluacion
                    ).first()

                    lista_notas.append({
                        "nombre": evaluacion.nombre,
                        "tipo": evaluacion.tipo,
                        "fecha": evaluacion.fecha,
                        "valor": evaluacion.valor,
                        "nota": nota.nota if nota else None
                    })

                resultados.append({
                    "materia": asignacion.materia.nombre,
                    "curso": inscripcion.curso.nombre,
                    "gestion": inscripcion.gestion.nombre,
                    "evaluaciones": lista_notas
                })

        return Response({"resultados": resultados})
    

class MateriasEstudianteView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        estudiante = request.user

        materias_info = []

        inscripciones = Inscripcion.objects.filter(estudiante=estudiante)

        for inscripcion in inscripciones:
            asignaciones = Asignacion.objects.filter(
                curso=inscripcion.curso,
                gestion=inscripcion.gestion
            ).select_related('materia')

            for asignacion in asignaciones:
                materias_info.append({
                    "id": asignacion.materia.id,              # 👈 ahora será `id` en vez de `materia_id`
                    "nombre": asignacion.materia.nombre,      # 👈 y `nombre` en vez de `materia`
                    "curso": inscripcion.curso.nombre,
                    "gestion": inscripcion.gestion.nombre
                })
        return Response({ "materias": materias_info })