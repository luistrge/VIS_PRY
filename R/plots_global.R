# ==============================================================================
# GLOBAL PAGE CHART FUNCTIONS
# ==============================================================================

#' Create choropleth map (animated by week)
#'
#' @param df COVID data frame
#' @return Plotly figure
create_choropleth_map <- function(df) {
  # 1. Prepare data using the helper function
  data_map <- aggregate_weekly(df) %>%
    dplyr::filter(!is.na(iso3c) & iso3c != "") %>%
    # Safety check: Replace Infinite or NaN values to prevent rendering errors
    dplyr::mutate(IA_100k_semanal = ifelse(is.finite(IA_100k_semanal), IA_100k_semanal, 0))

  # CRITICAL: Complete all combinations of countries and weeks
  # This ensures animation frames work correctly
  data_map <- data_map %>%
    tidyr::complete(
      iso3c, semana_str,
      fill = list(IA_100k_semanal = 0, pais = NA)
    ) %>%
    dplyr::arrange(semana_str, iso3c)

  # Fill missing country names
  country_mapping <- data_map %>%
    dplyr::filter(!is.na(pais)) %>%
    dplyr::select(iso3c, pais) %>%
    dplyr::distinct()

  data_map <- data_map %>%
    dplyr::left_join(country_mapping, by = "iso3c", suffix = c("", ".y")) %>%
    dplyr::mutate(pais = dplyr::coalesce(pais, pais.y)) %>%
    dplyr::select(-pais.y)

  # 3. Calculate max scale (robust)
  max_incidencia <- quantile(data_map$IA_100k_semanal, 0.95, na.rm = TRUE)
  if (is.na(max_incidencia) || max_incidencia == 0) max_incidencia <- 100

  # 4. Use Plasma colorscale (purple to yellow) - matches dark theme
  # Plasma is a vibrant, perceptually uniform colorscale

  # 5. Create Animated Map
  # NOTE: In R Plotly, %{frame} doesn't work in hovertemplate for choropleth.
  # Use customdata to pass the week info for hover display.
  # CRITICAL: redraw = TRUE is required for choropleth animations to update properly
  fig <- plot_geo(data_map) %>%
    add_trace(
      type = "choropleth",
      locations = ~iso3c,
      z = ~IA_100k_semanal,
      text = ~pais,
      customdata = ~semana_str,
      frame = ~semana_str, # Animation Frame
      colorscale = "Plasma",
      zmin = 0,
      zmax = max_incidencia,
      marker = list(line = list(color = "rgba(240,240,240,0.25)", width = 0.5)),
      colorbar = list(
        title = list(text = "Incidencia<br>Semanal/100k", font = list(size = 11, color = "white")),
        thickness = 18,
        len = 0.75,
        x = 0.98,
        bgcolor = "rgba(0,0,0,0)",
        bordercolor = "rgba(0,0,0,0)",
        borderwidth = 1,
        tickfont = list(color = "rgba(255,255,255,0.9)", size = 10),
        tickcolor = "rgba(255,255,255,0.5)"
      ),
      hovertemplate = "<b>%{text}</b><br>Semana: %{customdata}<br>Incidencia: %{z:,.1f}/100k<extra></extra>"
    ) %>%
    layout(
      geo = list(
        showframe = FALSE,
        showcoastlines = TRUE,
        coastlinecolor = "#030d1b",
        coastlinewidth = 0.5,
        projection = list(type = "natural earth"),
        bgcolor = "rgba(0,0,0,0)",
        landcolor = "#1a1f3a",
        showland = TRUE,
        oceancolor = "#030d1b",
        showocean = TRUE,
        showcountries = TRUE,
        countrycolor = "rgba(200,200,200,0.15)",
        countrywidth = 0.3
      ),
      height = 550,
      paper_bgcolor = "rgba(0,0,0,0)",
      plot_bgcolor = "rgba(0,0,0,0)",
      font = list(color = "rgba(255,255,255,0.9)"),
      margin = list(l = 80, r = 80, t = 10, b = 200) # Bottom margin for slider
    ) %>%
    # 6. Explicitly Style Animation Controls (White Text & Visible Buttons)
    # CRITICAL: redraw = TRUE is required for choropleth maps to animate properly
    animation_opts(
      frame = 500,
      transition = 300,
      redraw = TRUE
    ) %>%
    animation_slider(
      currentvalue = list(
        prefix = "Semana: ",
        font = list(color = "white", size = 14)
      ),
      font = list(color = "white"),
      bgcolor = "rgba(3, 13, 27, 0.9)",
      bordercolor = "rgba(3, 13, 27, 0.9)",
      tickcolor = "rgba(255,255,255,0.7)"
    ) %>%
    animation_button(
      x = 0.02, xanchor = "left", y = 0, yanchor = "top",
      label = "Play",
      font = list(color = "white"),
      bgcolor = "rgba(99,102,241,0.8)",
      bordercolor = "rgba(255,255,255,0.4)"
    )

  return(fig)
}

