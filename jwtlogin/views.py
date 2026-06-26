from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse


# HOME PAGE (SIN AUTENTICACIÓN)
def home_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')


# DASHBOARD (REQUIERE AUTENTICACIÓN)
@login_required(login_url='/')
def dashboard_page(request):
    # OBTENER TOKENS PARA EL USUARIO AUTENTICADO
    refresh = RefreshToken.for_user(request.user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)

    return render(request, 'dashboard.html', {
        'access_token': access_token,
        'refresh_token': refresh_token,
    })


# LOGIN
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'home.html', {'error': 'Usuario o contraseña incorrectos'})
    return redirect('/')


# LOGOUT
def logout_view(request):
    logout(request)
    return redirect('/')


# API DE PRUEBA
class HomePageAPI(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Página de inicio API",
        description="Endpoint de prueba que requiere autenticación JWT",
        responses={
            200: OpenApiResponse(description="Bienvenido"),
            401: OpenApiResponse(description="No autenticado"),
        }
    )
    def get(self, request):
        return Response({
            "mensaje": "Bienvenido a la API con JWT",
            "usuario": str(request.user)
        })