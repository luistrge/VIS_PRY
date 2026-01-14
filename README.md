# 🦠 Dashboard COVID-19 2020

Dashboard interactivo para la visualización y análisis de datos de COVID-19 durante el año 2020, desarrollado con **Shiny for Python** y **Plotly**.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Shiny](https://img.shields.io/badge/Shiny-Python-green.svg)
![Plotly](https://img.shields.io/badge/Plotly-Interactive-orange.svg)

## 📋 Descripción

Este dashboard proporciona una visualización completa de la pandemia COVID-19 con dos secciones principales:

### 🌍 Visualización Global
- **Mapa mundial interactivo** con animación temporal de incidencia semanal
- **Olas de contagio** - Comparación entre países (gráfico ridgeline normalizado)
- **Incremento de incidencia** - Crecimiento desde inicio a fin del período (dumbbell chart)
- **Gasto en Salud vs Letalidad** - Análisis de inversión sanitaria
- **Matriz de Eficiencia Sanitaria** - Incidencia vs Letalidad por país

### 📍 Análisis por País
- **KPIs del país**: Casos, muertes, incidencia, letalidad y gasto en salud
- **Evolución temporal** de casos confirmados
- **Comparativa mundial** - Comparación del país con la media mundial
- **Casos por mes** y **Muertes por mes** - Evolución temporal con identificación de picos

## 🚀 Instalación y Ejecución

### Requisitos previos
- Python 3.10 o superior
- pip (gestor de paquetes de Python)

### 1. Clonar el repositorio
```bash
git clone <URL_DEL_REPOSITORIO>
cd Trabajo_Académico
```

### 2. Crear entorno virtual (recomendado)
```bash
python -m venv venv
source venv/bin/activate  # En Linux/Mac
# o
venv\Scripts\activate  # En Windows
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

## ▶️ Ejecución

Para iniciar la aplicación:

```bash
shiny run app.py
```

O especificando un puerto:

```bash
shiny run app.py --port 8000
```

La aplicación estará disponible en: **http://127.0.0.1:8000**

## 📊 Datos

El dashboard utiliza el archivo `panel_2020_paises_sin_nan_R_clean.csv` que contiene:

| Variable | Descripción |
|----------|-------------|
| `pais` | Nombre del país |
| `iso3c` | Código ISO del país |
| `fecha` | Fecha del registro |
| `confirmados` | Casos confirmados acumulados |
| `muertes` | Muertes acumuladas |
| `confirmados_dia` | Nuevos casos diarios |
| `muertes_dia` | Nuevas muertes diarias |
| `IA_100k` | Incidencia acumulada por 100.000 habitantes |
| `tasa_mortalidad_por_millon` | Tasa de mortalidad por millón |
| `letalidad_CFR_pct` | Tasa de letalidad (Case Fatality Rate) |
| `pib_per_capita_2019` | PIB per cápita 2019 |
| `gasto_salud_pib` | Gasto en salud como % del PIB |
| `poblacion` | Población del país |

**Fuentes de datos**: WHO (Organización Mundial de la Salud) & World Bank

## 🛠️ Tecnologías utilizadas

- **[Shiny for Python](https://shiny.posit.co/py/)** - Framework para aplicaciones web interactivas
- **[Plotly](https://plotly.com/python/)** - Gráficos interactivos
- **[Pandas](https://pandas.pydata.org/)** - Manipulación de datos
- **[ShinyWidgets](https://github.com/posit-dev/py-shinywidgets)** - Integración de widgets Plotly con Shiny

## 📁 Estructura del proyecto

```
.
├── app.py                                 # Aplicación principal Shiny
├── panel_2020_paises_sin_nan_R_clean.csv  # Dataset COVID-19
├── requirements.txt                       # Dependencias Python
├── README.md                              # Documentación
├── dashboard_covid19_2020.html            # Versión HTML estática (generada)
└── .gitignore                             # Archivos ignorados por Git
```

## 📊 Dataset

El archivo `panel_2020_paises_sin_nan_R_clean.csv` contiene datos de +190 países con las siguientes variables:

| Variable | Descripción |
|----------|-------------|
| `pais` | Nombre del país |
| `iso3c` | Código ISO 3166-1 alpha-3 |
| `fecha` | Fecha del registro |
| `confirmados` | Casos confirmados acumulados |
| `muertes` | Muertes acumuladas |
| `confirmados_dia` | Nuevos casos diarios |
| `muertes_dia` | Nuevas muertes diarias |
| `IA_100k` | Incidencia acumulada por 100.000 habitantes |
| `tasa_mortalidad_100k` | Tasa de mortalidad por 100.000 habitantes |
| `letalidad_CFR_pct` | Tasa de letalidad (Case Fatality Rate) en % |
| `pib_per_capita_2019` | PIB per cápita 2019 (USD) |
| `gasto_salud_pib` | Gasto en salud como % del PIB |
| `poblacion` | Población del país |

**Fuentes**: WHO (Organización Mundial de la Salud) & World Bank

## 🛠️ Tecnologías

| Tecnología | Uso |
|------------|-----|
| [Shiny for Python](https://shiny.posit.co/py/) | Framework web interactivo |
| [Plotly](https://plotly.com/python/) | Gráficos interactivos |
| [Pandas](https://pandas.pydata.org/) | Procesamiento de datos |
| [NumPy](https://numpy.org/) | Operaciones numéricas |
| [Uvicorn](https://www.uvicorn.org/) | Servidor ASGI |


## 📝 Licencia

Proyecto de uso académico - Asignatura de Visualización de Datos.

## 👤 Autor

Desarrollado como trabajo académico por: Fernando Martínez Gómez, Sergio Ortiz Montesinos y Luis Trigueros Espada