#' Create ridgeline plot (wave comparison)
#'
#' @param df COVID data frame
#' @param selected_countries Vector of country names
#' @return Plotly figure
create_ridgeline_plot <- function(df, selected_countries) {
  if (is.null(selected_countries) || length(selected_countries) == 0) {
    return(plot_ly() %>%
      layout(paper_bgcolor = "rgba(0,0,0,0)", plot_bgcolor = "rgba(0,0,0,0)"))
  }

  # Aggregate by week
  data <- df %>%
    dplyr::filter(pais %in% selected_countries) %>%
    dplyr::mutate(semana = lubridate::floor_date(fecha, "week")) %>%
    dplyr::group_by(pais, semana) %>%
    dplyr::summarise(confirmados_dia = sum(confirmados_dia, na.rm = TRUE), .groups = "drop")

  # Normalize by country
  data <- data %>%
    dplyr::group_by(pais) %>%
    dplyr::mutate(
      max_val = max(confirmados_dia, na.rm = TRUE),
      confirmados_norm = confirmados_dia / dplyr::if_else(max_val == 0, 1, max_val)
    ) %>%
    dplyr::ungroup()

  # Create ridgeline
  fig <- plot_ly()

  countries <- rev(selected_countries)
  colors <- c("#66c2a5", "#fc8d62", "#8da0cb", "#e78ac3", "#a6d854", "#ffd92f", "#e5c494", "#b3b3b3")

  for (i in seq_along(countries)) {
    country_data <- data %>%
      dplyr::filter(pais == countries[i]) %>%
      dplyr::arrange(semana)

    if (nrow(country_data) == 0) next

    offset <- (i - 1) * 1.0
    x_vals <- c(country_data$semana, rev(country_data$semana))
    y_vals <- c(country_data$confirmados_norm + offset, rep(offset, nrow(country_data)))

    color_idx <- ((i - 1) %% length(colors)) + 1
    fill_color <- paste0(colors[color_idx], "66")

    fig <- fig %>%
      add_trace(
        type = "scatter",
        mode = "lines",
        x = x_vals,
        y = y_vals,
        fill = "toself",
        fillcolor = fill_color,
        line = list(color = colors[color_idx], width = 1.5),
        name = countries[i],
        hovertemplate = paste0("<b>", countries[i], "</b><br>Semana: %{x}<extra></extra>")
      )
  }

  fig <- fig %>%
    layout(
      height = 450,
      paper_bgcolor = "rgba(0,0,0,0)",
      plot_bgcolor = "rgba(0,0,0,0)",
      font = list(color = "rgba(255,255,255,0.8)"),
      showlegend = TRUE,
      legend = list(
        orientation = "h",
        yanchor = "bottom",
        y = 1.02,
        xanchor = "center",
        x = 0.5,
        bgcolor = "rgba(0,0,0,0)",
        bordercolor = "rgba(0,0,0,0)",
        borderwidth = 0
      ),
      xaxis = list(
        title = list(text = "Tiempo", font = list(size = 13, color = "rgba(255,255,255,0.9)")),
        gridcolor = "rgba(255,255,255,0.1)",
        showline = TRUE,
        linecolor = "rgba(99,102,241,0.3)"
      ),
      yaxis = list(
        title = list(text = "Intensidad (normalizado)", font = list(size = 13, color = "rgba(255,255,255,0.9)")),
        gridcolor = "rgba(255,255,255,0.05)",
        showticklabels = FALSE
      ),
      margin = list(l = 60, r = 30, t = 50, b = 60)
    )

  return(fig)
}

