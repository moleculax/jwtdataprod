from django.urls import path
from . import views

app_name = 'transaccionesdatos'

urlpatterns = [
    # Clientes
    path('clientes/', views.ClienteViewSet.as_view({'get': 'list', 'post': 'create'}), name='cliente-list'),
    path('clientes/<int:pk>/', views.ClienteViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}),
         name='cliente-detail'),

    # Habitaciones
    path('habitaciones/', views.HabitacionViewSet.as_view({'get': 'list'}), name='habitacion-list'),
    path('habitaciones/<int:pk>/', views.HabitacionViewSet.as_view({'get': 'retrieve'}), name='habitacion-detail'),
    path('habitaciones/disponibles/', views.HabitacionViewSet.as_view({'get': 'disponibles'}),
         name='habitacion-disponibles'),
    path('habitaciones/<int:pk>/ocupar/', views.HabitacionViewSet.as_view({'post': 'ocupar'}),
         name='habitacion-ocupar'),
    path('habitaciones/<int:pk>/liberar/', views.HabitacionViewSet.as_view({'post': 'liberar'}),
         name='habitacion-liberar'),
    path('habitaciones/<int:pk>/mantenimiento/', views.HabitacionViewSet.as_view({'post': 'mantenimiento'}),
         name='habitacion-mantenimiento'),

    # Reservas
    path('transaccionesdatos/', views.ReservaViewSet.as_view({'get': 'list', 'post': 'create'}), name='reserva-list'),
    path('transaccionesdatos/<int:pk>/', views.ReservaViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}),
         name='reserva-detail'),
    path('transaccionesdatos/<int:pk>/cancelar/', views.ReservaViewSet.as_view({'post': 'cancelar'}), name='reserva-cancelar'),
    path('transaccionesdatos/historial/', views.ReservaViewSet.as_view({'get': 'historial'}), name='reserva-historial'),
]