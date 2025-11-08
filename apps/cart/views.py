from rest_framework.viewsets import ReadOnlyModelViewSet 
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from django.db import transaction

from .models import Carrito, DetalleCarrito
from .serializers import ( 
    CarritoSerializer, 
    AddItemSerializer, 
    UpdateItemSerializer
)
from apps.customers.models import Cliente

class CarritoViewSet(ReadOnlyModelViewSet): 
    """
    ViewSet para el Carrito.
    """
    serializer_class = CarritoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        qs = Carrito.objects.select_related('cliente__user').prefetch_related('detalles__producto')
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return qs.order_by('-id')
        try:
            cliente = user.cliente
        except Cliente.DoesNotExist:
            return Carrito.objects.none()
        return qs.filter(cliente=cliente).order_by('-id')

    @action(detail=False, methods=['get'], url_path='mi-activo')
    def mi_activo(self, request):
        user = request.user
        try:
            cliente = user.cliente
        except Cliente.DoesNotExist:
            return Response({"detail": "Este usuario no tiene perfil de cliente."}, status=400)
        carrito, _ = Carrito.objects.get_or_create(cliente=cliente, estado='activo')
        data = CarritoSerializer(carrito).data
        return Response(data)

    @action(detail=False, methods=['post'], url_path='add-item')
    @transaction.atomic
    def add_item(self, request):
        """Agrega o incrementa un producto en el carrito activo del usuario."""
        
        # Usamos el serializer que SÍ valida stock
        s = AddItemSerializer(data=request.data) 
        
        s.is_valid(raise_exception=True)
        producto = s.validated_data['producto']
        cantidad = s.validated_data['cantidad']
        
        # ... (El resto de tu lógica de add_item es perfecta y se queda igual) ...
        user = request.user
        try:
            cliente = user.cliente
        except Cliente.DoesNotExist:
            return Response({"detail": "Este usuario no tiene perfil de cliente."}, status=400)
        carrito, _ = Carrito.objects.get_or_create(cliente=cliente, estado='activo')
        detalle, created = DetalleCarrito.objects.select_for_update().get_or_create(
            carrito=carrito, producto=producto,
            defaults={'cantidad': 0, 'precio_unitario': producto.precio}
        )
        detalle.cantidad += cantidad
        detalle.precio_unitario = producto.precio
        detalle.save()
        return Response(CarritoSerializer(carrito).data, status=status.HTTP_200_OK)


    @action(detail=False, methods=['post'], url_path='remove-item')
    @transaction.atomic
    def remove_item(self, request):
        """Decrementa o elimina un producto del carrito activo."""
        
        # --- MEJORA: Usamos el nuevo serializer que NO valida stock ---
        s = UpdateItemSerializer(data=request.data)
        
        s.is_valid(raise_exception=True)
        producto = s.validated_data['producto']
        cantidad = s.validated_data['cantidad']

        # ... (El resto de tu lógica de remove_item es perfecta y se queda igual) ...
        user = request.user
        try:
            cliente = user.cliente
        except Cliente.DoesNotExist:
            return Response({"detail": "Este usuario no tiene perfil de cliente."}, status=400)
        try:
            carrito = Carrito.objects.get(cliente=cliente, estado='activo')
            detalle = DetalleCarrito.objects.select_for_update().get(carrito=carrito, producto=producto)
        except (Carrito.DoesNotExist, DetalleCarrito.DoesNotExist):
            return Response({"detail": "El producto no está en el carrito."}, status=400)

        nueva = detalle.cantidad - cantidad
        if nueva <= 0:
            detalle.delete()
        else:
            detalle.cantidad = nueva
            detalle.save()
        return Response(CarritoSerializer(carrito).data)

    @action(detail=False, methods=['post'], url_path='clear')
    def clear(self, request):
        user = request.user
        try:
            cliente = user.cliente
            carrito = Carrito.objects.get(cliente=cliente, estado='activo')
        except (Cliente.DoesNotExist, Carrito.DoesNotExist):
            return Response({"detail": "No hay carrito activo."}, status=400)
        carrito.detalles.all().delete()
        return Response(CarritoSerializer(carrito).data)