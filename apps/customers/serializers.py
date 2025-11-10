from rest_framework import serializers
from django.conf import settings
from .models import Cliente

class ClienteSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    nombre_completo = serializers.SerializerMethodField()

    class Meta:
        model = Cliente
        fields = [
            'id', 'user', 'username', 'email', 'nombre_completo', 
            'ci_nit', 'telefono', 'direccion', 'ciudad', 'fecha_registro'
        ]
        read_only_fields = ['id', 'fecha_registro', 'user']

    def get_nombre_completo(self, obj):
        full_name = obj.user.get_full_name()
        return full_name or obj.user.username