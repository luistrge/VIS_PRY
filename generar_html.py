"""
Script para generar un HTML estático con todos los gráficos del dashboard COVID-19
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ═══════════════════════════════════════════════════════════════════════════════
# CARGA DE DATOS
# ═══════════════════════════════════════════════════════════════════════════════
print("📊 Cargando datos...")
df = pd.read_csv("panel_2020_paises_sin_nan_R_clean.csv")
df["fecha"] = pd.to_datetime(df["fecha"])

numeric_cols = [
    "confirmados", "muertes", "IA_100k", "tasa_mortalidad_100k",
    "letalidad_CFR_pct", "confirmados_dia", "muertes_dia",
    "pib_per_capita_2019", "gasto_salud_pib", "poblacion",
]
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

df_ultimo = df.loc[df.groupby("pais")["fecha"].idxmax()]
paises = sorted(df["pais"].dropna().unique().tolist())

# Función para formatear números
def fmt(n):
    if n >= 1e9:
        return f"{n / 1e9:.2f}B"
    if n >= 1e6:
        return f"{n / 1e6:.2f}M"
    if n >= 1e3:
        return f"{n / 1e3:.1f}K"
    return f"{n:,.0f}"

# ═══════════════════════════════════════════════════════════════════════════════
# KPIs GLOBALES
# ═══════════════════════════════════════════════════════════════════════════════
print("📈 Calculando KPIs...")
total_casos = int(df_ultimo["confirmados"].sum())
total_muertes = int(df_ultimo["muertes"].sum())
n_paises = df_ultimo["pais"].nunique()
avg_letalidad = df_ultimo["letalidad_CFR_pct"].mean()

# ═══════════════════════════════════════════════════════════════════════════════
# GRÁFICO 1: MAPA GLOBAL (última semana)
# ═══════════════════════════════════════════════════════════════════════════════
print("🗺️  Generando mapa global...")
fig_mapa = go.Figure(data=go.Choropleth(
    locations=df_ultimo["iso3c"],
    z=df_ultimo["IA_100k"],
    text=df_ultimo["pais"],
    colorscale=[
        [0, "#0f0a2e"], [0.1, "#1e1b4b"], [0.25, "#3730a3"],
        [0.4, "#4f46e5"], [0.55, "#6366f1"], [0.7, "#818cf8"],
        [0.85, "#a5b4fc"], [1, "#e0e7ff"],
    ],
    colorbar=dict(
        title=dict(text="Incidencia<br>/100k", font=dict(size=11, color="white")),
        thickness=18, len=0.75,
        bgcolor="rgba(15,15,40,0.9)",
        bordercolor="rgba(99,102,241,0.4)",
        tickfont=dict(color="rgba(255,255,255,0.8)", size=10),
    ),
    hovertemplate="<b>%{text}</b><br>Incidencia: %{z:,.1f}/100k<extra></extra>",
))
fig_mapa.update_geos(
    showframe=False, showcoastlines=True,
    coastlinecolor="rgba(99,102,241,0.5)", coastlinewidth=0.5,
    projection_type="natural earth", bgcolor="rgba(0,0,0,0)",
    landcolor="rgba(20,20,45,0.95)", oceancolor="rgba(8,8,25,1)",
    showland=True, showcountries=True,
    countrycolor="rgba(99,102,241,0.25)", countrywidth=0.3,
)
fig_mapa.update_layout(
    height=500, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="rgba(255,255,255,0.8)"), margin=dict(l=0, r=0, t=10, b=10),
)

# ═══════════════════════════════════════════════════════════════════════════════
# GRÁFICO 2: OLAS DE CONTAGIO (Ridgeline)
# ═══════════════════════════════════════════════════════════════════════════════
print("🌊 Generando gráfico de olas...")
selected_countries = ["Spain", "Italy", "United States", "Brazil", "Germany", "France", "United Kingdom"]
selected_countries = [p for p in selected_countries if p in paises][:7]

data_wave = df[df["pais"].isin(selected_countries)].copy()
data_wave["semana"] = data_wave["fecha"].dt.to_period("W").apply(lambda x: x.start_time)
data_semanal = data_wave.groupby(["pais", "semana"]).agg({"confirmados_dia": "sum"}).reset_index()
max_by_country = data_semanal.groupby("pais")["confirmados_dia"].transform("max")
data_semanal["confirmados_norm"] = data_semanal["confirmados_dia"] / max_by_country.replace(0, 1)

fig_wave = go.Figure()
country_colors = px.colors.qualitative.Set2
countries = list(reversed(selected_countries))
offset_step = 1.0

for i, country in enumerate(countries):
    country_data = data_semanal[data_semanal["pais"] == country].sort_values("semana")
    if len(country_data) == 0:
        continue
    offset = i * offset_step
    color = country_colors[i % len(country_colors)]
    x_vals = country_data["semana"].tolist()
    y_vals = (country_data["confirmados_norm"] + offset).tolist()
    y_base = [offset] * len(x_vals)
    fig_wave.add_trace(go.Scatter(
        x=x_vals + x_vals[::-1], y=y_vals + y_base[::-1],
        fill="toself",
        fillcolor=color.replace("rgb", "rgba").replace(")", ",0.4)") if "rgb" in color else color + "66",
        line=dict(color=color, width=1.5), name=country,
        hovertemplate=f"<b>{country}</b><br>Semana: %{{x|%Y-%m-%d}}<extra></extra>",
    ))

fig_wave.update_layout(
    height=450, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="rgba(255,255,255,0.8)"),
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5,
                bgcolor="rgba(20,20,50,0.7)", bordercolor="rgba(99,102,241,0.3)"),
    xaxis=dict(title="Tiempo", gridcolor="rgba(255,255,255,0.1)"),
    yaxis=dict(title="Intensidad (normalizado)", gridcolor="rgba(255,255,255,0.05)", showticklabels=False),
    margin=dict(l=60, r=30, t=50, b=60),
)

# ═══════════════════════════════════════════════════════════════════════════════
# GRÁFICO 3: DUMBBELL - INCREMENTO DE INCIDENCIA
# ═══════════════════════════════════════════════════════════════════════════════
print("📊 Generando gráfico dumbbell...")
top_countries = df_ultimo.nlargest(15, "IA_100k")["pais"].tolist()
data_dumb = df[df["pais"].isin(top_countries)].copy()

data_inicio = data_dumb.loc[data_dumb.groupby("pais")["fecha"].idxmin()][["pais", "IA_100k"]].copy()
data_inicio.columns = ["pais", "IA_100k_inicio"]
data_fin = data_dumb.loc[data_dumb.groupby("pais")["fecha"].idxmax()][["pais", "IA_100k"]].copy()
data_fin.columns = ["pais", "IA_100k_fin"]
data_dumbbell = data_inicio.merge(data_fin, on="pais")
data_dumbbell["incremento"] = data_dumbbell["IA_100k_fin"] - data_dumbbell["IA_100k_inicio"]
data_dumbbell = data_dumbbell.sort_values("IA_100k_fin", ascending=True)

fig_dumbbell = go.Figure()
for _, row in data_dumbbell.iterrows():
    fig_dumbbell.add_trace(go.Scatter(
        x=[row["IA_100k_inicio"], row["IA_100k_fin"]], y=[row["pais"], row["pais"]],
        mode="lines", line=dict(color="rgba(148,163,184,0.6)", width=2),
        showlegend=False, hoverinfo="skip",
    ))
fig_dumbbell.add_trace(go.Scatter(
    x=data_dumbbell["IA_100k_inicio"], y=data_dumbbell["pais"],
    mode="markers", marker=dict(color="#10b981", size=12, line=dict(color="white", width=1)),
    name="Inicio", hovertemplate="<b>%{y}</b><br>Incidencia Inicio: %{x:.1f}/100k<extra></extra>",
))
fig_dumbbell.add_trace(go.Scatter(
    x=data_dumbbell["IA_100k_fin"], y=data_dumbbell["pais"],
    mode="markers", marker=dict(color="#ef4444", size=12, line=dict(color="white", width=1)),
    name="Fin", hovertemplate="<b>%{y}</b><br>Incidencia Final: %{x:.1f}/100k<extra></extra>",
))
fig_dumbbell.update_layout(
    height=500, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="rgba(255,255,255,0.8)"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5,
                bgcolor="rgba(20,20,50,0.7)"),
    xaxis=dict(title="Incidencia Acumulada (por 100k)", gridcolor="rgba(255,255,255,0.1)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont=dict(size=10)),
    margin=dict(l=120, r=30, t=50, b=60),
)

# ═══════════════════════════════════════════════════════════════════════════════
# GRÁFICO 4: GASTO EN SALUD VS LETALIDAD
# ═══════════════════════════════════════════════════════════════════════════════
print("💰 Generando gráfico de gasto en salud...")
data_salud = df_ultimo[df_ultimo["gasto_salud_pib"] > 0].copy()

fig_salud = px.scatter(
    data_salud, x="gasto_salud_pib", y="letalidad_CFR_pct",
    size="poblacion", color="pib_per_capita_2019", hover_name="pais",
    color_continuous_scale=["#10b981", "#fbbf24", "#ef4444"],
    labels={"gasto_salud_pib": "Gasto Salud (%PIB)", "letalidad_CFR_pct": "Letalidad (%)"},
)
fig_salud.update_layout(
    height=450, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="rgba(255,255,255,0.9)", size=12),
    xaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
    margin=dict(l=50, r=15, t=10, b=40),
)

# ═══════════════════════════════════════════════════════════════════════════════
# GRÁFICO 5: MATRIZ DE EFICIENCIA SANITARIA
# ═══════════════════════════════════════════════════════════════════════════════
print("🏥 Generando matriz de eficiencia...")
data_eff = df_ultimo[(df_ultimo["gasto_salud_pib"] > 0) & (df_ultimo["IA_100k"] > 0)].copy()
median_incidencia = data_eff["IA_100k"].median()
median_letalidad = data_eff["letalidad_CFR_pct"].median()
max_pop = data_eff["poblacion"].max()
data_eff["size"] = (data_eff["poblacion"] / max_pop * 40) + 5

fig_efficiency = go.Figure()
fig_efficiency.add_trace(go.Scatter(
    x=data_eff["IA_100k"], y=data_eff["letalidad_CFR_pct"],
    mode="markers",
    marker=dict(
        size=data_eff["size"], color=data_eff["gasto_salud_pib"],
        colorscale="Viridis", opacity=0.7,
        line=dict(width=1, color="rgba(255,255,255,0.3)"),
        colorbar=dict(title="Gasto Salud<br>(% PIB)", thickness=15, len=0.6),
    ),
    text=data_eff["pais"],
    hovertemplate="<b>%{text}</b><br>Incidencia: %{x:.1f}/100k<br>Letalidad: %{y:.2f}%<extra></extra>",
))
fig_efficiency.add_hline(y=median_letalidad, line=dict(color="rgba(255,255,255,0.4)", width=1, dash="dash"))
fig_efficiency.add_vline(x=median_incidencia, line=dict(color="rgba(255,255,255,0.4)", width=1, dash="dash"))
fig_efficiency.update_layout(
    height=450, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="rgba(255,255,255,0.8)", size=10),
    xaxis=dict(title="Incidencia (por 100k)", gridcolor="rgba(255,255,255,0.1)"),
    yaxis=dict(title="Letalidad (%)", gridcolor="rgba(255,255,255,0.1)"),
    margin=dict(l=50, r=15, t=10, b=40),
)

# ═══════════════════════════════════════════════════════════════════════════════
# GRÁFICO 6: EVOLUCIÓN TEMPORAL (España como ejemplo)
# ═══════════════════════════════════════════════════════════════════════════════
print("📈 Generando evolución temporal...")
pais_ejemplo = "Spain" if "Spain" in paises else paises[0]
data_pais = df[df["pais"] == pais_ejemplo].copy()
data_pais["mes"] = data_pais["fecha"].dt.to_period("M").astype(str)
data_mes = data_pais.groupby("mes").agg({"confirmados": "max"}).reset_index()

fig_temporal = px.line(
    data_mes, x="mes", y="confirmados",
    labels={"mes": "Mes", "confirmados": "Casos Acumulados"},
    color_discrete_sequence=["#6366f1"], markers=True,
)
fig_temporal.update_layout(
    height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="rgba(255,255,255,0.9)", size=12),
    xaxis=dict(gridcolor="rgba(255,255,255,0.1)", tickangle=-45),
    yaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
    margin=dict(l=50, r=20, t=30, b=80),
)

# ═══════════════════════════════════════════════════════════════════════════════
# GRÁFICO 7: CASOS POR MES
# ═══════════════════════════════════════════════════════════════════════════════
print("📊 Generando casos por mes...")
data_pais_sorted = data_pais.sort_values("fecha").copy()
data_pais_sorted["mes"] = data_pais_sorted["fecha"].dt.to_period("M")
data_casos_mes = data_pais_sorted.groupby("mes").agg({"confirmados_dia": "sum"}).reset_index()
data_casos_mes["mes_str"] = data_casos_mes["mes"].dt.strftime("%b")
idx_max = data_casos_mes["confirmados_dia"].idxmax()
colores_casos = ["#a855f7" if i != idx_max else "#22c55e" for i in range(len(data_casos_mes))]

fig_casos = go.Figure()
fig_casos.add_trace(go.Bar(
    x=data_casos_mes["mes_str"], y=data_casos_mes["confirmados_dia"],
    marker_color=colores_casos,
    hovertemplate="<b>%{x}</b><br>Casos: %{y:,.0f}<extra></extra>",
))
fig_casos.update_layout(
    height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="rgba(255,255,255,0.9)", size=12),
    xaxis=dict(title="Mes 2020", gridcolor="rgba(255,255,255,0.05)"),
    yaxis=dict(title="Casos", gridcolor="rgba(255,255,255,0.1)"),
    margin=dict(l=60, r=20, t=40, b=60),
)

# ═══════════════════════════════════════════════════════════════════════════════
# GRÁFICO 8: MUERTES POR MES
# ═══════════════════════════════════════════════════════════════════════════════
print("💀 Generando muertes por mes...")
data_muertes_mes = data_pais_sorted.groupby("mes").agg({"muertes_dia": "sum"}).reset_index()
data_muertes_mes["mes_str"] = data_muertes_mes["mes"].dt.strftime("%b")
idx_max_m = data_muertes_mes["muertes_dia"].idxmax()
colores_muertes = ["#ef4444" if i != idx_max_m else "#f97316" for i in range(len(data_muertes_mes))]

fig_muertes = go.Figure()
fig_muertes.add_trace(go.Bar(
    x=data_muertes_mes["mes_str"], y=data_muertes_mes["muertes_dia"],
    marker_color=colores_muertes,
    hovertemplate="<b>%{x}</b><br>Muertes: %{y:,.0f}<extra></extra>",
))
fig_muertes.update_layout(
    height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="rgba(255,255,255,0.9)", size=12),
    xaxis=dict(title="Mes 2020", gridcolor="rgba(255,255,255,0.05)"),
    yaxis=dict(title="Muertes", gridcolor="rgba(255,255,255,0.1)"),
    margin=dict(l=60, r=20, t=40, b=60),
)

# ═══════════════════════════════════════════════════════════════════════════════
# GENERAR HTML
# ═══════════════════════════════════════════════════════════════════════════════
print("🔧 Generando HTML...")

html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard COVID-19 2020</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ font-family: 'Inter', sans-serif; box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ 
            background: linear-gradient(135deg, #0c0c1e 0%, #1a1a3e 50%, #0d0d2b 100%); 
            min-height: 100vh; 
            color: white;
            padding: 40px;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        
        /* Header */
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding: 40px;
            background: linear-gradient(135deg, rgba(15, 15, 35, 0.95), rgba(25, 25, 55, 0.9));
            border-radius: 20px;
            border: 1px solid rgba(99, 102, 241, 0.2);
        }}
        .header h1 {{
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 10px;
        }}
        .header h1 span {{
            background: linear-gradient(135deg, #6366f1, #a855f7, #ec4899);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .header p {{ color: rgba(255,255,255,0.6); font-size: 1.1rem; }}
        
        /* KPIs */
        .kpis {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 40px;
        }}
        .kpi {{
            background: linear-gradient(145deg, rgba(25, 25, 55, 0.9), rgba(35, 35, 70, 0.8));
            border-radius: 20px;
            padding: 25px;
            text-align: center;
            border: 1px solid rgba(99, 102, 241, 0.25);
        }}
        .kpi-value {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 5px;
        }}
        .kpi-value.casos {{ color: #818cf8; }}
        .kpi-value.muertes {{ color: #f87171; }}
        .kpi-value.paises {{ color: #34d399; }}
        .kpi-value.letalidad {{ color: #fbbf24; }}
        .kpi-label {{
            font-size: 0.9rem;
            color: rgba(255,255,255,0.6);
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        /* Sections */
        .section {{
            background: linear-gradient(145deg, rgba(25, 25, 55, 0.7), rgba(15, 15, 45, 0.8));
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            border: 1px solid rgba(255, 255, 255, 0.08);
        }}
        .section-header {{
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid rgba(99, 102, 241, 0.2);
        }}
        .section-number {{
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.3), rgba(168, 85, 247, 0.3));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .section-title {{ font-size: 1.4rem; font-weight: 600; }}
        .section-subtitle {{ font-size: 0.85rem; color: rgba(255,255,255,0.5); margin-top: 3px; }}
        
        /* Grid */
        .grid-2 {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 30px;
        }}
        
        /* Footer */
        .footer {{
            text-align: center;
            padding: 30px;
            color: rgba(255,255,255,0.4);
            font-size: 0.85rem;
            border-top: 1px solid rgba(255,255,255,0.05);
            margin-top: 30px;
        }}
        
        @media (max-width: 992px) {{
            .kpis {{ grid-template-columns: repeat(2, 1fr); }}
            .grid-2 {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>COVID-19 <span>Panel de Análisis 2020</span></h1>
            <p>Análisis integral del impacto del COVID-19 correlacionado con indicadores económicos y de salud</p>
        </div>
        
        <!-- KPIs -->
        <div class="kpis">
            <div class="kpi">
                <div class="kpi-value casos">{fmt(total_casos)}</div>
                <div class="kpi-label">Casos Confirmados</div>
            </div>
            <div class="kpi">
                <div class="kpi-value muertes">{fmt(total_muertes)}</div>
                <div class="kpi-label">Muertes Totales</div>
            </div>
            <div class="kpi">
                <div class="kpi-value paises">{n_paises}</div>
                <div class="kpi-label">Países Analizados</div>
            </div>
            <div class="kpi">
                <div class="kpi-value letalidad">{avg_letalidad:.2f}%</div>
                <div class="kpi-label">Tasa de Letalidad</div>
            </div>
        </div>
        
        <!-- Sección Global -->
        <h2 style="font-size: 1.8rem; margin-bottom: 25px; padding-left: 10px; border-left: 4px solid #6366f1;">
            🌍 Visualización Global
        </h2>
        
        <!-- Mapa -->
        <div class="section">
            <div class="section-header">
                <span class="section-number">01</span>
                <div>
                    <div class="section-title">Mapa Global de Incidencia</div>
                    <div class="section-subtitle">Distribución geográfica de casos por 100.000 habitantes (datos finales 2020)</div>
                </div>
            </div>
            <div id="mapa"></div>
        </div>
        
        <!-- Grid 2x2 -->
        <div class="grid-2">
            <div class="section">
                <div class="section-header">
                    <span class="section-number">02</span>
                    <div>
                        <div class="section-title">Olas de Contagio</div>
                        <div class="section-subtitle">Comparación de olas entre países (normalizado)</div>
                    </div>
                </div>
                <div id="wave"></div>
            </div>
            
            <div class="section">
                <div class="section-header">
                    <span class="section-number">03</span>
                    <div>
                        <div class="section-title">Incremento de Incidencia</div>
                        <div class="section-subtitle">Crecimiento desde inicio a fin del período</div>
                    </div>
                </div>
                <div id="dumbbell"></div>
            </div>
            
            <div class="section">
                <div class="section-header">
                    <span class="section-number">04</span>
                    <div>
                        <div class="section-title">Gasto en Salud vs Letalidad</div>
                        <div class="section-subtitle">Inversión sanitaria y tasa de letalidad</div>
                    </div>
                </div>
                <div id="salud"></div>
            </div>
            
            <div class="section">
                <div class="section-header">
                    <span class="section-number">05</span>
                    <div>
                        <div class="section-title">Matriz de Eficiencia Sanitaria</div>
                        <div class="section-subtitle">Incidencia vs Letalidad por país</div>
                    </div>
                </div>
                <div id="efficiency"></div>
            </div>
        </div>
        
        <!-- Sección País -->
        <h2 style="font-size: 1.8rem; margin: 40px 0 25px; padding-left: 10px; border-left: 4px solid #a855f7;">
            📍 Análisis por País: {pais_ejemplo}
        </h2>
        
        <div class="grid-2">
            <div class="section">
                <div class="section-header">
                    <span class="section-number">01</span>
                    <div>
                        <div class="section-title">Evolución Temporal</div>
                        <div class="section-subtitle">Casos acumulados a lo largo del tiempo</div>
                    </div>
                </div>
                <div id="temporal"></div>
            </div>
            
            <div class="section">
                <div class="section-header">
                    <span class="section-number">02</span>
                    <div>
                        <div class="section-title">Casos por Mes</div>
                        <div class="section-subtitle">Nuevos contagios mensuales</div>
                    </div>
                </div>
                <div id="casos"></div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-header">
                <span class="section-number">03</span>
                <div>
                    <div class="section-title">Muertes por Mes</div>
                    <div class="section-subtitle">Fallecimientos mensuales</div>
                </div>
            </div>
            <div id="muertes"></div>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            Dashboard COVID-19 2020 | Datos: WHO & World Bank | Generado con Python + Plotly
        </div>
    </div>
    
    <script>
        // Mapa
        {fig_mapa.to_json()}
        Plotly.newPlot('mapa', {fig_mapa.to_json()}.data, {fig_mapa.to_json()}.layout, {{responsive: true}});
        
        // Wave
        Plotly.newPlot('wave', {fig_wave.to_json()}.data, {fig_wave.to_json()}.layout, {{responsive: true}});
        
        // Dumbbell
        Plotly.newPlot('dumbbell', {fig_dumbbell.to_json()}.data, {fig_dumbbell.to_json()}.layout, {{responsive: true}});
        
        // Salud
        Plotly.newPlot('salud', {fig_salud.to_json()}.data, {fig_salud.to_json()}.layout, {{responsive: true}});
        
        // Efficiency
        Plotly.newPlot('efficiency', {fig_efficiency.to_json()}.data, {fig_efficiency.to_json()}.layout, {{responsive: true}});
        
        // Temporal
        Plotly.newPlot('temporal', {fig_temporal.to_json()}.data, {fig_temporal.to_json()}.layout, {{responsive: true}});
        
        // Casos
        Plotly.newPlot('casos', {fig_casos.to_json()}.data, {fig_casos.to_json()}.layout, {{responsive: true}});
        
        // Muertes
        Plotly.newPlot('muertes', {fig_muertes.to_json()}.data, {fig_muertes.to_json()}.layout, {{responsive: true}});
    </script>
</body>
</html>
"""

# Guardar archivo
with open("dashboard_covid19_2020.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("\n✅ ¡HTML generado exitosamente!")
print("📁 Archivo: dashboard_covid19_2020.html")
print("\n💡 Puedes abrir este archivo en cualquier navegador web.")
