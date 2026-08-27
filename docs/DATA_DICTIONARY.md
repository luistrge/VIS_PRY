# Data dictionary

The dashboard reads `data/panel_2020_paises_sin_nan_R_clean.csv`, a balanced daily panel covering 189 countries from 1 January through 31 December 2020.

## Audited structure

| Check | Result |
|---|---:|
| Rows | 69,174 |
| Columns | 16 |
| Countries | 189 |
| Calendar days per country | 366 |
| Missing cells | 0 |
| Duplicate `pais`–`fecha` keys | 0 |

These checks describe the bundled file. They do not independently validate every value against an upstream raw release.

## Fields

| Field | Type | Meaning |
|---|---|---|
| `iso3c` | character | ISO 3166-1 alpha-3 country code used by the map |
| `pais` | character | Country name displayed in selectors and tooltips |
| `fecha` | date | Daily observation date in `YYYY-MM-DD` format |
| `poblacion` | numeric | Population denominator used for normalized rates |
| `confirmados` | numeric | Cumulative reported confirmed cases through `fecha` |
| `muertes` | numeric | Cumulative reported deaths through `fecha` |
| `IA_100k` | numeric | Cumulative confirmed cases per 100,000 residents |
| `tasa_mortalidad_100k` | numeric | Cumulative deaths per 100,000 residents |
| `letalidad_CFR_pct` | numeric | Cumulative reported deaths divided by confirmed cases, in percent |
| `confirmados_dia` | numeric | Reported new confirmed cases for the day |
| `muertes_dia` | numeric | Reported new deaths for the day |
| `IA_100k_dia` | numeric | Daily confirmed cases per 100,000 residents |
| `tasa_mortalidad_100k_dia` | numeric | Daily deaths per 100,000 residents |
| `letalidad_CFR_pct_dia` | numeric | Daily deaths divided by daily confirmed cases, in percent; zero when daily cases are zero in this processed file |
| `pib_per_capita_2019` | numeric | GDP per capita for 2019; currency basis is not encoded in the CSV column name |
| `gasto_salud_pib` | numeric | Current health expenditure as a percentage of GDP; reference year is not encoded in the processed file |

## Verified derived-field identities

The stored values match the following identities to floating-point precision:

```text
IA_100k                    = confirmados / poblacion × 100,000
tasa_mortalidad_100k       = muertes / poblacion × 100,000
letalidad_CFR_pct          = muertes / confirmados × 100
IA_100k_dia                = confirmados_dia / poblacion × 100,000
tasa_mortalidad_100k_dia   = muertes_dia / poblacion × 100,000
letalidad_CFR_pct_dia      = muertes_dia / confirmados_dia × 100
```

For divisions whose denominator is zero, the processed file stores zero rather than an undefined or missing value.

## Provenance boundary

The repository attributes the epidemiological data to the World Health Organization and its contextual indicators to World Bank data. It does not contain raw source snapshots or the original extraction and joining scripts. Consult the [methodology note](METHODOLOGY.md) before using the file outside this dashboard.
