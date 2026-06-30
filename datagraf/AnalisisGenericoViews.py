# /datagraf/AnalisisGenericoViews.py

import os
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from django.conf import settings
from django.shortcuts import render
from django.views import View
from django.http import JsonResponse

from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView


class AnalisisCSVView(APIView):

    @extend_schema(
        summary="Analisis CSV/Excel Generico",
        description="Muestra un reporte segun datos del archivo CSV o Excel elegido",
        tags=["Analisis CSV"],
    )
    def get(self, request, *args, **kwargs):
        return self._analizar_archivo(request)

    def post(self, request, *args, **kwargs):
        return self._analizar_archivo(request)

    def _analizar_archivo(self, request):
        # ==========================================
        # 1. OBTENER EL ARCHIVO
        # ==========================================
        if request.method == 'POST' and request.FILES.get('archivo'):
            # Archivo subido por el usuario
            archivo = request.FILES['archivo']
            sep = request.POST.get('sep', ';')
            nombre_archivo = archivo.name
            extension = nombre_archivo.split('.')[-1].lower()

            try:
                # Detectar formato por extensión
                if extension in ['csv']:
                    df = pd.read_csv(archivo, sep=sep)
                elif extension in ['xlsx', 'xls']:
                    df = pd.read_excel(archivo)
                else:
                    return JsonResponse({'error': f'Formato no soportado: {extension}. Use CSV, XLSX o XLS'},
                                        status=400)
            except Exception as e:
                return JsonResponse({'error': f'Error al leer el archivo: {str(e)}'}, status=400)
        else:
            # Archivo por defecto (CSV)
            ruta_archivo = request.GET.get('ruta') or os.path.join(settings.BASE_DIR,
                                                                   "data/reportes/excel/logistica.csv")
            sep = request.GET.get('sep', ';')
            nombre_archivo = ruta_archivo.split('/')[-1]
            extension = nombre_archivo.split('.')[-1].lower()

            try:
                if extension in ['csv']:
                    df = pd.read_csv(ruta_archivo, sep=sep)
                elif extension in ['xlsx', 'xls']:
                    df = pd.read_excel(ruta_archivo)
                else:
                    return JsonResponse({'error': f'Formato no soportado: {extension}'}, status=400)
            except Exception as e:
                return JsonResponse({'error': f'No se pudo leer el archivo: {str(e)}'}, status=400)

        # ==========================================
        # 2. ANÁLISIS AUTOMÁTICO
        # ==========================================
        columnas = df.columns.tolist()
        columnas_num = df.select_dtypes(include=['number']).columns.tolist()
        columnas_cat = df.select_dtypes(include=['object', 'category']).columns.tolist()
        estadisticas = df.describe().to_dict()
        nulos = df.isnull().sum().to_dict()
        total_registros = len(df)

        # ==========================================
        # 3. GRÁFICO AUTOMÁTICO
        # ==========================================
        plt.figure(figsize=(12, 6))

        if columnas_cat and columnas_num:
            col_cat = columnas_cat[0]
            col_num = columnas_num[0]
            resumen = df.groupby(col_cat)[col_num].mean().sort_values(ascending=False)
            resumen.plot(kind='bar', color='skyblue', edgecolor='black')
            plt.title(f'📊 {col_num} promedio por {col_cat}')
            plt.xlabel(col_cat)
            plt.ylabel(f'{col_num} promedio')
            plt.xticks(rotation=45, ha='right')
        elif columnas_num:
            col_num = columnas_num[0]
            df[col_num].hist(bins=20, edgecolor='black')
            plt.title(f'📊 Distribución de {col_num}')
            plt.xlabel(col_num)
            plt.ylabel('Frecuencia')
        else:
            plt.text(0.5, 0.5, 'No hay datos suficientes para graficar',
                     ha='center', va='center', fontsize=14)
            plt.axis('off')

        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100)
        buffer.seek(0)
        grafico_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()

        context = {
            'columnas': columnas,
            'columnas_num': columnas_num,
            'columnas_cat': columnas_cat,
            'estadisticas': estadisticas,
            'nulos': nulos,
            'total_registros': total_registros,
            'grafico': grafico_base64,
            'nombre_archivo': nombre_archivo,
            'extension': extension,
        }

        return render(request, 'analisisgenerico/analisis_csv.html', context)


# ========================================================
# CLASE PARA ANÁLISIS DESDE CONSOLA O SCRIPTS
# =========================================================
class AnalisisCSV:
    def __init__(self, ruta_archivo, sep=";"):
        self.ruta_archivo = ruta_archivo
        self.nombre_archivo = ruta_archivo.split('/')[-1]
        self.extension = self.nombre_archivo.split('.')[-1].lower()
        self._cargar_archivo(sep)

    def _cargar_archivo(self, sep):
        """Carga el archivo según su extensión"""
        if self.extension in ['csv']:
            self.df = pd.read_csv(self.ruta_archivo, sep=sep)
        elif self.extension in ['xlsx', 'xls']:
            self.df = pd.read_excel(self.ruta_archivo)
        else:
            raise ValueError(f"Formato no soportado: {self.extension}")

    def analisis_general(self):
        """Muestra un resumen completo del archivo"""
        print(f"📊 Análisis de: {self.nombre_archivo}")
        print(f"📏 Total de registros: {len(self.df)}")
        print(f"📋 Columnas: {list(self.df.columns)}")
        print(f"📌 Tipos de datos:\n{self.df.dtypes}")
        print(f"🧩 Valores nulos por columna:\n{self.df.isnull().sum()}")
        print(f"📊 Estadísticas de columnas numéricas:\n{self.df.describe()}")

    def detectar_columnas_numericas(self):
        return self.df.select_dtypes(include=['number']).columns.tolist()

    def detectar_columnas_categoricas(self):
        return self.df.select_dtypes(include=['object', 'category']).columns.tolist()

    def grafico_automatico(self, guardar=False):
        """Genera gráficos automáticos según las columnas disponibles"""
        columnas_num = self.detectar_columnas_numericas()
        columnas_cat = self.detectar_columnas_categoricas()

        if columnas_cat and columnas_num:
            col_cat = columnas_cat[0]
            col_num = columnas_num[0]
            resumen = self.df.groupby(col_cat)[col_num].mean().sort_values(ascending=False)

            plt.figure(figsize=(12, 6))
            resumen.plot(kind='bar', color='skyblue', edgecolor='black')
            plt.title(f'📊 {col_num} promedio por {col_cat}')
            plt.xlabel(col_cat)
            plt.ylabel(f'{col_num} promedio')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()

            if guardar:
                os.makedirs('data/reportes/graficos', exist_ok=True)
                ruta = f'data/reportes/graficos/grafico_{col_num}_por_{col_cat}.png'
                plt.savefig(ruta, dpi=100)
                print(f"✅ Gráfico guardado en: {ruta}")

            return plt

        elif columnas_num:
            col_num = columnas_num[0]
            plt.figure(figsize=(10, 6))
            self.df[col_num].hist(bins=20, edgecolor='black')
            plt.title(f'📊 Distribución de {col_num}')
            plt.xlabel(col_num)
            plt.ylabel('Frecuencia')
            plt.tight_layout()

            if guardar:
                os.makedirs('data/reportes/graficos', exist_ok=True)
                ruta = f'data/reportes/graficos/histograma_{col_num}.png'
                plt.savefig(ruta, dpi=100)
                print(f"✅ Gráfico guardado en: {ruta}")

            return plt

        print("❌ No hay datos suficientes para graficar")
        return None