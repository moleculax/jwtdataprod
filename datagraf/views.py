import os
import io
import base64
import pandas as pd
import numpy as np
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
        data = df.to_json(orient='records', lines=False)
        # almacenaJson = df.to_json(ruta_json, orient='records', lines=False)  # Esto no funciona así
        return JsonResponse(
            data,
            safe=False,
            json_dumps_params={'ensure_ascii': False}
        )


# ===================================================
# GRAFICO PROMEDIO DE SUELDO POR DEPARTAMENTO
# ===================================================
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
        ruta_csv = os.path.join(settings.BASE_DIR, "data/reportes/excel/empleados.csv")
        df = pd.read_csv(ruta_csv, sep=";")
        df_resumen = df.groupby('Departamento')['Salario'].mean().round(2).sort_values(ascending=False)

        plt.figure(figsize=(12, 6))
        plt.plot(df_resumen.index, df_resumen.values,
                 marker='o', linestyle='-', linewidth=3, markersize=10,
                 color='#2E86AB', markerfacecolor='#A23B72',
                 markeredgecolor='black', markeredgewidth=1.5)

        plt.title('📈 Sueldos Promedio por Departamento', fontsize=16, fontweight='bold')
        plt.xlabel('Departamento', fontsize=12)
        plt.ylabel('Sueldo Promedio ($)', fontsize=12)
        plt.xticks(rotation=45, ha='right', fontsize=11)
        plt.grid(axis='both', linestyle='--', alpha=0.6)

        for i, v in enumerate(df_resumen.values):
            plt.text(i, v + 80, f'${v:,.0f}',
                     ha='center', va='bottom', fontsize=10, fontweight='bold',
                     bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='gray', alpha=0.7))

        plt.tight_layout()

        graficos_dir = os.path.join(settings.BASE_DIR, "data/reportes/graficos")
        os.makedirs(graficos_dir, exist_ok=True)
        nombre_archivo = "sueldos_por_departamento.png"
        ruta_guardado = os.path.join(graficos_dir, nombre_archivo)
        plt.savefig(ruta_guardado, format='png', dpi=100)

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100)
        buffer.seek(0)
        grafico_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()

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
            'ruta_grafico': ruta_guardado,
            'nombre_grafico': nombre_archivo,
        }

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


# ==========================================
# RELACIÓN EXPERIENCIA VS SALARIO
# ==========================================
class ExperienciaSalarioView(APIView):
    """
    Vista que genera un gráfico de dispersión entre experiencia y salario
    """

    @extend_schema(
        summary="Relación experiencia vs salario",
        description="Muestra un gráfico de dispersión con la relación entre años de experiencia y salario",
        tags=["Reporte Grafico"],
    )
    def get(self, request, *args, **kwargs):
        template_grafica = "reportes/experiencia_salario.html"
        ruta_csv = os.path.join(settings.BASE_DIR, "data/reportes/excel/empleados.csv")
        df = pd.read_csv(ruta_csv, sep=";")

        plt.figure(figsize=(12, 7))

        departamentos = df['Departamento'].unique()
        colores = plt.cm.Set3(range(len(departamentos)))

        for i, dept in enumerate(departamentos):
            datos = df[df['Departamento'] == dept]
            plt.scatter(datos['Experiencia'], datos['Salario'],
                        label=dept, color=colores[i], s=80, alpha=0.7, edgecolor='black')

        # Línea de tendencia
        from scipy import stats
        x = df['Experiencia'].dropna()
        y = df['Salario'].dropna()
        if len(x) > 1 and len(y) > 1:
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            linea_tendencia = slope * x + intercept
            plt.plot(x, linea_tendencia, color='red', linestyle='--', linewidth=2, label='Tendencia')

        plt.title('📈 Relación entre Experiencia y Salario', fontsize=16, fontweight='bold')
        plt.xlabel('Años de Experiencia', fontsize=12)
        plt.ylabel('Salario ($)', fontsize=12)
        plt.grid(axis='both', linestyle='--', alpha=0.6)
        plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
        plt.tight_layout()

        graficos_dir = os.path.join(settings.BASE_DIR, "data/reportes/graficos")
        os.makedirs(graficos_dir, exist_ok=True)
        nombre_archivo = "experiencia_salario.png"
        ruta_guardado = os.path.join(graficos_dir, nombre_archivo)
        plt.savefig(ruta_guardado, format='png', dpi=100)

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100)
        buffer.seek(0)
        grafico_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()

        correlacion = df['Experiencia'].corr(df['Salario'])
        stats_datos = {
            'correlacion': round(correlacion, 3) if not pd.isna(correlacion) else 0,
            'total_empleados': len(df),
            'experiencia_promedio': round(df['Experiencia'].mean(), 1),
            'salario_promedio': round(df['Salario'].mean(), 2),
        }

        context = {
            'grafico': grafico_base64,
            'stats': stats_datos,
        }
        return render(request, template_grafica, context)


