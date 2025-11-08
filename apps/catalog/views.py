from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import DjangoModelPermissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters  
from .models import Categoria, Producto, Garantia
from .serializers import CategoriaSerializer, ProductoSerializer, GarantiaSerializer

class CategoriaViewSet(ModelViewSet):
    """
    CRUD para Categorías.
    """
    queryset = Categoria.objects.prefetch_related('productos').all().order_by('nombre')
    serializer_class = CategoriaSerializer
    permission_classes = [DjangoModelPermissions]
    search_fields = ['nombre']


class ProductoViewSet(ModelViewSet):
    """
    CRUD para Productos.
    """
    
    # --- OPTIMIZACIÓN ---
    queryset = Producto.objects.select_related('categoria') \
                               .prefetch_related('garantias') \
                               .all().order_by('-id')
                               
    serializer_class = ProductoSerializer
    permission_classes = [DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['categoria', 'estado', 'marca']
    search_fields = ['nombre', 'descripcion', 'marca', 'modelo']


class GarantiaViewSet(ModelViewSet):
    """
    CRUD para Garantías.
    """
    queryset = Garantia.objects.select_related('producto').all()
    serializer_class = GarantiaSerializer
    permission_classes = [DjangoModelPermissions]
    filterset_fields = ['producto', 'tipo_garantia', 'estado'] 