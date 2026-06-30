"""
URL configuration for jwtlogin project.
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from .views import home_page, dashboard_page, login_view, logout_view, HomePageAPI
from datagraf.views import (
    ReporteEmpleadosView,
    ReporteEmpleadosCSVToJSON,
    GraficaSueldosEmpleados,
    ExperienciaSalarioView,
    DashboardGraficosView,
)
from transaccionesdatos import views as transacciones_views

urlpatterns = [
    path("", home_page, name="home"),
    path("dashboard/", dashboard_page, name="dashboard"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/home/', HomePageAPI.as_view(), name='api_home'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # TRANSACCIONESDATOS
    path('api/transaccionesdatos/clientes/',
         transacciones_views.ClienteViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='cliente-list'),
    path('api/transaccionesdatos/clientes/<int:pk>/',
         transacciones_views.ClienteViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}),
         name='cliente-detail'),
    path('api/transaccionesdatos/habitaciones/',
         transacciones_views.HabitacionViewSet.as_view({'get': 'list'}),
         name='habitacion-list'),
    path('api/transaccionesdatos/habitaciones/<int:pk>/',
         transacciones_views.HabitacionViewSet.as_view({'get': 'retrieve'}),
         name='habitacion-detail'),
    path('api/transaccionesdatos/habitaciones/disponibles/',
         transacciones_views.HabitacionViewSet.as_view({'get': 'disponibles'}),
         name='habitacion-disponibles'),
    path('api/transaccionesdatos/habitaciones/<int:pk>/ocupar/',
         transacciones_views.HabitacionViewSet.as_view({'post': 'ocupar'}),
         name='habitacion-ocupar'),
    path('api/transaccionesdatos/habitaciones/<int:pk>/liberar/',
         transacciones_views.HabitacionViewSet.as_view({'post': 'liberar'}),
         name='habitacion-liberar'),
    path('api/transaccionesdatos/habitaciones/<int:pk>/mantenimiento/',
         transacciones_views.HabitacionViewSet.as_view({'post': 'mantenimiento'}),
         name='habitacion-mantenimiento'),
    path('api/transaccionesdatos/transaccionesdatos/',
         transacciones_views.ReservaViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='reserva-list'),
    path('api/transaccionesdatos/transaccionesdatos/<int:pk>/',
         transacciones_views.ReservaViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}),
         name='reserva-detail'),
    path('api/transaccionesdatos/transaccionesdatos/<int:pk>/cancelar/',
         transacciones_views.ReservaViewSet.as_view({'post': 'cancelar'}),
         name='reserva-cancelar'),
    path('api/transaccionesdatos/transaccionesdatos/historial/',
         transacciones_views.ReservaViewSet.as_view({'get': 'historial'}),
         name='reserva-historial'),

    # EMPLEADOS
    path("reporte-empleados/", ReporteEmpleadosView.as_view(), name="reporte_pandas"),
    path("list-empleados/", ReporteEmpleadosCSVToJSON.as_view(), name="list_empleados"),
    path("grafica-sueldos/", GraficaSueldosEmpleados.as_view(), name="grafica_sueldos"),
    path("experiencia-salario/", ExperienciaSalarioView.as_view(), name="experiencia_salario"),

    path("dashboard-graficos/", DashboardGraficosView.as_view(), name="dashboard_graficos"),
]