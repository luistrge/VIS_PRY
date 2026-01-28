# ==============================================================================
# COVID-19 DASHBOARD - R SHINY
# Replication of Python Shiny dashboard
# ==============================================================================

# Load libraries
library(shiny)
library(plotly)
library(dplyr)
library(tidyr)
library(lubridate)
library(readr)
library(htmltools)
library(glue)
library(rlang)

# Source helper files
source("R/utils.R")
source("R/data_processing.R")
source("R/plots_global.R")
source("R/plots_country.R")

# ==============================================================================
# LOAD DATA
# ==============================================================================
df <- load_covid_data("data/panel_2020_paises_sin_nan_R_clean.csv")
df_ultimo <- get_latest_by_country(df)
paises <- get_country_list(df)
fecha_min <- min(df$fecha, na.rm = TRUE)
fecha_max <- max(df$fecha, na.rm = TRUE)

# ==============================================================================
# UI
# ==============================================================================
ui <- fluidPage(
  # Link CSS
  tags$head(
    tags$link(rel = "stylesheet", type = "text/css", href = "styles.css")
  ),

  # Conditional page rendering
  uiOutput("pagina_inicio"),
  uiOutput("pagina_global"),
  uiOutput("pagina_pais")
)

# ==============================================================================
# SERVER
# ==============================================================================
server <- function(input, output, session) {
  # Page state
  current_page <- reactiveVal("inicio")

  # ============================================================================
  # NAVIGATION
  # ============================================================================
  observeEvent(input$btn_global, {
    current_page("global")
  })
  observeEvent(input$btn_pais, {
    current_page("pais")
  })
  observeEvent(input$btn_volver_global, {
    current_page("inicio")
  })
  observeEvent(input$btn_volver_pais, {
    current_page("inicio")
  })

  # ============================================================================
  # LANDING PAGE
  # ============================================================================
  output$pagina_inicio <- renderUI({
    req(current_page() == "inicio")

    total_casos <- sum(df_ultimo$confirmados, na.rm = TRUE)
    total_muertes <- sum(df_ultimo$muertes, na.rm = TRUE)
    n_paises <- n_distinct(df_ultimo$pais)
    avg_letalidad <- mean(df_ultimo$letalidad_CFR_pct, na.rm = TRUE)

    # Format numbers
    casos_fmt <- fmt_number(total_casos)
    muertes_fmt <- fmt_number(total_muertes)

    div(
      class = "hero-landing",
      div(
        class = "hero-section",
        HTML('
          <div class="hero-content">
            <div class="hero-text">
              <div class="hero-badge">
                <span class="hero-badge-dot"></span>
                <span>Dashboard Interactivo</span>
              </div>
              <h1 class="hero-title">
                COVID-19<br>
                <span class="hero-title-accent">Panel de Analisis 2020</span>
              </h1>
              <p class="hero-description">
                Analisis integral del impacto del COVID-19 correlacionado con indicadores
                economicos y de salud. Explora la evolucion temporal y compara datos de mas de 190 paises.
              </p>
            </div>
            <div class="hero-visual">
              <div class="hero-globe">
                <svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
                  <defs>
                    <linearGradient id="lungGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" style="stop-color:#ef4444;stop-opacity:0.8" />
                      <stop offset="100%" style="stop-color:#f97316;stop-opacity:0.5" />
                    </linearGradient>
                    <linearGradient id="virusGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" style="stop-color:#a855f7;stop-opacity:0.9" />
                      <stop offset="100%" style="stop-color:#6366f1;stop-opacity:0.7" />
                    </linearGradient>
                    <filter id="glow">
                      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                      <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
                    </filter>
                  </defs>
                  <path d="M75,70 Q55,75 50,95 Q45,125 55,150 Q65,170 80,165 Q90,160 90,130 Q90,100 85,85 Q82,75 75,70" fill="url(#lungGrad)" opacity="0.7" filter="url(#glow)">
                    <animate attributeName="opacity" values="0.6;0.8;0.6" dur="3s" repeatCount="indefinite"/>
                  </path>
                  <path d="M125,70 Q145,75 150,95 Q155,125 145,150 Q135,170 120,165 Q110,160 110,130 Q110,100 115,85 Q118,75 125,70" fill="url(#lungGrad)" opacity="0.7" filter="url(#glow)">
                    <animate attributeName="opacity" values="0.7;0.9;0.7" dur="2.8s" repeatCount="indefinite"/>
                  </path>
                  <path d="M100,40 L100,85 M90,85 L100,70 L110,85" stroke="#f97316" stroke-width="4" fill="none" stroke-linecap="round"/>
                  <circle cx="140" cy="55" r="20" fill="url(#virusGrad)" filter="url(#glow)">
                    <animate attributeName="r" values="20;22;20" dur="2s" repeatCount="indefinite"/>
                  </circle>
                  <g stroke="#a855f7" stroke-width="2" fill="none">
                    <line x1="140" y1="35" x2="140" y2="25"/><circle cx="140" cy="22" r="4" fill="#a855f7"/>
                    <line x1="140" y1="75" x2="140" y2="85"/><circle cx="140" cy="88" r="4" fill="#c084fc"/>
                    <line x1="120" y1="55" x2="110" y2="55"/><circle cx="107" cy="55" r="4" fill="#818cf8"/>
                    <line x1="160" y1="55" x2="170" y2="55"/><circle cx="173" cy="55" r="4" fill="#a855f7"/>
                  </g>
                  <circle cx="55" cy="50" r="12" fill="url(#virusGrad)" opacity="0.6">
                    <animate attributeName="opacity" values="0.4;0.7;0.4" dur="2.5s" repeatCount="indefinite"/>
                  </circle>
                </svg>
              </div>
            </div>
          </div>
        '),
        div(
          class = "hero-buttons",
          actionButton("btn_global",
            HTML('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg> Visualizacion Global'),
            class = "hero-btn hero-btn-primary"
          ),
          actionButton("btn_pais",
            HTML('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 2v2m0 16v2M4.93 4.93l1.41 1.41m11.32 11.32l1.41 1.41M2 12h2m16 0h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/></svg> Analisis por Pais'),
            class = "hero-btn hero-btn-secondary"
          )
        ),
        HTML(glue('
          <div class="hero-kpis">
            <div class="hero-kpi">
              <div class="hero-kpi-value">{casos_fmt}</div>
              <div class="hero-kpi-label">Casos Totales</div>
            </div>
            <div class="hero-kpi">
              <div class="hero-kpi-value">{muertes_fmt}</div>
              <div class="hero-kpi-label">Muertes</div>
            </div>
            <div class="hero-kpi">
              <div class="hero-kpi-value">{n_paises}</div>
              <div class="hero-kpi-label">Paises</div>
            </div>
            <div class="hero-kpi">
              <div class="hero-kpi-value">{sprintf("%.2f%%", avg_letalidad)}</div>
              <div class="hero-kpi-label">Letalidad</div>
            </div>
          </div>
        '))
      )
    )
  })

  # ============================================================================
  # GLOBAL PAGE
  # ============================================================================
  output$pagina_global <- renderUI({
    req(current_page() == "global")

    total_casos <- sum(df_ultimo$confirmados, na.rm = TRUE)
    total_muertes <- sum(df_ultimo$muertes, na.rm = TRUE)
    n_paises <- n_distinct(df_ultimo$pais)
    avg_letalidad <- mean(df_ultimo$letalidad_CFR_pct, na.rm = TRUE)

    # Format numbers
    casos_fmt <- fmt_number(total_casos)
    muertes_fmt <- fmt_number(total_muertes)

    div(
      class = "container-fluid px-4 dashboard-section",
      style = "padding-top: 80px;",

      # Back button
      actionButton("btn_volver_global",
        HTML('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg> Volver al Inicio'),
        class = "back-button"
      ),

      # Header
      HTML('
        <div class="section-page-header">
          <div class="section-page-icon global">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
          </div>
          <div>
            <h1 class="section-page-title">Visualizacion Global</h1>
            <p class="section-page-subtitle">Analisis comparativo de todos los paises del mundo</p>
          </div>
        </div>
      '),

      # KPIs
      HTML(glue('
        <div class="dashboard-kpis" style="grid-template-columns: repeat(4, 1fr);">
          <div class="dashboard-kpi">
            <div class="dashboard-kpi-icon casos"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 2v4m0 12v4M2 12h4m12 0h4"/></svg></div>
            <div class="dashboard-kpi-value casos">{casos_fmt}</div>
            <div class="dashboard-kpi-label">Casos Confirmados</div>
          </div>
          <div class="dashboard-kpi">
            <div class="dashboard-kpi-icon muertes"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg></div>
            <div class="dashboard-kpi-value muertes">{muertes_fmt}</div>
            <div class="dashboard-kpi-label">Muertes Totales</div>
          </div>
          <div class="dashboard-kpi">
            <div class="dashboard-kpi-icon paises"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M2 12h20"/></svg></div>
            <div class="dashboard-kpi-value paises">{n_paises}</div>
            <div class="dashboard-kpi-label">Paises Analizados</div>
          </div>
          <div class="dashboard-kpi">
            <div class="dashboard-kpi-icon letalidad"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg></div>
            <div class="dashboard-kpi-value letalidad">{sprintf("%.2f%%", avg_letalidad)}</div>
            <div class="dashboard-kpi-label">Tasa de Letalidad</div>
          </div>
        </div>
      ')),

      # Chart 1: Choropleth Map
      div(
        class = "chart-section map-section",
        div(
          class = "section-header",
          tags$span("01", class = "section-number"),
          div(
            div("Mapa Global de Incidencia", class = "section-title"),
            div("Distribucion geografica de casos por 100.000 habitantes", class = "section-subtitle")
          )
        ),
        div(
          class = "chart-content",
          plotlyOutput("chart_mapa_global", height = "600px")
        )
      ),

      # Charts 2-5: Grid
      div(
        class = "charts-grid",
        # Chart 2: Ridgeline
        div(
          class = "chart-section",
          div(
            class = "section-header",
            tags$span("02", class = "section-number"),
            div(
              div("Olas de Contagio", class = "section-title"),
              div("Comparacion de olas entre paises (normalizado)", class = "section-subtitle")
            )
          ),
          fluidRow(
            column(
              12,
              selectizeInput("paises_wave", "Seleccionar paises:",
                choices = paises, selected = head(paises, 5), multiple = TRUE,
                options = list(maxItems = 8)
              )
            )
          ),
          div(
            class = "chart-content",
            plotlyOutput("chart_wave_global", height = "450px")
          )
        ),

        # Chart 3: Dumbbell
        div(
          class = "chart-section",
          div(
            class = "section-header",
            tags$span("03", class = "section-number"),
            div(
              div("Incremento de Incidencia", class = "section-title"),
              div("Crecimiento desde inicio a fin del periodo", class = "section-subtitle")
            )
          ),
          fluidRow(
            column(
              6,
              selectizeInput("paises_dumbbell", "Seleccionar paises:",
                choices = paises, selected = head(paises, 10), multiple = TRUE,
                options = list(maxItems = 15)
              )
            ),
            column(3, dateInput("fecha_inicio_dumbbell", "Fecha inicio:", value = fecha_min, min = fecha_min, max = fecha_max)),
            column(3, dateInput("fecha_fin_dumbbell", "Fecha fin:", value = fecha_max, min = fecha_min, max = fecha_max))
          ),
          div(
            class = "chart-content",
            plotlyOutput("chart_dumbbell_global", height = "450px")
          )
        ),

        # Chart 4: Health vs Lethality
        div(
          class = "chart-section",
          div(
            class = "section-header",
            tags$span("04", class = "section-number"),
            div(
              div("Gasto en Salud vs Letalidad", class = "section-title"),
              div("Inversion sanitaria y tasa de letalidad", class = "section-subtitle")
            )
          ),
          div(
            class = "chart-content",
            plotlyOutput("chart_salud_global", height = "450px")
          )
        ),

        # Chart 5: Efficiency Matrix
        div(
          class = "chart-section chart-efficiency",
          div(
            class = "section-header",
            tags$span("05", class = "section-number"),
            div(
              div("Matriz de Eficiencia Sanitaria", class = "section-title"),
              div("Incidencia vs Letalidad por pais", class = "section-subtitle")
            )
          ),
          fluidRow(
            column(
              12,
              selectizeInput("paises_efficiency", "Filtrar paises (vacio = todos):",
                choices = paises, selected = NULL, multiple = TRUE,
                options = list(maxItems = 20)
              )
            )
          ),
          div(
            class = "chart-content",
            plotlyOutput("chart_efficiency_global", height = "450px")
          )
        )
      ),

      # Footer
      HTML('<div class="footer">Dashboard COVID-19 2020 | Datos: WHO & World Bank | R Shiny + Plotly</div>')
    )
  })

  # ============================================================================
  # GLOBAL PAGE CHARTS
  # ============================================================================
  output$chart_mapa_global <- renderPlotly({
    req(current_page() == "global")
    tryCatch(
      create_choropleth_map(df),
      error = function(e) {
        plot_ly() %>% layout(
          title = list(text = paste("Error:", e$message), font = list(color = "red")),
          paper_bgcolor = "rgba(0,0,0,0)",
          plot_bgcolor = "rgba(0,0,0,0)"
        )
      }
    )
  })

  output$chart_wave_global <- renderPlotly({
    req(current_page() == "global")
    create_ridgeline_plot(df, input$paises_wave)
  })

  output$chart_dumbbell_global <- renderPlotly({
    req(current_page() == "global")
    create_dumbbell_chart(df, input$paises_dumbbell, input$fecha_inicio_dumbbell, input$fecha_fin_dumbbell)
  })

  output$chart_salud_global <- renderPlotly({
    req(current_page() == "global")
    create_health_lethality_scatter(df_ultimo)
  })

  output$chart_efficiency_global <- renderPlotly({
    req(current_page() == "global")
    create_efficiency_matrix(df_ultimo, input$paises_efficiency)
  })

  # ============================================================================
  # COUNTRY PAGE
  # ============================================================================
  output$pagina_pais <- renderUI({
    req(current_page() == "pais")

    div(
      class = "container-fluid px-4 dashboard-section",
      style = "padding-top: 80px;",

      # Back button
      actionButton("btn_volver_pais",
        HTML('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg> Volver al Inicio'),
        class = "back-button"
      ),

      # Header
      HTML('
        <div class="section-page-header">
          <div class="section-page-icon pais">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 2v2m0 16v2M4.93 4.93l1.41 1.41m11.32 11.32l1.41 1.41M2 12h2m16 0h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/></svg>
          </div>
          <div>
            <h1 class="section-page-title">Analisis por Pais</h1>
            <p class="section-page-subtitle">Explora los datos detallados de cada pais</p>
          </div>
        </div>
      '),

      # Filter panel
      div(
        class = "filter-panel",
        div(
          class = "filter-header",
          HTML('<div class="filter-title"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:18px;height:18px;vertical-align:middle;margin-right:8px"><path d="M22 3H2l8 9.46V19l4 2v-8.54L22 3z"/></svg>Selecciona un Pais</div>')
        ),
        fluidRow(
          column(4, selectizeInput("pais_select", "Pais:", choices = paises, selected = paises[1])),
          column(4, dateInput("fecha_inicio", "Fecha inicio:", value = fecha_min, min = fecha_min, max = fecha_max)),
          column(4, dateInput("fecha_fin", "Fecha fin:", value = fecha_max, min = fecha_min, max = fecha_max))
        )
      ),

      # KPIs
      uiOutput("kpis_pais"),

      # Charts row 1
      div(
        class = "charts-row",
        div(
          class = "chart-section",
          div(
            class = "section-header",
            tags$span("01", class = "section-number"),
            div(
              div("Evolucion Temporal", class = "section-title"),
              div("Evolucion de casos confirmados a lo largo del tiempo", class = "section-subtitle")
            )
          ),
          div(
            class = "chart-content",
            plotlyOutput("chart_temporal_pais", height = "450px")
          )
        ),
        div(
          class = "chart-section",
          div(
            class = "section-header",
            tags$span("02", class = "section-number"),
            div(
              div("Comparativa Mundial", class = "section-title"),
              div("Comparacion del pais con la media mundial", class = "section-subtitle")
            )
          ),
          div(
            class = "chart-content",
            plotlyOutput("chart_gauge_pais", height = "450px")
          )
        )
      ),

      # Charts row 2
      div(
        class = "charts-row",
        div(
          class = "chart-section",
          div(
            class = "section-header",
            tags$span("03", class = "section-number"),
            div(
              div("Casos por Mes", class = "section-title"),
              div("Nuevos contagios mensuales", class = "section-subtitle")
            )
          ),
          div(
            class = "chart-content",
            plotlyOutput("chart_casos_mes", height = "450px")
          )
        ),
        div(
          class = "chart-section",
          div(
            class = "section-header",
            tags$span("04", class = "section-number"),
            div(
              div("Muertes por Mes", class = "section-title"),
              div("Fallecimientos mensuales", class = "section-subtitle")
            )
          ),
          div(
            class = "chart-content",
            plotlyOutput("chart_muertes_mes", height = "450px")
          )
        )
      ),

      # Footer
      HTML('<div class="footer">Dashboard COVID-19 2020 | Datos: WHO & World Bank | R Shiny + Plotly</div>')
    )
  })

  # ============================================================================
  # COUNTRY PAGE REACTIVE DATA
  # ============================================================================
  datos_pais_filtrados <- reactive({
    req(input$pais_select)
    req(input$fecha_inicio)
    req(input$fecha_fin)

    result <- df %>%
      dplyr::filter(
        pais == input$pais_select,
        fecha >= input$fecha_inicio,
        fecha <= input$fecha_fin
      )

    result
  })

  # ============================================================================
  # COUNTRY PAGE KPIs
  # ============================================================================
  output$kpis_pais <- renderUI({
    data <- datos_pais_filtrados()
    req(nrow(data) > 0)

    ultimo <- data %>% dplyr::slice_max(fecha, n = 1)

    total_casos <- as.integer(ultimo$confirmados)
    total_muertes <- as.integer(ultimo$muertes)
    incidencia <- ultimo$IA_100k
    letalidad <- ultimo$letalidad_CFR_pct
    gasto_salud <- if ("gasto_salud_pib" %in% names(ultimo)) ultimo$gasto_salud_pib else 0

    # Format numbers
    casos_fmt <- fmt_number(total_casos)
    muertes_fmt <- fmt_number(total_muertes)

    HTML(glue('
      <div class="dashboard-kpis">
        <div class="dashboard-kpi">
          <div class="dashboard-kpi-icon casos"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 2v4m0 12v4M2 12h4m12 0h4"/></svg></div>
          <div class="dashboard-kpi-value casos">{casos_fmt}</div>
          <div class="dashboard-kpi-label">Casos Confirmados</div>
        </div>
        <div class="dashboard-kpi">
          <div class="dashboard-kpi-icon muertes"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg></div>
          <div class="dashboard-kpi-value muertes">{muertes_fmt}</div>
          <div class="dashboard-kpi-label">Muertes Totales</div>
        </div>
        <div class="dashboard-kpi">
          <div class="dashboard-kpi-icon paises"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg></div>
          <div class="dashboard-kpi-value paises">{sprintf("%.1f", incidencia)}</div>
          <div class="dashboard-kpi-label">Incidencia/100k</div>
        </div>
        <div class="dashboard-kpi">
          <div class="dashboard-kpi-icon letalidad"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg></div>
          <div class="dashboard-kpi-value letalidad">{sprintf("%.2f%%", letalidad)}</div>
          <div class="dashboard-kpi-label">Tasa de Letalidad</div>
        </div>
        <div class="dashboard-kpi">
          <div class="dashboard-kpi-icon salud"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/></svg></div>
          <div class="dashboard-kpi-value salud">{sprintf("%.1f%%", gasto_salud)}</div>
          <div class="dashboard-kpi-label">Gasto Salud/PIB</div>
        </div>
      </div>
    '))
  })

  # ============================================================================
  # COUNTRY PAGE CHARTS
  # ============================================================================
  output$chart_temporal_pais <- renderPlotly({
    req(current_page() == "pais")
    data <- datos_pais_filtrados()
    req(nrow(data) > 0)
    tryCatch(
      create_temporal_evolution(data),
      error = function(e) {
        plot_ly() %>% layout(
          title = list(text = paste("Error:", e$message), font = list(color = "red")),
          paper_bgcolor = "rgba(0,0,0,0)",
          plot_bgcolor = "rgba(0,0,0,0)"
        )
      }
    )
  })

  output$chart_gauge_pais <- renderPlotly({
    req(current_page() == "pais")
    data <- datos_pais_filtrados()
    req(nrow(data) > 0)
    tryCatch(
      create_country_vs_world(data, df_ultimo, input$pais_select),
      error = function(e) {
        plot_ly() %>% layout(
          title = list(text = paste("Error:", e$message), font = list(color = "red")),
          paper_bgcolor = "rgba(0,0,0,0)",
          plot_bgcolor = "rgba(0,0,0,0)"
        )
      }
    )
  })

  output$chart_casos_mes <- renderPlotly({
    req(current_page() == "pais")
    data <- datos_pais_filtrados()
    req(nrow(data) > 0)
    tryCatch(
      create_monthly_cases(data),
      error = function(e) {
        plot_ly() %>% layout(
          title = list(text = paste("Error:", e$message), font = list(color = "red")),
          paper_bgcolor = "rgba(0,0,0,0)",
          plot_bgcolor = "rgba(0,0,0,0)"
        )
      }
    )
  })

  output$chart_muertes_mes <- renderPlotly({
    req(current_page() == "pais")
    data <- datos_pais_filtrados()
    req(nrow(data) > 0)
    tryCatch(
      create_monthly_deaths(data),
      error = function(e) {
        plot_ly() %>% layout(
          title = list(text = paste("Error:", e$message), font = list(color = "red")),
          paper_bgcolor = "rgba(0,0,0,0)",
          plot_bgcolor = "rgba(0,0,0,0)"
        )
      }
    )
  })

}

# ==============================================================================
# RUN APP
# ==============================================================================
shinyApp(ui, server)