#' Create dumbbell chart (incidence growth)
#'
#' @param df COVID data frame
#' @param selected_countries Vector of country names
#' @param fecha_inicio Start date
#' @param fecha_fin End date
#' @return Plotly figure
create_dumbbell_chart <- function(df, selected_countries, fecha_inicio, fecha_fin) {
  if (is.null(selected_countries) || length(selected_countries) == 0) {
    return(plot_ly() %>%
      layout(paper_bgcolor = "rgba(0,0,0,0)", plot_bgcolor = "rgba(0,0,0,0)"))
  }

  data <- df %>%
    dplyr::filter(
      pais %in% selected_countries,
      fecha >= fecha_inicio,
      fecha <= fecha_fin
    )

  # Get start and end values per country
  data_inicio <- data %>%
    dplyr::group_by(pais) %>%
    dplyr::slice_min(fecha, n = 1) %>%
    dplyr::select(pais, IA_100k_inicio = IA_100k, fecha_inicio = fecha) %>%
    dplyr::ungroup()

  data_fin <- data %>%
    dplyr::group_by(pais) %>%
    dplyr::slice_max(fecha, n = 1) %>%
    dplyr::select(pais, IA_100k_fin = IA_100k, fecha_fin = fecha) %>%
    dplyr::ungroup()

  data_dumbbell <- data_inicio %>%
    dplyr::inner_join(data_fin, by = "pais") %>%
    dplyr::mutate(incremento = IA_100k_fin - IA_100k_inicio) %>%
    dplyr::arrange(IA_100k_fin)

  if (nrow(data_dumbbell) == 0) {
    return(plot_ly() %>%
      layout(paper_bgcolor = "rgba(0,0,0,0)", plot_bgcolor = "rgba(0,0,0,0)"))
  }

  fig <- plot_ly()

  # Add lines
  for (i in 1:nrow(data_dumbbell)) {
    row <- data_dumbbell[i, ]
    fig <- fig %>%
      add_trace(
        type = "scatter",
        mode = "lines",
        x = c(row$IA_100k_inicio, row$IA_100k_fin),
        y = c(row$pais, row$pais),
        line = list(color = "rgba(148,163,184,0.6)", width = 2),
        showlegend = FALSE,
        hoverinfo = "skip"
      )
  }

  # Add start markers
  fig <- fig %>%
    add_trace(
      type = "scatter",
      mode = "markers",
      x = data_dumbbell$IA_100k_inicio,
      y = data_dumbbell$pais,
      marker = list(
        color = "#10b981",
        size = 12,
        line = list(color = "white", width = 1)
      ),
      name = "Inicio",
      hovertemplate = "<b>%{y}</b><br>Incidencia Inicio: %{x:.1f}/100k<extra></extra>"
    )

  # Add end markers
  fig <- fig %>%
    add_trace(
      type = "scatter",
      mode = "markers",
      x = data_dumbbell$IA_100k_fin,
      y = data_dumbbell$pais,
      marker = list(
        color = "#ef4444",
        size = 12,
        line = list(color = "white", width = 1)
      ),
      name = "Fin",
      hovertemplate = "<b>%{y}</b><br>Incidencia Final: %{x:.1f}/100k<extra></extra>"
    )

  fig <- fig %>%
    layout(
      height = 450,
      paper_bgcolor = "rgba(0,0,0,0)",
      plot_bgcolor = "rgba(0,0,0,0)",
      font = list(color = "rgba(255,255,255,0.8)"),
      showlegend = TRUE,
      legend = list(
        orientation = "h",
        yanchor = "bottom",
        y = 1.02,
        xanchor = "center",
        x = 0.5,
        bgcolor = "rgba(0,0,0,0)",
        bordercolor = "rgba(0,0,0,0)",
        borderwidth = 0
      ),
      xaxis = list(
        title = "Incidencia Acumulada (por 100k)",
        gridcolor = "rgba(255,255,255,0.1)",
        showline = TRUE,
        linecolor = "rgba(99,102,241,0.3)"
      ),
      yaxis = list(
        gridcolor = "rgba(255,255,255,0.05)",
        tickfont = list(size = 10),
        categoryorder = "array",
        categoryarray = data_dumbbell$pais
      ),
      margin = list(l = 100, r = 30, t = 50, b = 60)
    )

  return(fig)
}

