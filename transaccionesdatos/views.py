from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiResponse
from datetime import datetime

from .models import Cliente, Habitacion, Reserva
from .serializers import ClienteSerializer, HabitacionSerializer, ReservaSerializer


class ClienteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ClienteSerializer
    queryset = Cliente.objects.all()


class HabitacionViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = HabitacionSerializer

    def get_queryset(self):
        return Habitacion.objects.all()

    @extend_schema(
        summary="Listar habitaciones disponibles",
        description="Obtiene todas las habitaciones disponibles en un rango de fechas",
        responses={200: OpenApiResponse(description="Lista de habitaciones disponibles")}
    )
    @action(detail=False, methods=['get'])
    def disponibles(self, request):
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')

        if not fecha_inicio or not fecha_fin:
            return Response(
                {"error": "Debes proporcionar fecha_inicio y fecha_fin"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {"error": "Formato de fecha inválido. Usa YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )

        habitaciones = Habitacion.habitaciones_disponibles(fecha_inicio, fecha_fin)
        serializer = self.get_serializer(habitaciones, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def ocupar(self, request, pk=None):
        """Cambiar estado de la habitación a ocupada"""
        habitacion = self.get_object()
        if habitacion.estado != 'reservada':
            return Response(
                {"error": "Solo se puede ocupar una habitación reservada"},
                status=status.HTTP_400_BAD_REQUEST
            )
        habitacion.ocupar()
        return Response({
            "mensaje": f"Habitación {habitacion.numero} ocupada",
            "estado": habitacion.get_estado_display()
        })

    @action(detail=True, methods=['post'])
    def liberar(self, request, pk=None):
        """Cambiar estado de la habitación a disponible"""
        habitacion = self.get_object()
        if habitacion.estado not in ['reservada', 'ocupada']:
            return Response(
                {"error": "Solo se puede liberar una habitación reservada u ocupada"},
                status=status.HTTP_400_BAD_REQUEST
            )
        habitacion.liberar()
        return Response({
            "mensaje": f"Habitación {habitacion.numero} liberada",
            "estado": habitacion.get_estado_display()
        })

    @action(detail=True, methods=['post'])
    def mantenimiento(self, request, pk=None):
        """Cambiar estado de la habitación a mantenimiento"""
        habitacion = self.get_object()
        habitacion.poner_mantenimiento()
        return Response({
            "mensaje": f"Habitación {habitacion.numero} en mantenimiento",
            "estado": habitacion.get_estado_display()
        })


class ReservaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ReservaSerializer

    def get_queryset(self):
        """Filtrar transaccionesdatos por usuario logueado"""
        return Reserva.objects.filter(usuario=self.request.user)

    @extend_schema(
        summary="Crear una reserva",
        description="Crea una nueva reserva. La habitación debe estar disponible en las fechas seleccionadas.",
        request=ReservaSerializer,
        responses={
            201: OpenApiResponse(description="Reserva creada exitosamente"),
            400: OpenApiResponse(description="Datos inválidos o habitación no disponible"),
            401: OpenApiResponse(description="No autenticado"),
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            habitacion = serializer.validated_data.get('habitacion')
            fecha_inicio = serializer.validated_data.get('fecha_inicio')
            fecha_fin = serializer.validated_data.get('fecha_fin')

            if not habitacion.esta_disponible_para_reservar(fecha_inicio, fecha_fin):
                return Response(
                    {"error": "La habitación no está disponible en las fechas seleccionadas"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # ✅ EL USUARIO LOGUEADO SE ASIGNA AUTOMÁTICAMENTE
            reserva = serializer.save(usuario=request.user)
            habitacion.reservar()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Cancelar una reserva",
        description="Cambia el estado de una reserva a 'cancelada'",
        responses={
            200: OpenApiResponse(description="Reserva cancelada"),
            404: OpenApiResponse(description="Reserva no encontrada"),
            401: OpenApiResponse(description="No autenticado"),
            403: OpenApiResponse(description="No tienes permiso"),
        }
    )
    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        reserva = self.get_object()

        if reserva.usuario != request.user:
            return Response(
                {"error": "No tienes permiso para cancelar esta reserva"},
                status=status.HTTP_403_FORBIDDEN
            )

        reserva.estado = 'cancelada'
        reserva.save()

        if reserva.habitacion:
            reserva.habitacion.actualizar_estado()

        return Response({
            "mensaje": "Reserva cancelada exitosamente",
            "reserva": self.get_serializer(reserva).data
        })

    @action(detail=False, methods=['get'])
    def historial(self, request):
        """Obtener historial de transaccionesdatos del usuario logueado"""
        reservas = self.get_queryset().order_by('-created_at')
        serializer = self.get_serializer(reservas, many=True)
        return Response(serializer.data)