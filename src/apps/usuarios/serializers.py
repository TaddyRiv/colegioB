from rest_framework import serializers
from .models import User, Rol
from django.utils.crypto import get_random_string
from .models import Inscripcion,Curso, Gestion
from apps.usuarios.models import Nota, Evaluacion, Inscripcion, User

class EstudianteRegisterSerializer(serializers.ModelSerializer):
    tutor_ci = serializers.IntegerField(write_only=True, required=False)
    crear_tutor = serializers.BooleanField(write_only=True, default=False)
    nombre_tutor = serializers.CharField(write_only=True, required=False)
    celular_tutor = serializers.CharField(write_only=True, required=False)
    email_tutor = serializers.EmailField(write_only=True, required=False)  # Nuevo campo

    class Meta:
        model = User
        fields = [
            'nombre', 'ci', 'email', 'celular',
            'tutor_ci', 'crear_tutor',
            'nombre_tutor', 'celular_tutor', 'email_tutor'  # Incluir aquí
        ]

    def create(self, validated_data):
        rol_estudiante = Rol.objects.get(nombre='estudiante')
        rol_tutor = Rol.objects.get(nombre='tutor')

        ci = validated_data['ci']
        email = validated_data['email']
        nombre = validated_data['nombre']
        celular = validated_data['celular']

        username = f"EST_{get_random_string(length=6).upper()}"

        tutor = None
        tutor_data = {}

        if validated_data.get('crear_tutor'):
            ci_tutor = validated_data['tutor_ci']
            nombre_tutor = validated_data.get('nombre_tutor', f'Tutor de {nombre}')
            celular_tutor = validated_data.get('celular_tutor', '')
            email_tutor = validated_data.get('email_tutor')

            if not email_tutor:
                raise serializers.ValidationError("Debe proporcionar el email del tutor.")

            tutor = User.objects.create(
                ci=ci_tutor,
                nombre=nombre_tutor,
                celular=celular_tutor,
                email=email_tutor,
                rol=rol_tutor,
            )
            tutor.set_password(str(ci_tutor))
            tutor.save()
            tutor.username = f"tutor_{tutor.id}"
            tutor.save()

            tutor_data = {
                "username": tutor.username,
                "nombre": tutor.nombre,
                "ci": tutor.ci,
                "email": tutor.email,
                "rol": tutor.rol.nombre,
                "contraseña": str(ci_tutor)
            }

        elif validated_data.get('tutor_ci'):
            tutor = User.objects.filter(ci=validated_data['tutor_ci'], rol=rol_tutor).first()
            if not tutor:
                raise serializers.ValidationError("No se encontró un tutor con ese CI.")
            tutor_data = {
                "username": tutor.username,
                "nombre": tutor.nombre,
                "ci": tutor.ci,
                "email": tutor.email,
                "rol": tutor.rol.nombre
            }

        else:
            raise serializers.ValidationError("Debes seleccionar un tutor existente o crear uno nuevo.")

        estudiante = User.objects.create(
            username=username,
            nombre=nombre,
            ci=ci,
            email=email,
            celular=celular,
            rol=rol_estudiante,
            tutor=tutor
        )
        estudiante.set_password(str(ci))
        estudiante.save()

        self.estudiante_info = {
            "mensaje": "Estudiante registrado exitosamente.",
            "estudiante": {
                "username": username,
                "nombre": nombre,
                "email": email,
                "rol": rol_estudiante.nombre,
                "contraseña": str(ci)
            },
            "tutor": tutor_data
        }

        return estudiante


class DocenteRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['nombre', 'ci', 'email', 'celular']

    def create(self, validated_data):
        rol_docente = Rol.objects.get(nombre='docente')

        ci = validated_data['ci']
        email = validated_data['email']
        nombre = validated_data['nombre']
        celular = validated_data['celular']
        username = f"DOC_{get_random_string(length=6).upper()}"

        docente = User.objects.create(
            username=username,
            nombre=nombre,
            ci=ci,
            email=email,
            celular=celular,
            rol=rol_docente,
        )
        docente.set_password(str(ci))
        docente.save()

        self.docente_info = {
            "mensaje": "Docente registrado exitosamente.",
            "docente": {
                "id": docente.id,
                "username": docente.username,
                "nombre": docente.nombre,
                "email": docente.email,
                "rol": rol_docente.nombre,
                "contraseña": str(ci)
            }
        }

        return docente

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'nombre', 'email', 'ci', 'rol']


class InscripcionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inscripcion
        fields = ['estudiante', 'curso', 'gestion']

    def validate(self, data):
        # Evitar duplicados: un estudiante no puede inscribirse dos veces a la misma gestión
        if Inscripcion.objects.filter(
            estudiante=data['estudiante'],
            gestion=data['gestion']
        ).exists():
            raise serializers.ValidationError("El estudiante ya está inscrito en esta gestión.")
        return data
    
    
from rest_framework import serializers
from .models import Materia

class MateriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Materia
        fields = ['id', 'nombre']  # Puedes incluir más campos si lo necesitas
    

#######################################       
       
       
class EstudianteSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'nombre', 'email', 'ci']
        
class CursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curso
        fields = ['id', 'nombre', 'nivel']

class GestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gestion
        fields = ['id', 'nombre', 'estado']

class TutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'nombre', 'ci', 'email', 'celular']
        


class NotaEstudianteSerializer(serializers.Serializer):
    estudiante_id = serializers.IntegerField()
    nota = serializers.FloatField(min_value=0, max_value=100)  # <-- Agrega max_value=100


class RegistrarNotasSerializer(serializers.Serializer):
    evaluacion_id = serializers.IntegerField()
    notas = NotaEstudianteSerializer(many=True)

    def validate(self, data):
        try:
            evaluacion = Evaluacion.objects.get(id=data['evaluacion_id'])
            if evaluacion.cerrado:
                raise serializers.ValidationError("Esta evaluación ya está cerrada y no permite subir más notas.")
        except Evaluacion.DoesNotExist:
            raise serializers.ValidationError("Evaluación no encontrada.")
        return data

    def create(self, validated_data):
        try:
            evaluacion = Evaluacion.objects.get(id=validated_data['evaluacion_id'])
            if evaluacion.cerrado:
                raise serializers.ValidationError("Esta evaluación ya está cerrada y no se pueden subir más notas.")
        except Evaluacion.DoesNotExist:
            raise serializers.ValidationError("Evaluación no encontrada.")

        gestion = evaluacion.asignacion.gestion
        curso = evaluacion.asignacion.curso

        resultados = []
        errores = False

        for nota_data in validated_data['notas']:
            estudiante_id = nota_data['estudiante_id']
            nota_valor = nota_data['nota']

            try:
                estudiante = User.objects.get(id=estudiante_id)
                inscripcion = Inscripcion.objects.get(
                    estudiante=estudiante,
                    curso=curso,
                    gestion=gestion
                )

                nota_obj, created = Nota.objects.update_or_create(
                    inscripcion=inscripcion,
                    evaluacion=evaluacion,
                    defaults={"nota": nota_valor}
                )

                resultados.append({
                    "estudiante": estudiante.nombre,
                    "nota": nota_valor,
                    "estado": "creado" if created else "actualizado"
                })

            except (User.DoesNotExist, Inscripcion.DoesNotExist):
                errores = True
                resultados.append({
                    "estudiante_id": estudiante_id,
                    "error": "No se encontró inscripción válida"
                })

        # ✅ Solo cerramos la evaluación si NO hubo errores
        if not errores:
            evaluacion.cerrado = True
            evaluacion.save()

        return resultados
