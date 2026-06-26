"""
URL configuration for jwtlogin project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include  # ← CORREGIDO: SE AGREGÓ EL IMPORT DE include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView  #  AGREGADO
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView  # AGREGADO
from .views import home_page, dashboard_page, login_view, logout_view, HomePageAPI


urlpatterns = [
    # HOME
    path("", home_page, name="home"),  # AGREGADO
path("dashboard/", dashboard_page, name="dashboard"),
    # LOGIN / LOGOUT
    path("login/", login_view, name="login"),  # AGREGADO
    path("logout/", logout_view, name="logout"),  # ← AGREGADO

    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),  # ← AGREGADO
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # ← AGREGADO
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # ← AGREGADO
    path('api/home/', HomePageAPI.as_view(), name='api_home'),  # ← AGREGADO

    # SWAGGER (DRF-SPECTACULAR) ============================================================================
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),  # ← AGREGADO
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),  # ← AGREGADO
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),  # ← AGREGADO (OPCIONAL)
    # ======================================================================================================

    path("api/transaccionesdatos/", include("transaccionesdatos.urls")),
]