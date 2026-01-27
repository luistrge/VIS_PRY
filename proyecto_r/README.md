# COVID-19 Dashboard R Shiny Implementation

This is an R Shiny replication of the Python Shiny COVID-19 dashboard.

## Project Status: ✅ COMPLETE

### All Files:
- `app.R` - Main Shiny application (complete)
- `R/utils.R` - Helper functions (fmt_number)
- `R/data_processing.R` - Data loading and transformation functions
- `R/plots_global.R` - Global page chart functions (5 charts)
- `R/plots_country.R` - Country page chart functions (4 charts)
- `www/styles.css` - Complete CSS styling from Python version
- `data/panel_2020_paises_sin_nan_R_clean.csv` - COVID-19 data

## Installation

```r
# Install required packages
install.packages(c(
  "shiny", "plotly", "dplyr", "tidyr", "lubridate", "readr",
  "htmltools", "glue", "RColorBrewer", "rlang"
))
```

## Quick Start Guide

### Step 1: Create app.R

The main `app.R` file should contain:
- Library imports
- Source all R files from `R/` directory
- Load data using `load_covid_data()`
- Define UI with CSS link and conditional page rendering
- Define server with navigation logic and chart outputs
- Run the app

**Key Structure:**
```r
library(shiny)
library(plotly)
library(dplyr)
library(tidyr)
library(lubridate)
library(readr)
library(htmltools)
library(glue)

# Source helper files
source("R/utils.R")
source("R/data_processing.R")
# source("R/ui_components.R")  # To be created
# source("R/plots_global.R")   # To be created
# source("R/plots_country.R")  # To be created

# Load data
df <- load_covid_data("data/panel_2020_paises_sin_nan_R_clean.csv")
df_ultimo <- get_latest_by_country(df)
paises <- get_country_list(df)
fecha_min <- min(df$fecha, na.rm = TRUE)
fecha_max <- max(df$fecha, na.rm = TRUE)

# UI
ui <- fluidPage(
  tags$head(
    tags$link(rel = "stylesheet", type = "text/css", href = "styles.css")
  ),
  uiOutput("pagina_inicio"),
  uiOutput("pagina_global"),
  uiOutput("pagina_pais")
)

# Server
server <- function(input, output, session) {
  current_page <- reactiveVal("inicio")

  # Navigation
  observeEvent(input$btn_global, { current_page("global") })
  observeEvent(input$btn_pais, { current_page("pais") })
  observeEvent(input$btn_volver_global, { current_page("inicio") })
  observeEvent(input$btn_volver_pais, { current_page("inicio") })

  # Page rendering (to be implemented)
  # output$pagina_inicio <- renderUI({ ... })
  # output$pagina_global <- renderUI({ ... })
  # output$pagina_pais <- renderUI({ ... })
}

shinyApp(ui, server)
```

### Step 2: Create R/ui_components.R

This file should contain three main functions:

1. **`landing_page_ui(total_casos, total_muertes, n_paises, avg_letalidad)`**
   - Hero section with animated SVG (copy from Python app.py lines 319-380)
   - Navigation buttons using `actionButton()`
   - 4 KPI cards with formatted numbers

2. **`global_page_ui(df_ultimo, paises, fecha_min, fecha_max)`**
   - Back button
   - Page header
   - 4 large KPI cards
   - Chart sections with:
     - `plotlyOutput("chart_mapa_global")`
     - `plotlyOutput("chart_wave_global")` with country selector
     - `plotlyOutput("chart_dumbbell_global")` with date filters
     - `plotlyOutput("chart_salud_global")`
     - `plotlyOutput("chart_efficiency_global")` with country filter

3. **`country_page_ui(paises, fecha_min, fecha_max)`**
   - Back button
   - Page header
   - Filter panel with: `selectizeInput("pais_select")`, `dateInput("fecha_inicio")`, `dateInput("fecha_fin")`
   - 5 KPI cards: `uiOutput("kpis_pais")`
   - Chart outputs:
     - `plotlyOutput("chart_temporal_pais")`
     - `plotlyOutput("chart_gauge_pais")`
     - `plotlyOutput("chart_casos_mes")`
     - `plotlyOutput("chart_muertes_mes")`
   - Peak relationship message: `uiOutput("mensaje_relacion_picos")`

