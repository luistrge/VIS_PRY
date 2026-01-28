# ==============================================================================
# COUNTRY PAGE CHART FUNCTIONS
# ==============================================================================

#' Create temporal evolution line chart
#' Cyberpunk Scientific - Cian Neón (#22D3EE)
#'
#' @param data Filtered country data
#' @return Plotly figure
create_temporal_evolution <- function(data) {
  if (is.null(data) || nrow(data) == 0) {
    return(plot_ly() %>%
             layout(paper_bgcolor = "rgba(0,0,0,0)", plot_bgcolor = "rgba(0,0,0,0)"))
  }

  data_mes <- data %>%
    dplyr::mutate(mes = format(fecha, "%Y-%m")) %>%
    dplyr::group_by(mes) %>%
    dplyr::summarise(confirmados = max(confirmados, na.rm = TRUE), .groups = "drop") %>%
    dplyr::arrange(mes)

  # Cian Neón para alta visibilidad
  fig <- plot_ly(
    data = data_mes,
    type = "scatter",
    mode = "lines+markers",
    x = ~mes,
    y = ~confirmados,
    fill = "tozeroy",
    fillcolor = "rgba(34, 211, 238, 0.15)",
    line = list(color = "#22D3EE", width = 3),
    marker = list(color = "#22D3EE", size = 10, line = list(color = "#06B6D4", width = 2)),
    hovertemplate = "<b>%{x}</b><br>Casos: %{y:,.0f}<extra></extra>"
  ) %>%
    layout(
      height = 400,
      paper_bgcolor = "rgba(0,0,0,0)",
      plot_bgcolor = "rgba(0,0,0,0)",
      font = list(color = "#94A3B8", size = 12),
      xaxis = list(
        title = list(text = "Mes", font = list(size = 13, color = "#94A3B8")),
        gridcolor = "rgba(148, 163, 184, 0.1)",
        tickangle = -45,
        showline = TRUE,
        linecolor = "rgba(148, 163, 184, 0.2)",
        tickfont = list(color = "#94A3B8")
      ),
      yaxis = list(
        title = list(text = "Casos Acumulados", font = list(size = 13, color = "#94A3B8")),
        gridcolor = "rgba(148, 163, 184, 0.1)",
        showline = TRUE,
        linecolor = "rgba(148, 163, 184, 0.2)",
        tickfont = list(color = "#94A3B8")
      ),
      margin = list(l = 70, r = 20, t = 30, b = 80)
    )

  return(fig)
}

