from rest_framework import serializers
from .models import User, Rol

class TutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'nombre', 'ci', 'celular']

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    rol = serializers.PrimaryKeyRelatedField(queryset=Rol.objects.all())
    tutor = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(rol__nombre='tutor'),
        required=False,
        allow_null=True
    )

    ci = serializers.IntegerField(min_value=1, required=True)
  

    class Meta:
        model = User
        fields = ['username', 'password', 'ci', 'nombre', 'celular', 'rol', 'tutor']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
