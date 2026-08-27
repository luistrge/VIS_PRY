# Methodology and interpretation

This note documents what the application computes from the bundled processed panel and how its visual outputs should be interpreted.

## Processing flow

```text
Processed daily country panel
        │
        ├── latest observation per country ──► global KPIs and cross-sectional charts
        │
        ├── weekly aggregation ──────────────► animated incidence map and wave comparison
        │
        └── country + date filtering ────────► country KPIs and monthly charts
```

The dataset is loaded once when the Shiny process starts. User inputs then filter or aggregate that in-memory table reactively.

## Core indicators

### Cumulative incidence

```text
cumulative incidence per 100,000 = cumulative confirmed cases / population × 100,000
```

### Mortality rate

```text
mortality per 100,000 = cumulative deaths / population × 100,000
```

### Case-fatality ratio

```text
CFR (%) = cumulative deaths / cumulative confirmed cases × 100
```

CFR describes deaths among reported confirmed cases. It is not an infection-fatality ratio and is sensitive to testing coverage, reporting delays, and differences in national definitions.

## Visualization-specific transformations

### Animated choropleth

Daily new cases and deaths are summed into week-start groups using `lubridate::floor_date(fecha, "week")`. The map displays weekly new confirmed cases per 100,000 residents. The panel produces 53 groups, from the week beginning 2019-12-29 through the week beginning 2020-12-27, because the first and last calendar weeks cross year boundaries.

The upper color limit is the 95th percentile of the displayed weekly-incidence distribution. Values above that limit share the top color. This increases contrast for most countries but compresses extremes.

### Wave comparison

Weekly new cases are divided by the maximum weekly count within each selected country:

```text
normalized weekly intensity = country weekly cases / country maximum weekly cases
```

This makes temporal shapes comparable. It intentionally removes absolute scale, so equal peak heights do not imply equal population burden or case counts.

### Incidence dumbbell

For each selected country, the chart takes the first and last available observations within the user-selected interval. It compares cumulative incidence at those two endpoints.

### Health expenditure vs case fatality

Each marker represents a country's latest 2020 observation:

- x-axis: health expenditure as a percentage of GDP;
- y-axis: case-fatality ratio;
- bubble area input: population-scaled marker diameter; and
- color: GDP per capita for 2019.

The plot is descriptive. It does not estimate an effect of spending or wealth on mortality.

### Incidence–fatality matrix

Dashed lines show the median cumulative incidence and median CFR of the currently displayed country sample. Filtering countries therefore changes both reference lines. The four areas are relative quadrants, not validated categories of health-system efficiency.

### Country radar comparison

The latest selected-country observation is compared with the unweighted world mean for five metrics. Each metric is min–max normalized over the 189-country latest-observation table. A higher radial value only means a higher value for that metric within this dataset; it is not necessarily a better outcome.

### Monthly charts

- The temporal line uses the maximum cumulative confirmed-case value observed in each month.
- Monthly case and death bars sum the respective daily fields.
- `PICO` marks the largest monthly total within the selected date interval.

## Important limitations

1. **Reporting is not measurement of true prevalence.** Confirmed cases depend on access to testing and national reporting practices.
2. **Deaths are not perfectly comparable.** Definitions, certification, reporting delays, and retrospective updates vary.
3. **Associations are not causal effects.** The dashboard does not adjust for demographic structure, epidemic timing, policy, testing, mobility, or other confounders.
4. **The socioeconomic join is not fully traceable here.** The processed file includes GDP and health-spending fields, but the raw snapshots, extraction date, and join pipeline are absent.
5. **A complete zero-filled panel can conceal upstream absence.** No missing cells remain, but the repository does not establish whether every stored zero originated as an observed zero.
6. **The global CFR KPI is an unweighted mean.** It gives the same weight to every country and differs from a population- or case-weighted global ratio.
7. **The scope ends in 2020.** The dashboard is a historical view of the first pandemic year, not a current tracker.

## Source references

- [WHO COVID-19 dashboard data](https://data.who.int/dashboards/covid19/data)
- [World Bank: GDP per capita](https://data.worldbank.org/indicator/NY.GDP.PCAP.CD)
- [World Bank: current health expenditure (% of GDP)](https://data.worldbank.org/indicator/SH.XPD.CHEX.GD.ZS)

These links identify the organizations and indicators attributed by the project. They do not substitute for missing raw-data snapshots or establish exact row-level lineage for the bundled CSV.