#' Create country vs world comparison RADAR chart (Spider Chart)
#' Cyberpunk Scientific - País (#22D3EE Cian Neón) vs Media (#9CA3AF Gris)
#'
#' @param data Filtered country data
#' @param df_ultimo Latest data per country (for world averages)
#' @param pais_nombre Country name
#' @return Plotly figure (scatterpolar radar chart)
create_country_vs_world <- function(data, df_ultimo, pais_nombre) {
  if (is.null(data) || nrow(data) == 0) {
    return(plot_ly() %>%
             layout(paper_bgcolor = "rgba(0,0,0,0)", plot_bgcolor = "rgba(0,0,0,0)"))
  }

  # Get latest data for selected country

ultimo <- data %>% dplyr::slice_max(fecha, n = 1)

  # Define the 5 key metrics for radar
  metrics <- c("IA_100k", "tasa_mortalidad_100k", "letalidad_CFR_pct",
               "gasto_salud_pib", "pib_per_capita_2019")

  # Human-readable labels for radar axes
  labels <- c("Incidencia\n(por 100k)",
              "Mortalidad\n(por 100k)",
              "Letalidad\n(CFR %)",
              "Gasto Salud\n(% PIB)",
              "PIB per\ncápita")

  # ============================================================================
  # NORMALIZE DATA (Min-Max scaling 0-1) using df_ultimo (all countries)
  # ============================================================================
  normalize <- function(x) {
    min_val <- min(x, na.rm = TRUE)
    max_val <- max(x, na.rm = TRUE)
    if (max_val == min_val) return(rep(0.5, length(x)))
    (x - min_val) / (max_val - min_val)
  }

  # Get raw values for country and calculate world average
  pais_raw <- c(
    ultimo$IA_100k,
    ultimo$tasa_mortalidad_100k,
    ultimo$letalidad_CFR_pct,
    ultimo$gasto_salud_pib,
    ultimo$pib_per_capita_2019
  )

  media_raw <- c(
    mean(df_ultimo$IA_100k, na.rm = TRUE),
    mean(df_ultimo$tasa_mortalidad_100k, na.rm = TRUE),
    mean(df_ultimo$letalidad_CFR_pct, na.rm = TRUE),
    mean(df_ultimo$gasto_salud_pib, na.rm = TRUE),
    mean(df_ultimo$pib_per_capita_2019, na.rm = TRUE)
  )

  # Normalize each metric based on global min/max from df_ultimo
  pais_norm <- numeric(5)
  media_norm <- numeric(5)

  for (i in seq_along(metrics)) {
    col_data <- df_ultimo[[metrics[i]]]
    min_val <- min(col_data, na.rm = TRUE)
    max_val <- max(col_data, na.rm = TRUE)

    if (max_val == min_val) {
      pais_norm[i] <- 0.5
      media_norm[i] <- 0.5
    } else {
      pais_norm[i] <- (pais_raw[i] - min_val) / (max_val - min_val)
      media_norm[i] <- (media_raw[i] - min_val) / (max_val - min_val)
    }
  }

  # Close the radar polygon (repeat first value at end)
  pais_norm <- c(pais_norm, pais_norm[1])
  media_norm <- c(media_norm, media_norm[1])
  labels_closed <- c(labels, labels[1])
  pais_raw_closed <- c(pais_raw, pais_raw[1])
  media_raw_closed <- c(media_raw, media_raw[1])

  # ============================================================================
  # CREATE RADAR CHART with Cyberpunk aesthetics
  # ============================================================================
  fig <- plot_ly(type = "scatterpolar") %>%
    # Media Mundial trace (background, less prominent)
    add_trace(
      r = media_norm,
      theta = labels_closed,
      name = "Media Mundial",
      fill = "toself",
      fillcolor = "rgba(156, 163, 175, 0.1)",
      line = list(color = "#9CA3AF", width = 2),
      marker = list(color = "#9CA3AF", size = 6),
      customdata = media_raw_closed,
      hovertemplate = paste0(
        "<b>Media Mundial</b><br>",
        "%{theta}: %{customdata:.2f}<br>",
        "Normalizado: %{r:.2f}<extra></extra>"
      )
    ) %>%
    # País trace (protagonist, vibrant)
    add_trace(
      r = pais_norm,
      theta = labels_closed,
      name = pais_nombre,
      fill = "toself",
      fillcolor = "rgba(34, 211, 238, 0.25)",
      line = list(color = "#22D3EE", width = 3),
      marker = list(color = "#22D3EE", size = 8, line = list(color = "#06B6D4", width = 2)),
      customdata = pais_raw_closed,
      hovertemplate = paste0(
        "<b>", pais_nombre, "</b><br>",
        "%{theta}: %{customdata:.2f}<br>",
        "Normalizado: %{r:.2f}<extra></extra>"
      )
    ) %>%
    layout(
      height = 420,
      paper_bgcolor = "rgba(0,0,0,0)",
      plot_bgcolor = "rgba(0,0,0,0)",
      font = list(color = "#9CA3AF", size = 11),
      polar = list(
        bgcolor = "rgba(0,0,0,0)",
        radialaxis = list(
          visible = TRUE,
          range = c(0, 1),
          tickvals = c(0, 0.25, 0.5, 0.75, 1),
          ticktext = c("0", "0.25", "0.5", "0.75", "1"),
          tickfont = list(color = "#6B7280", size = 9),
          gridcolor = "rgba(55, 65, 81, 0.5)",
          linecolor = "rgba(55, 65, 81, 0.3)",
          tickcolor = "rgba(55, 65, 81, 0.5)"
        ),
        angularaxis = list(
          tickfont = list(color = "#9CA3AF", size = 11),
          linecolor = "rgba(55, 65, 81, 0.5)",
          gridcolor = "rgba(55, 65, 81, 0.4)"
        )
      ),
      legend = list(
        orientation = "h",
        yanchor = "bottom",
        y = -0.35,
        xanchor = "center",
        x = 0.5,
        bgcolor = "rgba(0,0,0,0)",
        bordercolor = "rgba(0,0,0,0)",
        borderwidth = 0,
        font = list(color = "#9CA3AF", size = 11)
      ),
      margin = list(l = 60, r = 60, t = 40, b = 80)
    )

  return(fig)
}

