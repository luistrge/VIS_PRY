<div align="center">

# 🦠 COVID-19 Global Analytics Dashboard 2020

[![R Shiny](https://img.shields.io/badge/R%20Shiny-4.0+-blue?logo=r&logoColor=white)](https://shiny.rstudio.com/)
[![Plotly](https://img.shields.io/badge/Plotly-Interactive-3F4F75?logo=plotly)](https://plotly.com/r/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Dashboard](https://img.shields.io/badge/Dashboard-Live-teal)](https://github.com/luistrge/VIS_PRY)

**Dashboard interactivo de visualización epidemiológica con estética Cyberpunk Scientific**

*Análisis integral del impacto del COVID-19 durante 2020 correlacionado con indicadores económicos y de salud de 189 países*

<img src="https://img.shields.io/badge/Casos_Analizados-83M+-22D3EE?style=for-the-badge" alt="Casos"/>
<img src="https://img.shields.io/badge/Países-189-22c55e?style=for-the-badge" alt="Países"/>
<img src="https://img.shields.io/badge/Visualizaciones-9+-F97316?style=for-the-badge" alt="Visualizaciones"/>

</div>

---

## ⚡ Lanzamiento Rápido

### Opción 1: Desde Terminal/Consola R

```r
# 1. Clonar repositorio
# git clone https://github.com/luistrge/VIS_PRY.git
# cd VIS_PRY

# 2. Instalar dependencias (solo la primera vez)
install.packages(c("shiny", "plotly", "dplyr", "tidyr", "lubridate", "readr", "htmltools", "glue", "rlang"))

# 3. Ejecutar dashboard
shiny::runApp()
```

### Opción 2: Desde RStudio
1. Abrir el proyecto o archivo `app.R`
2. Clic en **▶ Run App** (esquina superior derecha)
3. El dashboard se abrirá en el navegador

### Opción 3: Una línea
```r
shiny::runGitHub("VIS_PRY", "luistrge")
```

> 💡 **Tip**: El dashboard se abre automáticamente en `http://127.0.0.1:XXXX`

---

## 📊 Descripción del Proyecto

Este dashboard proporciona un análisis visual interactivo de los datos epidemiológicos del COVID-19 durante 2020, combinando:

- **Métricas de salud pública**: Casos, muertes, incidencia, letalidad
- **Indicadores socioeconómicos**: PIB per cápita, gasto en salud
- **Análisis temporal**: Evolución semanal y mensual de la pandemia
- **Comparativas internacionales**: Rankings y correlaciones entre países

### 🗂️ Fuentes de Datos

| Fuente | Datos | Cobertura |
|--------|-------|-----------|
| **WHO** (OMS) | Casos confirmados, muertes, tasas de incidencia | Global 2020 |
| **World Bank** | PIB per cápita, gasto en salud (% PIB) | 190+ países |

---

## 🏗️ Arquitectura del Dashboard

```
┌─────────────────────────────────────────────────────────────────┐
│                        🏠 HOME (Landing)                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │ 83M+     │ │ 1.8M+    │ │ 190+     │ │ 2.18%    │  KPIs     │
│  │ Casos    │ │ Muertes  │ │ Países   │ │ Letalidad│           │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │
│                    ↓                    ↓                       │
│         [🌍 Global]              [📍 Por País]                  │
└─────────────────────────────────────────────────────────────────┘
         │                                │
         ▼                                ▼
┌─────────────────────┐      ┌─────────────────────┐
│  VISUALIZACIÓN      │      │  ANÁLISIS POR PAÍS  │
│     GLOBAL          │      │                     │
│  ┌───────────────┐  │      │  ┌───────────────┐  │
│  │ 🗺️ Mapa       │  │      │  │ 📈 Evolución  │  │
│  │   Coroplético │  │      │  │   Temporal    │  │
│  └───────────────┘  │      │  └───────────────┘  │
│  ┌───────────────┐  │      │  ┌───────────────┐  │
│  │ 🌊 Ridgeline  │  │      │  │ 🎯 Radar      │  │
│  │   Plot        │  │      │  │   Chart       │  │
│  └───────────────┘  │      │  └───────────────┘  │
│  ┌───────────────┐  │      │  ┌───────────────┐  │
│  │ 📊 Dumbbell   │  │      │  │ 📊 Casos      │  │
│  │   Chart       │  │      │  │   Mensuales   │  │
│  └───────────────┘  │      │  └───────────────┘  │
│  ┌───────────────┐  │      │  ┌───────────────┐  │
│  │ 💰 Scatter    │  │      │  │ ☠️ Muertes    │  │
│  │   Económico   │  │      │  │   Mensuales   │  │
│  └───────────────┘  │      │  └───────────────┘  │
│  ┌───────────────┐  │      │                     │
│  │ ⚖️ Matriz     │  │      │                     │
│  │   Eficiencia  │  │      │                     │
│  └───────────────┘  │      │                     │
└─────────────────────┘      └─────────────────────┘
```

---

## 📈 Métricas Estadísticas

### 🔬 Indicadores Epidemiológicos

| Métrica | Fórmula | Interpretación |
|---------|---------|----------------|
| **Incidencia Acumulada** | $$IA = \frac{confirmados}{población} \times 100,000$$ | Casos totales por cada 100,000 habitantes |
| **Tasa de Mortalidad** | $$TM = \frac{muertes}{población} \times 100,000$$ | Muertes por cada 100,000 habitantes |
| **Letalidad (CFR)** | $$CFR = \frac{muertes}{confirmados} \times 100$$ | % de casos que resultan en muerte |
| **Incidencia Semanal** | $$IS = \frac{casos_{semana}}{población} \times 100,000$$ | Nuevos casos semanales normalizados |

### 💹 Indicadores Socioeconómicos

| Métrica | Fuente | Aplicación en Dashboard |
|---------|--------|-------------------------|
| **PIB per cápita (2019)** | World Bank | Correlación con capacidad de respuesta sanitaria |
| **Gasto en Salud (% PIB)** | World Bank | Análisis de eficiencia del sistema de salud |

### 📐 Normalización para Radar Chart
```
Fórmula Min-Max: x_norm = (x - min) / (max - min)
Rango resultante: [0, 1]
```

---

## 🎨 Visualizaciones Detalladas

### 🌍 Página Global (5 Gráficos)

#### 1. Mapa Coroplético Animado
| Atributo | Valor |
|----------|-------|
| Tipo | `choropleth` con animación temporal |
| Escala de color | **Plasma** (morado → magenta → naranja → amarillo) |
| Métrica | Incidencia semanal por 100k habitantes |
| Interactividad | Slider temporal, hover con datos detallados |
| Frames | 52 semanas de 2020 |

#### 2. Ridgeline Plot
- **Propósito**: Comparar patrones de olas pandémicas entre países
- **Técnica**: Áreas apiladas con transparencia (opacidad 0.6)
- **Datos**: Casos normalizados por máximo de cada país

#### 3. Gráfico Dumbbell
- **Propósito**: Visualizar crecimiento de incidencia entre dos fechas
- **Código de colores**: 🟢 Verde (fecha inicio) → 🔴 Rojo (fecha fin)
- **Línea conectora**: Muestra magnitud del cambio

#### 4. Scatter Gasto Salud vs Letalidad
| Canal Visual | Variable |
|--------------|----------|
| Eje X | Gasto en salud (% PIB) |
| Eje Y | Letalidad (CFR %) |
| Tamaño burbuja | Población |
| Color | PIB per cápita |

#### 5. Matriz de Eficiencia
- **Cuadrantes**: Definidos por medianas globales
- **Ejes**: Incidencia vs Letalidad
- **Interpretación**: 
  - ↙️ Mejor desempeño (baja incidencia, baja letalidad)
  - ↗️ Peor desempeño (alta incidencia, alta letalidad)

### 📍 Página País (4 Gráficos)

#### 1. Evolución Temporal
```
Tipo: Línea con área rellena
Color: Cian Neon (#22D3EE)
Datos: Casos acumulados mensuales
```

#### 2. Radar Chart Comparativo
| Métrica | Normalización |
|---------|---------------|
| Incidencia/100k | Min-Max global |
| Mortalidad/100k | Min-Max global |
| Letalidad (%) | Min-Max global |
| Gasto Salud (%) | Min-Max global |
| PIB per cápita | Min-Max global |

**Colores**: 🔵 País seleccionado (#22D3EE) vs ⚪ Media mundial (#9CA3AF)

#### 3. Casos Mensuales (Barras)
- Color base: Turquesa (#06B6D4)
- Pico resaltado: Azul (#0058ca)
- Anotación "PICO" sobre el máximo

#### 4. Muertes Mensuales (Barras)
- Color base: Naranja (#F97316)
- Pico resaltado: Rojo (#ec1c00)
- Anotación "PICO" sobre el máximo

---

## 🎨 Diseño: Estética Cyberpunk Scientific

### 🎨 Paleta de Colores

<table>
<tr>
<td>

**🌙 Fondos**
| Color | Hex | Uso |
|-------|-----|-----|
| <img src="https://via.placeholder.com/20/030d1b/030d1b?text=+" /> | `#030d1b` | Fondo principal |
| <img src="https://via.placeholder.com/20/0a0e27/0a0e27?text=+" /> | `#0a0e27` | Fondo secundario |
| <img src="https://via.placeholder.com/20/061826/061826?text=+" /> | `#061826` | Gradiente hero |

</td>
<td>

**💡 Primarios**
| Color | Hex | Uso |
|-------|-----|-----|
| <img src="https://via.placeholder.com/20/22D3EE/22D3EE?text=+" /> | `#22D3EE` | Cian neón |
| <img src="https://via.placeholder.com/20/14b8a6/14b8a6?text=+" /> | `#14b8a6` | Turquesa |
| <img src="https://via.placeholder.com/20/22c55e/22c55e?text=+" /> | `#22c55e` | Verde éxito |

</td>
</tr>
<tr>
<td>

**⚠️ Alertas**
| Color | Hex | Uso |
|-------|-----|-----|
| <img src="https://via.placeholder.com/20/F97316/F97316?text=+" /> | `#F97316` | Naranja |
| <img src="https://via.placeholder.com/20/ef4444/ef4444?text=+" /> | `#ef4444` | Rojo |
| <img src="https://via.placeholder.com/20/f59e0b/f59e0b?text=+" /> | `#f59e0b` | Ámbar |

</td>
<td>

**🌈 Acentos**
| Color | Hex | Uso |
|-------|-----|-----|
| <img src="https://via.placeholder.com/20/6366f1/6366f1?text=+" /> | `#6366f1` | Índigo |
| <img src="https://via.placeholder.com/20/a855f7/a855f7?text=+" /> | `#a855f7` | Púrpura |
| <img src="https://via.placeholder.com/20/9CA3AF/9CA3AF?text=+" /> | `#9CA3AF` | Gris neutro |

</td>
</tr>
</table>

### ✨ Efectos Visuales

| Efecto | Descripción | CSS |
|--------|-------------|-----|
| **Glow Pulse** | Animación de brillo en botones | `box-shadow` animado |
| **Float** | Elementos flotantes suaves | `translateY` animation |
| **Shimmer** | Efecto de destello en hover | `background-position` |
| **Slide In Up** | Entrada con desplazamiento | `opacity` + `transform` |
| **Count Up** | Animación de números | `scale` + `opacity` |

### 🔤 Tipografía
- **Fuente**: Inter (Google Fonts)
- **Pesos**: 300, 400, 500, 600, 700
- **Escala**: 1.5rem base, hasta 3.5rem en títulos hero

---

## 📁 Estructura del Proyecto

```
VIS_PRY/
├── 📄 app.R                    # Aplicación principal Shiny (667 líneas)
├── 📄 README.md                # Este archivo
├── 📄 .gitignore               # Archivos ignorados
│
├── 📂 R/                       # Módulos R
│   ├── utils.R                 # Funciones auxiliares (fmt_number, etc.)
│   ├── data_processing.R       # Carga y transformación de datos
│   ├── plots_global.R          # 5 funciones de gráficos globales
│   └── plots_country.R         # 4 funciones de gráficos por país
│
├── 📂 www/                     # Assets web
│   └── styles.css              # Estilos Cyberpunk (259 líneas)
│
└── 📂 data/                    # Datos
    └── panel_2020_paises_sin_nan_R_clean.csv
```

### 📊 Descripción de Archivos R

| Archivo | Funciones Principales | Líneas |
|---------|----------------------|--------|
| `app.R` | UI + Server Shiny, navegación, renderizado | ~667 |
| `utils.R` | `fmt_number()` - formato de números grandes | ~20 |
| `data_processing.R` | `load_covid_data()`, `get_latest_by_country()`, `get_country_list()` | ~50 |
| `plots_global.R` | `plot_choropleth_map()`, `plot_ridgeline()`, `plot_dumbbell()`, `plot_scatter_health()`, `plot_efficiency_matrix()` | ~300 |
| `plots_country.R` | `plot_country_evolution()`, `plot_radar_chart()`, `plot_monthly_cases()`, `plot_monthly_deaths()` | ~250 |

---

## ⚙️ Requisitos del Sistema

### Versión de R
```
R >= 4.0.0
```

### Paquetes Requeridos

```r
install.packages(c(
  "shiny",       # 🌐 Framework web reactivo
  "plotly",      # 📊 Gráficos interactivos
  "dplyr",       # 🔧 Manipulación de datos
  "tidyr",       # 🔄 Transformación de datos
  "lubridate",   # 📅 Manejo de fechas
  "readr",       # 📖 Lectura de CSV
  "htmltools",   # 🏗️ Generación HTML
  "glue",        # 🧵 Interpolación de strings
  "rlang"        # ⚡ Programación tidyverse
))
```

---

## 🎮 Uso del Dashboard

### 🧭 Navegación

```
[Home] ──┬──> [Visualización Global] ──> [Volver]
         │
         └──> [Análisis por País] ──> [Volver]
```

### 🎛️ Controles Interactivos

| Control | Ubicación | Función |
|---------|-----------|---------|
| **Selector de Países** | Panel lateral | Filtra gráficos multipaís |
| **Rango de Fechas** | Panel lateral | Define período de análisis |
| **Slider Animación** | Mapa coroplético | Navega por semanas |
| **Hover** | Todos los gráficos | Muestra tooltips detallados |
| **Zoom** | Mapa y scatters | Amplía regiones de interés |

---

## 🔧 Notas Técnicas

### Animación del Mapa Coroplético
```r
# Configuración crítica para animación
plot_ly(...) %>%
  animation_opts(frame = 500, redraw = TRUE) %>%
  animation_slider(...)

# redraw = TRUE es ESENCIAL para actualizar colores
```

### Optimización de Rendimiento
- ✅ Datos pre-cargados al inicio (`df <- load_covid_data()`)
- ✅ Agregación semanal reduce frames de animación
- ✅ Filtrado reactivo con `req()` evita cálculos innecesarios
- ✅ `customdata` para tooltips sin recálculo

### Workaround: Fecha en Hover
```r
# %{frame} no funciona en hover, usar customdata
customdata = ~fecha,
hovertemplate = "Fecha: %{customdata}<br>..."
```

---

## 🤝 Contribuciones

¿Encontraste un bug o tienes una mejora? ¡Las contribuciones son bienvenidas!

1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Añade nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

---

## 📜 Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

---

## 🙏 Créditos

| Recurso | Fuente |
|---------|--------|
| **Datos epidemiológicos** | WHO (Organización Mundial de la Salud) |
| **Datos económicos** | World Bank Open Data |
| **Framework** | R Shiny + Plotly |
| **Tipografía** | Google Fonts (Inter) |
| **Iconos** | SVG personalizados |

---

<div align="center">

**🦠 COVID-19 Global Analytics Dashboard 2020**

Desarrollado con ❤️ usando R Shiny + Plotly

[![GitHub](https://img.shields.io/badge/GitHub-luistrge/VIS__PRY-181717?logo=github)](https://github.com/luistrge/VIS_PRY)

</div>