# ===================================================
# DASHBOARD DE GRÁFICOS (TODAS LAS GRÁFICAS EN UN SOLO HTML)
# ===================================================
class DashboardGraficosView(APIView):
    """
    Vista que genera y muestra todas las gráficas en un solo HTML
    """

    @extend_schema(
        summary="Dashboard de gráficos",
        description="Genera y muestra todas las gráficas de empleados en un solo HTML",
        tags=["Reporte Grafico"],
    )
    def get(self, request, *args, **kwargs):
        template_grafica = "reportes/dashboard_graficos.html"
        ruta_csv = os.path.join(settings.BASE_DIR, "data/reportes/excel/empleados.csv")
        df = pd.read_csv(ruta_csv, sep=";")

        # ==========================================
        # 1. GRÁFICO 1: SUELDOS PROMEDIO POR DEPARTAMENTO (LÍNEAS)
        # ==========================================
        df_resumen = df.groupby('Departamento')['Salario'].mean().round(2).sort_values(ascending=False)

        plt.figure(figsize=(12, 6))
        plt.plot(df_resumen.index, df_resumen.values,
                 marker='o', linestyle='-', linewidth=3, markersize=10,
                 color='#2E86AB', markerfacecolor='#A23B72',
                 markeredgecolor='black', markeredgewidth=1.5)

        plt.title('📈 Sueldos Promedio por Departamento', fontsize=16, fontweight='bold')
        plt.xlabel('Departamento', fontsize=12)
        plt.ylabel('Sueldo Promedio ($)', fontsize=12)
        plt.xticks(rotation=45, ha='right', fontsize=11)
        plt.grid(axis='both', linestyle='--', alpha=0.6)

        for i, v in enumerate(df_resumen.values):
            plt.text(i, v + 80, f'${v:,.0f}',
                     ha='center', va='bottom', fontsize=10, fontweight='bold',
                     bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='gray', alpha=0.7))

        plt.tight_layout()

        graficos_dir = os.path.join(settings.BASE_DIR, "data/reportes/graficos")
        os.makedirs(graficos_dir, exist_ok=True)

        nombre_archivo_1 = "sueldos_por_departamento.png"
        ruta_guardado_1 = os.path.join(graficos_dir, nombre_archivo_1)
        plt.savefig(ruta_guardado_1, format='png', dpi=100)

        buffer1 = io.BytesIO()
        plt.savefig(buffer1, format='png', dpi=100)
        buffer1.seek(0)
        grafico1_base64 = base64.b64encode(buffer1.getvalue()).decode('utf-8')
        plt.close()

        # ==========================================
        # 2. GRÁFICO 2: SALARIO PROMEDIO POR RANGO DE EXPERIENCIA (BARRAS HORIZONTALES)
        # ==========================================
        # Crear rangos de experiencia
        bins = [0, 5, 10, 15, 20, 25, 30]
        labels = ['0-5 años', '6-10 años', '11-15 años', '16-20 años', '21-25 años', '26+ años']
        df['RangoExperiencia'] = pd.cut(df['Experiencia'], bins=bins, labels=labels, right=False)

        # Calcular salario promedio por rango de experiencia
        df_rango = df.groupby('RangoExperiencia')['Salario'].mean().round(2).sort_values(ascending=True)

        plt.figure(figsize=(12, 7))
        colores = plt.cm.Blues(np.linspace(0.4, 0.9, len(df_rango)))
        bars = plt.barh(df_rango.index, df_rango.values, color=colores, edgecolor='black', height=0.6)

        # Agregar valores al final de cada barra
        for bar in bars:
            width = bar.get_width()
            plt.text(width + 50, bar.get_y() + bar.get_height()/2.,
                     f'${width:,.0f}', ha='left', va='center', fontsize=10, fontweight='bold')

        plt.title('📊 Salario Promedio por Rango de Experiencia', fontsize=16, fontweight='bold')
        plt.xlabel('Salario Promedio ($)', fontsize=12)
        plt.ylabel('Rango de Experiencia', fontsize=12)
        plt.grid(axis='x', linestyle='--', alpha=0.6)
        plt.tight_layout()

        # Guardar gráfico 2
        nombre_archivo_2 = "experiencia_salario.png"
        ruta_guardado_2 = os.path.join(graficos_dir, nombre_archivo_2)
        plt.savefig(ruta_guardado_2, format='png', dpi=100)

        buffer2 = io.BytesIO()
        plt.savefig(buffer2, format='png', dpi=100)
        buffer2.seek(0)
        grafico2_base64 = base64.b64encode(buffer2.getvalue()).decode('utf-8')
        plt.close()

        # ==========================================
        # 3. ESTADÍSTICAS GENERALES
        # ==========================================
        correlacion = df['Experiencia'].corr(df['Salario'])
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
            'correlacion': round(correlacion, 3) if not pd.isna(correlacion) else 0,
            'experiencia_promedio': round(df['Experiencia'].mean(), 1),
        }

        # ==========================================
        # 4. CONTEXTO PARA EL TEMPLATE
        # ==========================================
        context = {
            'grafico1': grafico1_base64,
            'grafico2': grafico2_base64,
            'ruta_grafico1': ruta_guardado_1,
            'ruta_grafico2': ruta_guardado_2,
            'stats': stats,
        }

        return render(request, template_grafica, context)