#' Create monthly cases bar chart
#' Cyberpunk Scientific - Turquesa (#06B6D4) con Pico en Amarillo Neón (#0058ca)
#'
#' @param data Filtered country data
#' @return Plotly figure
create_monthly_cases <- function(data) {
  if (is.null(data) || nrow(data) == 0) {
    return(plot_ly() %>%
             layout(paper_bgcolor = "rgba(0,0,0,0)", plot_bgcolor = "rgba(0,0,0,0)"))
  }

  data_mes <- data %>%
    dplyr::mutate(
      mes_num = lubridate::month(fecha),
      mes = lubridate::month(fecha, label = TRUE, abbr = TRUE)
    ) %>%
    dplyr::group_by(mes_num, mes) %>%
    dplyr::summarise(confirmados_dia = sum(confirmados_dia, na.rm = TRUE), .groups = "drop") %>%
    dplyr::arrange(mes_num)

  if (nrow(data_mes) == 0) {
    return(plot_ly() %>%
             layout(paper_bgcolor = "rgba(0,0,0,0)", plot_bgcolor = "rgba(0,0,0,0)"))
  }

  # Detectar el pico y asignar colores
  idx_max <- which.max(data_mes$confirmados_dia)
  # Tonos fríos: Turquesa estándar, Amarillo Neón para el pico
  colores <- rep("#06B6D4", nrow(data_mes))
  colores[idx_max] <- "#0058ca"

  max_val <- max(data_mes$confirmados_dia, na.rm = TRUE)
  mes_pico <- as.character(data_mes$mes[idx_max])

  fig <- plot_ly(
    data = data_mes,
    type = "bar",
    x = ~mes,
    y = ~confirmados_dia,
    marker = list(
      color = colores,
      line = list(color = "rgba(6, 182, 212, 0.5)", width = 1)
    ),
    text = ~ifelse(confirmados_dia >= 1000,
                   sprintf("%.0fk", confirmados_dia / 1000),
                   as.character(as.integer(confirmados_dia))),
    textposition = "outside",
    textfont = list(color = "#94A3B8", size = 11),
    hovertemplate = "<b>%{x}</b><br>Casos: %{y:,.0f}<extra></extra>"
  ) %>%
    layout(
      height = 400,
      paper_bgcolor = "rgba(0,0,0,0)",
      plot_bgcolor = "rgba(0,0,0,0)",
      font = list(color = "#94A3B8", size = 12),
      xaxis = list(
        title = list(text = "Mes", font = list(size = 13, color = "#94A3B8")),
        gridcolor = "rgba(148, 163, 184, 0.1)",
        categoryorder = "array",
        categoryarray = data_mes$mes,
        tickfont = list(color = "#94A3B8")
      ),
      yaxis = list(
        title = list(text = "Nuevos Casos", font = list(size = 13, color = "#94A3B8")),
        gridcolor = "rgba(148, 163, 184, 0.1)",
        tickfont = list(color = "#94A3B8")
      ),
      margin = list(l = 60, r = 20, t = 50, b = 60),
      bargap = 0.3,
      annotations = list(
        list(
          x = mes_pico,
          y = max_val,
          text = "PICO",
          showarrow = FALSE,
          font = list(color = "#0058ca", size = 12, family = "Inter", weight = 700),
          yshift = 25
        )
      )
    )

  return(fig)
}

