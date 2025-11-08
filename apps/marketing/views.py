from django.utils import timezone
# --- MEJORA 1: Cambiamos ModelViewSet por ReadOnlyModelViewSet ---
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from .models import Promocion, ProductoPromocion, Notificacion
from .serializers import PromocionSerializer, ProductoPromocionSerializer, NotificacionSerializer
from apps.catalog.models import Producto

# ---- Promociones ----
class PromocionViewSet(ModelViewSet):
    # --- MEJORA DE OPTIMIZACIÓN ---
    queryset = Promocion.objects.prefetch_related('productos_rel__producto')
    serializer_class = PromocionSerializer
    permission_classes = [IsAdminUser]

    # ... (Tu acción 'activas' es perfecta y se queda igual) ...
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], url_path='activas')
    def activas(self, request):
        now = timezone.now()
        qs = self.queryset.filter(estado='activa', fecha_inicio__lte=now, fecha_fin__gte=now)
        data = self.get_serializer(qs, many=True).data
        return Response(data)

# Relación Producto ↔ Promoción
class ProductoPromocionViewSet(ModelViewSet):
    queryset = ProductoPromocion.objects.select_related('producto','promocion').all()
    serializer_class = ProductoPromocionSerializer
    permission_classes = [IsAdminUser]

# ---- Notificaciones ----
# --- MEJORA 1: Cambiado a ReadOnlyModelViewSet ---
class NotificacionViewSet(ReadOnlyModelViewSet):
    """
    Vista de SOLO LECTURA para Notificaciones.
    Los usuarios solo pueden listar y marcar como leídas.
    """
    queryset = Notificacion.objects.select_related('user').all()
    serializer_class = NotificacionSerializer
    permission_classes = [IsAuthenticated]

    # ... (Tu get_queryset es perfecto y se queda igual) ...
    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return self.queryset.order_by('-fecha_envio')
        return (Notificacion.objects.filter(user__isnull=True) | 
                Notificacion.objects.filter(user=user)).order_by('-fecha_envio')

    # ... (Tu 'marcar_leida' es perfecto y se queda igual) ...
    @action(detail=True, methods=['post'], url_path='marcar-leida')
    def marcar_leida(self, request, pk=None):
        noti = self.get_object()
        if noti.user and noti.user != request.user and not request.user.is_staff:
             return Response(status=status.HTTP_403_FORBIDDEN) # Pequeña guarda extra
        noti.leido = True
        noti.save(update_fields=['leido'])
        return Response(self.get_serializer(noti).data)

    # --- MEJORA 2: 'broadcast' usa s.save() ---
    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser], url_path='broadcast')
    def broadcast(self, request):
        """
        Crea una notificación para TODOS (user=None).
        Body: { "titulo": "...", "mensaje": "...", "tipo": "promocion" }
        """
        # Pasamos request.data directamente
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        
        # El serializer sabe que 'user' es opcional (null=True)
        # y s.save() lo creará como None.
        noti = s.save(user=None) 
        
        return Response(self.get_serializer(noti).data, status=status.HTTP_201_CREATED)