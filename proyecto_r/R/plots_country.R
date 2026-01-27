# ==============================================================================
# COUNTRY PAGE CHART FUNCTIONS
# ==============================================================================

#' Create temporal evolution line chart
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

  fig <- plot_ly(
    data = data_mes,
    type = "scatter",
    mode = "lines+markers",
    x = ~mes,
    y = ~confirmados,
    line = list(color = "#6366f1", width = 3),
    marker = list(color = "#6366f1", size = 10, line = list(color = "#818cf8", width = 2)),
    hovertemplate = "<b>%{x}</b><br>Casos: %{y:,.0f}<extra></extra>"
  ) %>%
    layout(
      height = 400,
      paper_bgcolor = "rgba(0,0,0,0)",
      plot_bgcolor = "rgba(0,0,0,0)",
      font = list(color = "rgba(255,255,255,0.9)", size = 12),
      xaxis = list(
        title = list(text = "Mes", font = list(size = 13)),
        gridcolor = "rgba(255,255,255,0.1)",
        tickangle = -45,
        showline = TRUE,
        linecolor = "rgba(99,102,241,0.3)"
      ),
      yaxis = list(
        title = list(text = "Casos Acumulados", font = list(size = 13)),
        gridcolor = "rgba(255,255,255,0.1)",
        showline = TRUE,
        linecolor = "rgba(99,102,241,0.3)"
      ),
      margin = list(l = 70, r = 20, t = 30, b = 80)
    )

  return(fig)
}

#' Create country vs world comparison bar chart
#'
#' @param data Filtered country data
#' @param df_ultimo Latest data per country (for world averages)
#' @param pais_nombre Country name
#' @return Plotly figure
create_country_vs_world <- function(data, df_ultimo, pais_nombre) {
  if (is.null(data) || nrow(data) == 0) {
    return(plot_ly() %>%
             layout(paper_bgcolor = "rgba(0,0,0,0)", plot_bgcolor = "rgba(0,0,0,0)"))
  }

  ultimo <- data %>% dplyr::slice_max(fecha, n = 1)

  # Country metrics (normalized for comparison)
  pais_letalidad <- ultimo$letalidad_CFR_pct
  pais_incidencia <- ultimo$IA_100k / 100
  pais_mortalidad <- ultimo$tasa_mortalidad_100k / 10
  pais_gasto_salud <- ultimo$gasto_salud_pib

  # World averages
  media_letalidad <- mean(df_ultimo$letalidad_CFR_pct, na.rm = TRUE)
  media_incidencia <- mean(df_ultimo$IA_100k, na.rm = TRUE) / 100
  media_mortalidad <- mean(df_ultimo$tasa_mortalidad_100k, na.rm = TRUE) / 10
  media_gasto_salud <- mean(df_ultimo$gasto_salud_pib, na.rm = TRUE)

  categorias <- c("Letalidad (%)", "Incidencia/100k", "Mort./100k", "Gasto Salud (%)")
  valores_pais <- c(pais_letalidad, pais_incidencia, pais_mortalidad, pais_gasto_salud)
  valores_media <- c(media_letalidad, media_incidencia, media_mortalidad, media_gasto_salud)

  fig <- plot_ly() %>%
    add_trace(
      type = "bar",
      x = categorias,
      y = valores_pais,
      name = pais_nombre,
      marker = list(color = "#6366f1", line = list(color = "#818cf8", width = 2)),
      text = c(
        sprintf("%.2f%%", pais_letalidad),
        formatC(ultimo$IA_100k, format = "f", digits = 0, big.mark = ","),
        formatC(ultimo$tasa_mortalidad_100k, format = "f", digits = 0, big.mark = ","),
        sprintf("%.1f%%", pais_gasto_salud)
      ),
      textposition = "outside",
      textfont = list(color = "#818cf8", size = 11)
    ) %>%
    add_trace(
      type = "bar",
      x = categorias,
      y = valores_media,
      name = "Media Mundial",
      marker = list(color = "#a855f7", line = list(color = "#c084fc", width = 2)),
      text = c(
        sprintf("%.2f%%", media_letalidad),
        formatC(mean(df_ultimo$IA_100k, na.rm = TRUE), format = "f", digits = 0, big.mark = ","),
        formatC(mean(df_ultimo$tasa_mortalidad_100k, na.rm = TRUE), format = "f", digits = 0, big.mark = ","),
        sprintf("%.1f%%", media_gasto_salud)
      ),
      textposition = "outside",
      textfont = list(color = "#c084fc", size = 11)
    ) %>%
    layout(
      barmode = "group",
      height = 400,
      paper_bgcolor = "rgba(0,0,0,0)",
      plot_bgcolor = "rgba(0,0,0,0)",
      font = list(color = "rgba(255,255,255,0.8)"),
      xaxis = list(
        gridcolor = "rgba(255,255,255,0.1)",
        tickangle = 0
      ),
      yaxis = list(
        title = list(text = "Valor (normalizado)", font = list(size = 11)),
        gridcolor = "rgba(255,255,255,0.1)",
        showticklabels = FALSE
      ),
      legend = list(
        orientation = "h",
        yanchor = "bottom",
        y = 1.02,
        xanchor = "center",
        x = 0.5,
        bgcolor = "rgba(20,20,50,0.7)",
        bordercolor = "rgba(99,102,241,0.3)",
        borderwidth = 1
      ),
      margin = list(l = 40, r = 20, t = 60, b = 60),
      bargap = 0.3
    )

  return(fig)
}