#' Create health spending vs lethality scatter
#'
#' @param df_ultimo Latest data per country
#' @return Plotly figure
create_health_lethality_scatter <- function(df_ultimo) {
  data <- df_ultimo %>%
    dplyr::filter(gasto_salud_pib > 0, !is.na(letalidad_CFR_pct))

  if (nrow(data) == 0) {
    return(plot_ly() %>%
      layout(paper_bgcolor = "rgba(0,0,0,0)", plot_bgcolor = "rgba(0,0,0,0)"))
  }

  # Calculate bubble sizes
  max_pop <- max(data$poblacion, na.rm = TRUE)
  data <- data %>%
    dplyr::mutate(size = (poblacion / max_pop * 40) + 5)

  fig <- plot_ly(
    data = data,
    type = "scatter",
    mode = "markers",
    x = ~gasto_salud_pib,
    y = ~letalidad_CFR_pct,
    marker = list(
      size = ~size,
      color = ~pib_per_capita_2019,
      colorscale = list(
        list(0, "#10b981"),
        list(0.5, "#fbbf24"),
        list(1, "#ef4444")
      ),
      opacity = 0.7,
      line = list(width = 1, color = "rgba(255,255,255,0.3)"),
      colorbar = list(
        title = list(text = "PIB per<br>cápita", font = list(size = 10, color = "white")),
        thickness = 15,
        len = 0.6,
        bgcolor = "rgba(0,0,0,0)",
        bordercolor = "rgba(0,0,0,0)",
        tickfont = list(color = "rgba(255,255,255,0.8)", size = 9)
      ),
      sizemode = "diameter"
    ),
    text = ~pais,
    hovertemplate = "<b>%{text}</b><br>Gasto Salud: %{x:.1f}% PIB<br>Letalidad: %{y:.2f}%<extra></extra>"
  ) %>%
    layout(
      height = 450,
      paper_bgcolor = "rgba(0,0,0,0)",
      plot_bgcolor = "rgba(0,0,0,0)",
      font = list(color = "rgba(255,255,255,0.9)", size = 12),
      xaxis = list(
        title = list(text = "Gasto Salud (%PIB)", font = list(size = 13)),
        gridcolor = "rgba(255,255,255,0.1)",
        showline = TRUE,
        linecolor = "rgba(99,102,241,0.3)"
      ),
      yaxis = list(
        title = list(text = "Letalidad (%)", font = list(size = 13)),
        gridcolor = "rgba(255,255,255,0.1)",
        showline = TRUE,
        linecolor = "rgba(99,102,241,0.3)"
      ),
      margin = list(l = 60, r = 30, t = 20, b = 50)
    )

  return(fig)
}

