from rest_framework import serializers
from .models import Categoria, Producto, Garantia

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'
        read_only_fields = ['id']


class GarantiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Garantia
        fields = '__all__'
        read_only_fields = ['id']


class ProductoSerializer(serializers.ModelSerializer):
    """
    Serializer para Producto.
    """

    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    garantias = GarantiaSerializer(many=True, read_only=True)

    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'descripcion', 'marca', 'modelo', 'precio', 'stock',
            'imagen_url', 'estado', 'fecha_registro',
            'categoria', 
            'categoria_nombre',
            'garantias' 
        ]
        read_only_fields = ['id', 'fecha_registro']