#' Create monthly deaths bar chart
#' Cyberpunk Scientific - Naranja Quemado (#F97316) con Pico en Rosa Pálido (#ec1c00)
#'
#' @param data Filtered country data
#' @return Plotly figure
create_monthly_deaths <- function(data) {
  if (is.null(data) || nrow(data) == 0) {
    return(plot_ly() %>%
             layout(paper_bgcolor = "rgba(0,0,0,0)", plot_bgcolor = "rgba(0,0,0,0)"))
  }

  data_mes <- data %>%
    dplyr::mutate(
      mes_num = lubridate::month(fecha),
      mes = lubridate::month(fecha, label = TRUE, abbr = TRUE)
    ) %>%
    dplyr::group_by(mes_num, mes) %>%
    dplyr::summarise(muertes_dia = sum(muertes_dia, na.rm = TRUE), .groups = "drop") %>%
    dplyr::arrange(mes_num)

  if (nrow(data_mes) == 0) {
    return(plot_ly() %>%
             layout(paper_bgcolor = "rgba(0,0,0,0)", plot_bgcolor = "rgba(0,0,0,0)"))
  }

  # Detectar el pico y asignar colores
  idx_max <- which.max(data_mes$muertes_dia)
  # Tonos cálidos (Alerta): Naranja estándar, Rosa Pálido para máximo contraste en el pico
  colores <- rep("#F97316", nrow(data_mes))
  colores[idx_max] <- "#ec1c00"

  max_val <- max(data_mes$muertes_dia, na.rm = TRUE)
  mes_pico <- as.character(data_mes$mes[idx_max])

  fig <- plot_ly(
    data = data_mes,
    type = "bar",
    x = ~mes,
    y = ~muertes_dia,
    marker = list(
      color = colores,
      line = list(color = "rgba(249, 115, 22, 0.5)", width = 1)
    ),
    text = ~ifelse(muertes_dia >= 1000,
                   sprintf("%.0fk", muertes_dia / 1000),
                   as.character(as.integer(muertes_dia))),
    textposition = "outside",
    textfont = list(color = "#94A3B8", size = 11),
    hovertemplate = "<b>%{x}</b><br>Muertes: %{y:,.0f}<extra></extra>"
  ) %>%
    layout(
      height = 400,
      paper_bgcolor = "rgba(0,0,0,0)",
      plot_bgcolor = "rgba(0,0,0,0)",
      font = list(color = "#94A3B8", size = 12),
      xaxis = list(
        title = list(text = "Mes", font = list(size = 13, color = "#94A3B8")),
        gridcolor = "rgba(148, 163, 184, 0.1)",
        categoryorder = "array",
        categoryarray = data_mes$mes,
        tickfont = list(color = "#94A3B8")
      ),
      yaxis = list(
        title = list(text = "Muertes", font = list(size = 13, color = "#94A3B8")),
        gridcolor = "rgba(148, 163, 184, 0.1)",
        tickfont = list(color = "#94A3B8")
      ),
      margin = list(l = 60, r = 20, t = 50, b = 60),
      bargap = 0.3,
      annotations = list(
        list(
          x = mes_pico,
          y = max_val,
          text = "PICO",
          showarrow = FALSE,
          font = list(color = "#ec1c00", size = 12, family = "Inter", weight = 700),
          yshift = 25
        )
      )
    )

  return(fig)
}

#' Generate peak relationship message
#' Cyberpunk Scientific - Colores semánticos para relaciones de picos
#'
#' @param data Filtered country data
#' @return HTML string with message
generate_peak_message <- function(data) {
  if (is.null(data) || nrow(data) == 0) {
    return("")
  }

  data_mes <- data %>%
    dplyr::mutate(
      mes_num = lubridate::month(fecha),
      mes = lubridate::month(fecha, label = TRUE, abbr = TRUE)
    ) %>%
    dplyr::group_by(mes_num, mes) %>%
    dplyr::summarise(
      confirmados_dia = sum(confirmados_dia, na.rm = TRUE),
      muertes_dia = sum(muertes_dia, na.rm = TRUE),
      .groups = "drop"
    ) %>%
    dplyr::arrange(mes_num)

  if (nrow(data_mes) == 0) return("")

  idx_max_casos <- which.max(data_mes$confirmados_dia)
  idx_max_muertes <- which.max(data_mes$muertes_dia)

  mes_casos <- as.character(data_mes$mes[idx_max_casos])
  mes_muertes <- as.character(data_mes$mes[idx_max_muertes])

  diff <- idx_max_muertes - idx_max_casos

  # Semántica de colores cyberpunk
  if (diff == 0) {
    texto <- sprintf("Casos y muertes alcanzaron su pico en el mismo mes: %s", mes_casos)
    color <- "#22D3EE"  # Cian Neón - Sincronización
    bg_gradient <- "rgba(34, 211, 238, 0.1)"
    border_color <- "rgba(34, 211, 238, 0.3)"
  } else if (diff > 0) {
    texto <- sprintf("El pico de muertes (%s) ocurrio %d mes(es) DESPUES del pico de casos (%s)",
                     mes_muertes, diff, mes_casos)
    color <- "#F97316"  # Naranja Quemado - Alerta (Retraso)
    bg_gradient <- "rgba(249, 115, 22, 0.1)"
    border_color <- "rgba(249, 115, 22, 0.3)"
  } else {
    texto <- sprintf("El pico de muertes (%s) ocurrio %d mes(es) ANTES del pico de casos (%s)",
                     mes_muertes, abs(diff), mes_casos)
    color <- "#3B82F6"  # Azul Real - Información (Anticipación)
    bg_gradient <- "rgba(59, 130, 246, 0.1)"
    border_color <- "rgba(59, 130, 246, 0.3)"
  }

  html <- sprintf('
    <div style="
      background: linear-gradient(90deg, %s, %s);
      border: 1px solid %s;
      border-radius: 12px;
      padding: 15px 30px;
      display: inline-block;
      font-size: 15px;
      color: %s;
      font-weight: 600;
      font-family: Inter, sans-serif;
      letter-spacing: 0.3px;
    ">
      %s
    </div>
  ', bg_gradient, bg_gradient, border_color, color, texto)

  return(html)
}
