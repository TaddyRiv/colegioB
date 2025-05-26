from rest_framework import serializers
from .models import User, Rol
from django.utils.crypto import get_random_string

class EstudianteRegisterSerializer(serializers.ModelSerializer):
    tutor_ci = serializers.IntegerField(write_only=True, required=False)  # buscar tutor existente
    crear_tutor = serializers.BooleanField(write_only=True, default=False)
    nombre_tutor = serializers.CharField(write_only=True, required=False)
    celular_tutor = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['nombre', 'ci', 'email', 'celular', 'tutor_ci', 'crear_tutor', 'nombre_tutor', 'celular_tutor']

    def create(self, validated_data):
        rol_estudiante = Rol.objects.get(nombre='estudiante')
        rol_tutor = Rol.objects.get(nombre='tutor')

        ci = validated_data['ci']
        email = validated_data['email']
        nombre = validated_data['nombre']
        celular = validated_data['celular']

        # Generar username tipo EST_<CODIGO>
        username = f"EST_{get_random_string(length=6).upper()}"

        tutor = None

        # Si se crea uno nuevo
        if validated_data.get('crear_tutor'):
            ci_tutor = validated_data['tutor_ci']
            nombre_tutor = validated_data.get('nombre_tutor', 'Tutor de ' + nombre)
            celular_tutor = validated_data.get('celular_tutor', '')

            tutor = User.objects.create(
                ci=ci_tutor,
                nombre=nombre_tutor,
                celular=celular_tutor,
                email=f"tutor{ci_tutor}@example.com",
                rol=rol_tutor,
            )
            tutor.set_password(str(ci_tutor))
            tutor.save()
            tutor.username = f"tutor_{tutor.id}"
            tutor.save()

        elif validated_data.get('tutor_ci'):
            tutor = User.objects.filter(ci=validated_data['tutor_ci'], rol=rol_tutor).first()
            if not tutor:
                raise serializers.ValidationError("No se encontró un tutor con ese CI.")

        else:
            raise serializers.ValidationError("Debes seleccionar un tutor existente o crear uno nuevo.")

        estudiante = User(
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
        return docente