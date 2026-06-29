import os
import io
import base64
import pandas as pd
import matplotlib.pyplot as plt
from django.conf import settings
from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema


class ReporteEmpleadosView(View):
    template_name = "reportes/empleados.html"

    @extend_schema(
        summary="Reporte de empleados en HTML",
        description="Muestra un reporte de empleados en formato HTML con tabla de datos",
        tags=["Empleados"],
    )
    def get(self, request, *args, **kwargs):
        ruta_csv = os.path.join(settings.BASE_DIR, "data/reportes/excel/empleados.csv")
        df = pd.read_csv(ruta_csv, sep=";")
        tabla_html = df.to_html(
            classes="table table-striped table-hover table-bordered",
            index=False,
            justify="left",
        )
        return render(request, self.template_name, {"tabla_reporte": tabla_html})


class ReporteEmpleadosCSVToJSON(APIView):
    """
    Endpoint que convierte CSV a JSON y lo retorna como respuesta
    """

    @extend_schema(
        summary="Lista de empleados en JSON",
        description="Convierte el archivo CSV de empleados a JSON y lo retorna como respuesta",
        tags=["Empleados"],
    )
    def get(self, request, *args, **kwargs):
        ruta_csv = os.path.join(settings.BASE_DIR, "data/reportes/excel/empleados.csv")
        ruta_json = os.path.join(settings.BASE_DIR, "data/reportes/json/empleados.json")
        df = pd.read_csv(ruta_csv, sep=";")
        data = df.to_json(orient='records', lines=False) # USA PARA MOSTRAR EN ENDPOINT
        almacenaJson = df.to_json(ruta_json, orient='records', lines=False) # LO GUARDA COMO data/reportes/json/empleados.json
        return JsonResponse(
            data,
            safe=False,
            json_dumps_params={'ensure_ascii': False}
        )


class GraficaSueldosEmpleados(APIView):
    """
    Vista que genera gráficos de sueldos de empleados
    """

    @extend_schema(
        summary="Gráfico de sueldos de empleados",
        description="Genera un gráfico de líneas con los sueldos promedio por departamento",
        tags=["Reporte Grafico"],
    )
    def get(self, request, *args, **kwargs):

        template_grafica = "reportes/grafico_empleados.html"
        # ==========================================
        # 1. CONSTRUIR LA RUTA DEL ARCHIVO CSV
        # ==========================================
        ruta_csv = os.path.join(settings.BASE_DIR, "data/reportes/excel/empleados.csv")

        # ==========================================
        # 2. LEER EL ARCHIVO CSV CON PANDAS
        # ==========================================
        df = pd.read_csv(ruta_csv, sep=";")

        # ==========================================
        # 3. PROCESAR DATOS: CALCULAR PROMEDIO POR DEPARTAMENTO
        # ==========================================
        df_resumen = df.groupby('Departamento')['Salario'].mean().round(2).sort_values(ascending=False)

        # ==========================================
        # GRÁFICO DE LÍNEAS
        # ==========================================
        plt.figure(figsize=(12, 6))

        # Crear el gráfico de líneas
        plt.plot(df_resumen.index, df_resumen.values,
                 marker='o',  # Marcador circular
                 linestyle='-',  # Línea continua
                 linewidth=3,  # Grosor de la línea
                 markersize=10,  # Tamaño del marcador
                 color='#2E86AB',  # Color de la línea
                 markerfacecolor='#A23B72',  # Color del marcador
                 markeredgecolor='black',  # Borde del marcador
                 markeredgewidth=1.5)  # Grosor del borde

        # Personalizar el gráfico
        plt.title('📈 Sueldos Promedio por Departamento', fontsize=16, fontweight='bold')
        plt.xlabel('Departamento', fontsize=12)
        plt.ylabel('Sueldo Promedio ($)', fontsize=12)
        plt.xticks(rotation=45, ha='right', fontsize=11)
        plt.grid(axis='both', linestyle='--', alpha=0.6)

        # Agregar valores encima de cada punto
        for i, v in enumerate(df_resumen.values):
            plt.text(i, v + 80, f'${v:,.0f}',
                     ha='center', va='bottom',
                     fontsize=10, fontweight='bold',
                     bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='gray', alpha=0.7))

        plt.tight_layout()

        # ==========================================
        # 5. GUARDAR EL GRÁFICO EN DISCO
        # ==========================================
        # Crear la carpeta si no existe
        graficos_dir = os.path.join(settings.BASE_DIR, "data/reportes/graficos")
        os.makedirs(graficos_dir, exist_ok=True)

        # Nombre del archivo con timestamp
        from datetime import datetime
        # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # nombre_archivo = f"sueldos_por_departamento_{timestamp}.png"
        nombre_archivo = f"sueldos_por_departamento.png"
        ruta_guardado = os.path.join(graficos_dir, nombre_archivo)

        # Guardar el gráfico en el archivo
        plt.savefig(ruta_guardado, format='png', dpi=100)

        # ==========================================
        # 6. CONVERTIR EL GRÁFICO A FORMATO BASE64
        # ==========================================
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100)
        buffer.seek(0)
        grafico_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()

        # ==========================================
        # 7. CREAR ESTADÍSTICAS ADICIONALES
        # ==========================================
        stats = {
            'total_empleados': len(df),
            'salario_promedio': round(df['Salario'].mean(), 2),
            'salario_maximo': df['Salario'].max(),
            'salario_minimo': df['Salario'].min(),
            'edad_promedio': round(df['Edad'].mean(), 1),
            'departamentos': df['Departamento'].nunique(),
            'total_departamentos': df.groupby('Departamento').size().to_dict(),
            'sueldo_max_departamento': df_resumen.idxmax(),
            'sueldo_min_departamento': df_resumen.idxmin(),
            'ruta_grafico': ruta_guardado,  # Ruta donde se guardó el archivo
            'nombre_grafico': nombre_archivo,  # Nombre del archivo
        }

        # ==========================================
        # 8. RESPUESTA SEGÚN TIPO DE PETICIÓN
        # ==========================================
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'grafico': grafico_base64,
                'stats': stats,
                'datos': df.to_dict(orient='records')
            }, safe=False)

        context = {
            'grafico': grafico_base64,
            'stats': stats,
        }
        return render(request, template_grafica, context)