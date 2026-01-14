# 🦠 Dashboard COVID-19 2020

Dashboard interactivo para la visualización y análisis de datos de COVID-19 durante el año 2020, desarrollado con **Shiny for Python** y **Plotly**.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
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
- **Casos diarios** y **Muertes diarias** - Evolución temporal

## 🚀 Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/tu-repo.git
cd tu-repo
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
├── app.py                                 # Aplicación principal
├── panel_2020_paises_sin_nan_R_clean.csv  # Datos COVID-19
├── requirements.txt                       # Dependencias Python
├── README.md                              # Este archivo
└── .gitignore                             # Archivos ignorados por Git
```

## 📸 Capturas de pantalla

### Página de Inicio
Landing page con KPIs globales y navegación a las secciones.

### Visualización Global
Mapa interactivo animado y gráficos comparativos entre países.

### Análisis por País
Filtros por país y fechas, con gráficos de evolución temporal y comparativa mundial.

## 📝 Licencia

Este proyecto es de uso académico.

## 👤 Autor

Desarrollado como trabajo académico para la asignatura de Visualización de Datos.

---

*Dashboard COVID-19 2020 | Datos: WHO & World Bank | Shiny for Python + Plotly*