#' Create efficiency matrix (quadrant scatter)
#'
#' @param df_ultimo Latest data per country
#' @param selected_countries Vector of country names (optional filter)
#' @return Plotly figure
create_efficiency_matrix <- function(df_ultimo, selected_countries = NULL) {
  data <- df_ultimo %>%
    dplyr::filter(gasto_salud_pib > 0, IA_100k > 0, !is.na(letalidad_CFR_pct))

  if (!is.null(selected_countries) && length(selected_countries) > 0) {
    data <- data %>% dplyr::filter(pais %in% selected_countries)
  }

  if (nrow(data) == 0) {
    return(plot_ly() %>%
      layout(paper_bgcolor = "rgba(0,0,0,0)", plot_bgcolor = "rgba(0,0,0,0)"))
  }

  median_incidencia <- median(data$IA_100k, na.rm = TRUE)
  median_letalidad <- median(data$letalidad_CFR_pct, na.rm = TRUE)
  max_pop <- max(data$poblacion, na.rm = TRUE)

  data <- data %>%
    dplyr::mutate(size = (poblacion / max_pop * 40) + 5)

  fig <- plot_ly(
    data = data,
    type = "scatter",
    mode = "markers",
    x = ~IA_100k,
    y = ~letalidad_CFR_pct,
    marker = list(
      size = ~size,
      color = ~gasto_salud_pib,
      colorscale = "Viridis",
      opacity = 0.7,
      line = list(width = 1, color = "rgba(255,255,255,0.3)"),
      colorbar = list(
        title = list(text = "Gasto Salud<br>(% PIB)", font = list(size = 10, color = "white")),
        thickness = 15,
        len = 0.6,
        bgcolor = "rgba(0,0,0,0)",
        bordercolor = "rgba(0,0,0,0)",
        tickfont = list(color = "rgba(255,255,255,0.8)", size = 9)
      ),
      sizemode = "diameter"
    ),
    text = ~pais,
    hovertemplate = paste0(
      "<b>%{text}</b><br>",
      "Incidencia: %{x:.1f}/100k<br>",
      "Letalidad: %{y:.2f}%<extra></extra>"
    )
  ) %>%
    layout(
      height = 450,
      paper_bgcolor = "rgba(0,0,0,0)",
      plot_bgcolor = "rgba(0,0,0,0)",
      font = list(color = "rgba(255,255,255,0.8)", size = 10),
      xaxis = list(
        title = list(text = "Incidencia (por 100k)", font = list(size = 13)),
        gridcolor = "rgba(255,255,255,0.1)",
        showline = TRUE,
        linecolor = "rgba(99,102,241,0.3)"
      ),
      yaxis = list(
        title = list(text = "Letalidad (%)", font = list(size = 13)),
        gridcolor = "rgba(255,255,255,0.1)",
        showline = TRUE,
        linecolor = "rgba(99,102,241,0.3)"
      ),
      shapes = list(
        # Horizontal median line
        list(
          type = "line",
          x0 = 0, x1 = 1, xref = "paper",
          y0 = median_letalidad, y1 = median_letalidad,
          line = list(color = "rgba(255,255,255,0.4)", width = 1, dash = "dash")
        ),
        # Vertical median line
        list(
          type = "line",
          y0 = 0, y1 = 1, yref = "paper",
          x0 = median_incidencia, x1 = median_incidencia,
          line = list(color = "rgba(255,255,255,0.4)", width = 1, dash = "dash")
        )
      ),
      annotations = list(
        list(
          x = median_incidencia,
          y = max(data$letalidad_CFR_pct, na.rm = TRUE) * 0.95,
          text = sprintf("Mediana: %.0f", median_incidencia),
          showarrow = FALSE,
          font = list(size = 9, color = "rgba(255,255,255,0.6)"),
          xshift = 40
        ),
        list(
          x = max(data$IA_100k, na.rm = TRUE) * 0.95,
          y = median_letalidad,
          text = sprintf("Mediana: %.2f%%", median_letalidad),
          showarrow = FALSE,
          font = list(size = 9, color = "rgba(255,255,255,0.6)"),
          yshift = 12
        )
      ),
      margin = list(l = 60, r = 30, t = 20, b = 50)
    )

  return(fig)
}