### Step 3: Create R/plots_global.R

Five chart functions matching Python implementation:

1. **`create_choropleth_map(df)`**
   ```r
   data_weekly <- aggregate_weekly(df)
   max_incidencia <- quantile(data_weekly$IA_100k_semanal, 0.95, na.rm = TRUE)

   plot_ly(data_weekly,
           type = "choropleth",
           locations = ~iso3c,
           z = ~IA_100k_semanal,
           frame = ~semana_str,
           colors = c("#0f0a2e", "#4f46e5", "#818cf8", "#e0e7ff"),
           ...) %>%
     animation_opts(frame = 400, transition = 200) %>%
     animation_slider(...)
   ```

2. **`create_ridgeline_plot(df, selected_countries)`**
   - Aggregate by week and normalize per country
   - Loop through countries creating polygons with `fill="toself"`

3. **`create_dumbbell_chart(df, selected_countries, fecha_inicio, fecha_fin)`**
   - Get start/end values per country
   - Add lines + markers (green start, red end)

4. **`create_health_lethality_scatter(df_ultimo)`**
   - Bubble scatter: x=gasto_salud_pib, y=letalidad_CFR_pct
   - size=poblacion, color=pib_per_capita_2019

5. **`create_efficiency_matrix(df_ultimo, selected_countries)`**
   - Scatter with median reference lines
   - Annotations for median values

### Step 4: Create R/plots_country.R

Four chart functions:

1. **`create_temporal_evolution(data)`**
   - Line chart with monthly aggregation
   - `plot_ly(type="scatter", mode="lines+markers")`

2. **`create_country_vs_world(data, df_ultimo, pais_nombre)`**
   - Grouped bar chart (barmode="group")
   - 4 metrics: Letalidad, Incidencia, Mortalidad, Gasto Salud

3. **`create_monthly_cases(data)`**
   - Bar chart with peak annotation
   - Green color for peak month

4. **`create_monthly_deaths(data)`**
   - Bar chart with peak annotation
   - Orange color for peak month

## Plotly Styling Template

Apply to all charts:
```r
fig %>%
  layout(
    paper_bgcolor = "rgba(0,0,0,0)",
    plot_bgcolor = "rgba(0,0,0,0)",
    font = list(color = "rgba(255,255,255,0.8)", size = 12),
    xaxis = list(
      gridcolor = "rgba(255,255,255,0.1)",
      showline = TRUE,
      linecolor = "rgba(99,102,241,0.3)"
    ),
    yaxis = list(
      gridcolor = "rgba(255,255,255,0.1)",
      showline = TRUE,
      linecolor = "rgba(99,102,241,0.3)"
    )
  )
```

## Color Palette

- Primary: `#6366f1` (Indigo), `#a855f7` (Purple), `#ec4899` (Pink)
- Success: `#10b981`, `#22c55e` (Green)
- Warning: `#fbbf24`, `#f97316` (Orange)
- Danger: `#ef4444`, `#f87171` (Red)
- Info: `#06b6d4`, `#22d3ee` (Cyan)

## Running the Dashboard

```r
shiny::runApp("path/to/proyecto_final_r")
```

Or open `app.R` in RStudio and click "Run App".

## Reference

- Original Python implementation: `../app.py`
- Plan file: `~/.claude/plans/sunny-bouncing-hartmanis.md`
- Data source: `data/panel_2020_paises_sin_nan_R_clean.csv`

## Next Steps

1. Review Python app.py for exact chart implementations
2. Create remaining R files following the structure above
3. Test each page independently
4. Compare side-by-side with Python version
5. Adjust styling and data calculations as needed

## Notes

- The choropleth animation in R may require custom JavaScript via `htmlwidgets::onRender()` for full compatibility
- Use `req()` to ensure inputs exist before rendering
- Cache data at app startup for performance
- Consider using `debounce()` for expensive reactive calculations
