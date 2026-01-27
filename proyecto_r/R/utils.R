# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

#' Format numbers in human-readable format
#'
#' Converts large numbers to abbreviated format (1.2M, 3.5K, etc.)
#' Matches the Python fmt() function from app.py
#'
#' @param n Numeric value to format
#' @return Character string with formatted number
#' @examples
#' fmt_number(1234) # "1.2K"
#' fmt_number(1234567) # "1.23M"
#' fmt_number(1234567890) # "1.23B"
fmt_number <- function(n) {
  dplyr::case_when(
    n >= 1e9 ~ sprintf("%.2fB", n / 1e9),
    n >= 1e6 ~ sprintf("%.2fM", n / 1e6),
    n >= 1e3 ~ sprintf("%.1fK", n / 1e3),
    TRUE ~ formatC(n, format = "f", digits = 0, big.mark = ",")
  )
}

# ==============================================================================
# DATA HELPERS (DATASET ALREADY CLEAN)
# ==============================================================================

#' Load COVID-19 data from CSV file (already processed/clean)
#'
#' @param file_path Path to the CSV file
#' @return Data frame with COVID data
load_covid_data <- function(file_path) {
  readr::read_csv(
    file_path,
    col_types = readr::cols(
      iso3c = readr::col_character(),
      pais = readr::col_character(),
      fecha = readr::col_date(format = ""),
      poblacion = readr::col_double(),
      confirmados = readr::col_double(),
      muertes = readr::col_double(),
      IA_100k = readr::col_double(),
      tasa_mortalidad_100k = readr::col_double(),
      letalidad_CFR_pct = readr::col_double(),
      confirmados_dia = readr::col_double(),
      muertes_dia = readr::col_double(),
      IA_100k_dia = readr::col_double(),
      tasa_mortalidad_100k_dia = readr::col_double(),
      letalidad_CFR_pct_dia = readr::col_double(),
      pib_per_capita_2019 = readr::col_double(),
      gasto_salud_pib = readr::col_double()
    ),
    show_col_types = FALSE
  )
}

#' Get latest data per country
get_latest_by_country <- function(df) {
  df %>%
    dplyr::group_by(pais) %>%
    dplyr::slice_max(fecha, n = 1, with_ties = FALSE) %>%
    dplyr::ungroup()
}

#' Get sorted list of countries
get_country_list <- function(df) {
  df %>%
    dplyr::pull(pais) %>%
    unique() %>%
    sort()
}

#' Aggregate data by week for choropleth animation
aggregate_weekly <- function(df) {
  df %>%
    dplyr::mutate(semana = lubridate::floor_date(fecha, "week")) %>%
    dplyr::group_by(pais, iso3c, semana) %>%
    dplyr::summarise(
      confirmados_dia = sum(confirmados_dia, na.rm = TRUE),
      muertes_dia = sum(muertes_dia, na.rm = TRUE),
      confirmados = max(confirmados, na.rm = TRUE),
      muertes = max(muertes, na.rm = TRUE),
      letalidad_CFR_pct = mean(letalidad_CFR_pct, na.rm = TRUE),
      poblacion = mean(poblacion, na.rm = TRUE),
      .groups = "drop"
    ) %>%
    dplyr::mutate(
      IA_100k_semanal = (confirmados_dia / poblacion) * 100000,
      semana_str = format(semana, "%Y-%m-%d")
    ) %>%
    dplyr::arrange(semana_str)
}

#' Normalize values by country
normalize_by_country <- function(df, value_col) {
  df %>%
    dplyr::group_by(pais) %>%
    dplyr::mutate(
      max_val = max(!!rlang::sym(value_col), na.rm = TRUE),
      normalized = !!rlang::sym(value_col) / dplyr::if_else(max_val == 0, 1, max_val)
    ) %>%
    dplyr::ungroup()
}
