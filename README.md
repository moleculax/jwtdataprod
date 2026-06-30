# 🔐 JWT Login data - Django Authentication System

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)



---

## 📋 Descripción general

El sistema es una plataforma web desarrollada en **Django** que integra **autenticación JWT** y herramientas de **análisis de datos** con **Pandas** y **NumPy**. Permite visualizar, procesar y graficar datos provenientes de archivos **CSV**, **JSON** y bases de datos **SQLite**, todo documentado con **Swagger** para una fácil integración con APIs.

---

## 🚀 Características principales

| Característica | Descripción |
|----------------|-------------|
| **Autenticación JWT** | Login seguro con tokens JWT (access/refresh) |
| **Dashboard** | Panel de control con estadísticas y métricas clave |
| **Análisis de datos** | Procesamiento con Pandas y NumPy para datos CSV/JSON/SQLite |
| **Gráficos** | Visualización interactiva con Matplotlib integrada |
| **Reportes** | Generación de reportes en HTML, JSON y Excel |
| **Documentación API** | Swagger UI para explorar y probar endpoints |
| **Base de datos SQLite** | Almacenamiento y consultas SQL nativas |

---

## 📊 Módulos del sistema

### 🔐 Autenticación JWT
- Login con usuario/contraseña
- Generación de tokens (access + refresh)
- Protección de rutas con autenticación

### 📊 Dashboard
- Resumen de ventas y métricas
- Tablas dinámicas con datos filtrados
- Acceso rápido a reportes y gráficos

### 📈 Análisis y Gráficos
- **Pandas**: Lectura de CSV, limpieza, agrupación, estadísticas
- **Matplotlib**: Gráficos de barras, líneas, dispersión, torta
- **Almacenamiento**: Imágenes guardadas en `data/reportes/graficos/`

### 📁 Datos
- **CSV**: Lectura desde `data/reportes/excel/`
- **JSON**: Exportación e importación desde `data/reportes/json/`
- **SQLite**: Tablas con ventas, clientes, productos

### 📝 Documentación
- Swagger en `/swagger/`
- Redoc en `/redoc/`
- Schema OpenAPI en `/api/schema/`

---

## 🛠️ Tecnologías utilizadas

| Tecnología | Función |
|------------|---------|
| **Django 6.0** | Framework web |
| **Django REST Framework** | API REST |
| **Simple JWT** | Autenticación con tokens JWT |
| **drf-spectacular** | Documentación Swagger/OpenAPI |
| **Pandas** | Procesamiento y análisis de datos |
| **NumPy** | Cálculos numéricos y arrays |
| **Matplotlib** | Generación de gráficos |
| **SQLite** | Base de datos integrada |
| **Bootstrap 5** | Estilizado y diseño responsive |

---



---

## 🛠️ Tecnologías utilizadas

| Tecnología | Descripción |
|------------|-------------|
| ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) | Lenguaje de programación principal |
| ![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white) | Framework web de alto nivel |
| ![Django REST Framework](https://img.shields.io/badge/DRF-ff1709?style=for-the-badge&logo=django&logoColor=white) | Toolkit para construir APIs RESTful |
| ![JWT](https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white) | Autenticación basada en tokens |
| ![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white) | Base de datos ligera |
| ![Bootstrap](https://img.shields.io/badge/Bootstrap-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white) | Framework CSS para el dashboard |
| ![Swagger](https://img.shields.io/badge/Swagger-85EA2D?style=for-the-badge&logo=swagger&logoColor=black) | Documentación interactiva de la API |

---

---
## Despliegue en

| **Recurso** |  |
| :--- | :--- |
| 🌐 **URL** | [http://moleculax.pythonanywhere.com](https://moleculax.pythonanywhere.com/) |
| 👤 **Usuario** | `admin` |
| 🔑 **Contraseña** | `admin123` |


---

## 🔧 Instalación y configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com/moleculax/Django.git
cd Django/jwtlogin

```


