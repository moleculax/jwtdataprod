# /datagraf/AnalisisGenericoViews.py

import os
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import numpy as np
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
        tags=["Analisis CSV/Excel Generico"],
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
            archivo = request.FILES['archivo']
            sep = request.POST.get('sep', ';')
            nombre_archivo = archivo.name
            extension = nombre_archivo.split('.')[-1].lower()

            try:
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
        # 3. CONVERTIR DATOS A HTML (TABLA) - SOLO PRIMERAS 15 FILAS
        # ==========================================
        # Convertir primeras 15 filas a HTML con clases Bootstrap
        tabla_html = df.head(15).to_html(
            classes="table table-striped table-hover table-bordered",
            index=False,
            justify="left"
        )

        # ==========================================
        # 4. GRÁFICO DE BARRAS CON COLORES VIVOS (menor a mayor)
        # ==========================================
        plt.figure(figsize=(12, 6))

        if columnas_cat and columnas_num:
            col_cat = columnas_cat[0]
            col_num = columnas_num[0]

            # ORDENAR DE MENOR A MAYOR
            resumen = df.groupby(col_cat)[col_num].mean().sort_values(ascending=True)

            # Paleta de colores vivos
            colores_vivos = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
                             '#DDA0DD', '#FF8A5C', '#A29BFE', '#FD79A8', '#00B894',
                             '#E17055', '#0984E3', '#FDCB6E', '#6C5CE7', '#00CEC9']

            # Asignar colores a cada barra
            colores = colores_vivos[:len(resumen)]

            # Crear gráfico de barras con colores vivos
            bars = plt.bar(resumen.index, resumen.values, color=colores, edgecolor='black', linewidth=1.2)

            # Valores encima de las barras
            for i, v in enumerate(resumen.values):
                plt.text(i, v + (v * 0.02), f'{v:.1f}',
                         ha='center', va='bottom', fontsize=9, fontweight='bold')

            plt.title(f'📊 {col_num} promedio por {col_cat}', fontsize=14, fontweight='bold')
            plt.xlabel(col_cat, fontsize=12)
            plt.ylabel(f'{col_num} promedio', fontsize=12)
            plt.xticks(rotation=45, ha='right')
            plt.grid(axis='y', linestyle='--', alpha=0.3)

        elif columnas_num:
            col_num = columnas_num[0]
            df[col_num].hist(bins=20, edgecolor='black', color='#4ECDC4')
            plt.title(f'📊 Distribución de {col_num}', fontsize=14, fontweight='bold')
            plt.xlabel(col_num, fontsize=12)
            plt.ylabel('Frecuencia', fontsize=12)
            plt.grid(axis='y', linestyle='--', alpha=0.3)
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
            'tabla_datos': tabla_html,
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
        if self.extension in ['csv']:
            self.df = pd.read_csv(self.ruta_archivo, sep=sep)
        elif self.extension in ['xlsx', 'xls']:
            self.df = pd.read_excel(self.ruta_archivo)
        else:
            raise ValueError(f"Formato no soportado: {self.extension}")

    def analisis_general(self):
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
        """Genera gráfico de barras con colores vivos"""
        columnas_num = self.detectar_columnas_numericas()
        columnas_cat = self.detectar_columnas_categoricas()

        if columnas_cat and columnas_num:
            col_cat = columnas_cat[0]
            col_num = columnas_num[0]

            resumen = self.df.groupby(col_cat)[col_num].mean().sort_values(ascending=True)

            plt.figure(figsize=(12, 6))

            colores_vivos = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
                             '#DDA0DD', '#FF8A5C', '#A29BFE', '#FD79A8', '#00B894',
                             '#E17055', '#0984E3', '#FDCB6E', '#6C5CE7', '#00CEC9']

            colores = colores_vivos[:len(resumen)]

            bars = plt.bar(resumen.index, resumen.values, color=colores, edgecolor='black', linewidth=1.2)

            for i, v in enumerate(resumen.values):
                plt.text(i, v + (v * 0.02), f'{v:.1f}',
                         ha='center', va='bottom', fontsize=9, fontweight='bold')

            plt.title(f'📊 {col_num} promedio por {col_cat}', fontsize=14, fontweight='bold')
            plt.xlabel(col_cat, fontsize=12)
            plt.ylabel(f'{col_num} promedio', fontsize=12)
            plt.xticks(rotation=45, ha='right')
            plt.grid(axis='y', linestyle='--', alpha=0.3)
            plt.tight_layout()

            if guardar:
                ruta = f'data/reportes/graficos/barras_{col_num}_por_{col_cat}.png'
                plt.savefig(ruta, dpi=100)
                print(f"✅ Gráfico guardado en: {ruta}")

            return plt

        elif columnas_num:
            col_num = columnas_num[0]
            plt.figure(figsize=(10, 6))
            self.df[col_num].hist(bins=20, edgecolor='black', color='#4ECDC4')
            plt.title(f'📊 Distribución de {col_num}', fontsize=14, fontweight='bold')
            plt.xlabel(col_num, fontsize=12)
            plt.ylabel('Frecuencia', fontsize=12)
            plt.grid(axis='y', linestyle='--', alpha=0.3)
            plt.tight_layout()

            if guardar:
                ruta = f'data/reportes/graficos/histograma_{col_num}.png'
                plt.savefig(ruta, dpi=100)
                print(f"✅ Gráfico guardado en: {ruta}")

            return plt

        print("❌ No hay datos suficientes para graficar")
        return None