#' Create monthly cases bar chart
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

  idx_max <- which.max(data_mes$confirmados_dia)
  colores <- rep("#a855f7", nrow(data_mes))
  colores[idx_max] <- "#22c55e"

  max_val <- max(data_mes$confirmados_dia, na.rm = TRUE)
  mes_pico <- as.character(data_mes$mes[idx_max])

  fig <- plot_ly(
    data = data_mes,
    type = "bar",
    x = ~mes,
    y = ~confirmados_dia,
    marker = list(
      color = colores,
      line = list(color = "#c084fc", width = 1)
    ),
    text = ~ifelse(confirmados_dia >= 1000,
                   sprintf("%.0fk", confirmados_dia / 1000),
                   as.character(as.integer(confirmados_dia))),
    textposition = "outside",
    textfont = list(color = "rgba(255,255,255,0.95)", size = 11),
    hovertemplate = "<b>%{x}</b><br>Casos: %{y:,.0f}<extra></extra>"
  ) %>%
    layout(
      height = 400,
      paper_bgcolor = "rgba(0,0,0,0)",
      plot_bgcolor = "rgba(0,0,0,0)",
      font = list(color = "rgba(255,255,255,0.9)", size = 12),
      xaxis = list(
        title = list(text = "Mes", font = list(size = 13)),
        gridcolor = "rgba(255,255,255,0.05)",
        categoryorder = "array",
        categoryarray = data_mes$mes
      ),
      yaxis = list(
        title = list(text = "Nuevos Casos", font = list(size = 13)),
        gridcolor = "rgba(255,255,255,0.1)"
      ),
      margin = list(l = 60, r = 20, t = 50, b = 60),
      bargap = 0.3,
      annotations = list(
        list(
          x = mes_pico,
          y = max_val,
          text = "PICO",
          showarrow = FALSE,
          font = list(color = "#22c55e", size = 12, family = "Inter"),
          yshift = 25
        )
      )
    )

  return(fig)
}

#' Create monthly deaths bar chart
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

  idx_max <- which.max(data_mes$muertes_dia)
  colores <- rep("#ef4444", nrow(data_mes))
  colores[idx_max] <- "#f97316"

  max_val <- max(data_mes$muertes_dia, na.rm = TRUE)
  mes_pico <- as.character(data_mes$mes[idx_max])

  fig <- plot_ly(
    data = data_mes,
    type = "bar",
    x = ~mes,
    y = ~muertes_dia,
    marker = list(
      color = colores,
      line = list(color = "#fca5a5", width = 1)
    ),
    text = ~ifelse(muertes_dia >= 1000,
                   sprintf("%.0fk", muertes_dia / 1000),
                   as.character(as.integer(muertes_dia))),
    textposition = "outside",
    textfont = list(color = "rgba(255,255,255,0.95)", size = 11),
    hovertemplate = "<b>%{x}</b><br>Muertes: %{y:,.0f}<extra></extra>"
  ) %>%
    layout(
      height = 400,
      paper_bgcolor = "rgba(0,0,0,0)",
      plot_bgcolor = "rgba(0,0,0,0)",
      font = list(color = "rgba(255,255,255,0.9)", size = 12),
      xaxis = list(
        title = list(text = "Mes", font = list(size = 13)),
        gridcolor = "rgba(255,255,255,0.05)",
        categoryorder = "array",
        categoryarray = data_mes$mes
      ),
      yaxis = list(
        title = list(text = "Muertes", font = list(size = 13)),
        gridcolor = "rgba(255,255,255,0.1)"
      ),
      margin = list(l = 60, r = 20, t = 50, b = 60),
      bargap = 0.3,
      annotations = list(
        list(
          x = mes_pico,
          y = max_val,
          text = "PICO",
          showarrow = FALSE,
          font = list(color = "#f97316", size = 12, family = "Inter"),
          yshift = 25
        )
      )
    )

  return(fig)
}

#' Generate peak relationship message
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

  if (diff == 0) {
    texto <- sprintf("Casos y muertes alcanzaron su pico en el mismo mes: %s", mes_casos)
    color <- "#22c55e"
  } else if (diff > 0) {
    texto <- sprintf("El pico de muertes (%s) ocurrio %d mes(es) DESPUES del pico de casos (%s)",
                     mes_muertes, diff, mes_casos)
    color <- "#f97316"
  } else {
    texto <- sprintf("El pico de muertes (%s) ocurrio %d mes(es) ANTES del pico de casos (%s)",
                     mes_muertes, abs(diff), mes_casos)
    color <- "#3b82f6"
  }

  html <- sprintf('
    <div style="
      background: linear-gradient(90deg, rgba(99,102,241,0.2), rgba(168,85,247,0.2));
      border: 1px solid rgba(168,85,247,0.4);
      border-radius: 12px;
      padding: 15px 30px;
      display: inline-block;
      font-size: 15px;
      color: %s;
      font-weight: 500;
    ">
      %s
    </div>
  ', color, texto)

  return(html)
}
