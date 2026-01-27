# ==============================================================================
# DATA PROCESSING FUNCTIONS
# ==============================================================================

#' Load COVID-19 data from CSV file
#'
#' Reads the CSV file and ensures proper data types for all columns
#'
#' @param file_path Path to the CSV file
#' @return Data frame with COVID data
load_covid_data <- function(file_path) {
  df <- readr::read_csv(
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

  # Ensure numeric columns are properly formatted and replace NA with 0
  numeric_cols <- c(
    "confirmados", "muertes", "IA_100k",
    "tasa_mortalidad_100k", "letalidad_CFR_pct",
    "confirmados_dia", "muertes_dia",
    "IA_100k_dia", "tasa_mortalidad_100k_dia", "letalidad_CFR_pct_dia",
    "pib_per_capita_2019", "gasto_salud_pib", "poblacion"
  )

  df <- df %>%
    dplyr::mutate(dplyr::across(dplyr::all_of(numeric_cols),
                                ~as.numeric(.) %>% tidyr::replace_na(0)))

  return(df)
}

#' Get latest data per country
#'
#' Extracts the most recent row for each country
#'
#' @param df COVID data frame
#' @return Data frame with one row per country (latest date)
get_latest_by_country <- function(df) {
  df %>%
    dplyr::group_by(pais) %>%
    dplyr::slice_max(fecha, n = 1, with_ties = FALSE) %>%
    dplyr::ungroup()
}

#' Get sorted list of countries
#'
#' @param df COVID data frame
#' @return Character vector of sorted country names
get_country_list <- function(df) {
  df %>%
    dplyr::pull(pais) %>%
    unique() %>%
    sort()
}

#' Aggregate data by week for choropleth animation
#'
#' Groups daily data by week and calculates weekly incidence rates
#'
#' @param df COVID data frame
#' @return Data frame with weekly aggregates
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
#'
#' Normalizes a column so that the max value per country is 1.0
#'
#' @param df Data frame
#' @param value_col Name of the column to normalize
#' @return Data frame with normalized column
normalize_by_country <- function(df, value_col) {
  df %>%
    dplyr::group_by(pais) %>%
    dplyr::mutate(
      max_val = max(!!rlang::sym(value_col), na.rm = TRUE),
      normalized = !!rlang::sym(value_col) / dplyr::if_else(max_val == 0, 1, max_val)
    ) %>%
    dplyr::ungroup()
}
