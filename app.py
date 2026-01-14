from shiny import App, ui, render, reactive
from shinywidgets import output_widget, render_widget
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ═══════════════════════════════════════════════════════════════════════════════
# CARGA DE DATOS
# ═══════════════════════════════════════════════════════════════════════════════
df = pd.read_csv("panel_2020_paises_sin_nan_R_clean.csv")
df["fecha"] = pd.to_datetime(df["fecha"])

numeric_cols = [
    "confirmados",
    "muertes",
    "IA_100k",
    "tasa_mortalidad_100k",
    "letalidad_CFR_pct",
    "confirmados_dia",
    "muertes_dia",
    "pib_per_capita_2019",
    "gasto_salud_pib",
    "poblacion",
]
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

df_ultimo = df.loc[df.groupby("pais")["fecha"].idxmax()]
paises = sorted(df["pais"].dropna().unique().tolist())
fecha_min = df["fecha"].min()
fecha_max = df["fecha"].max()

# Páginas disponibles
PAGINA_INICIO = "inicio"
PAGINA_GLOBAL = "global"
PAGINA_PAIS = "pais"

# ═══════════════════════════════════════════════════════════════════════════════
# CSS PROFESIONAL CON HERO Y NAVEGACIÓN
# ═══════════════════════════════════════════════════════════════════════════════
css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* { font-family: 'Inter', sans-serif; box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body { background: linear-gradient(135deg, #0c0c1e 0%, #1a1a3e 50%, #0d0d2b 100%); min-height: 100vh; background-attachment: fixed; }

/* ANIMACIONES */
@keyframes pulse { 0%, 100% { box-shadow: 0 0 20px rgba(99, 102, 241, 0.4); } 50% { box-shadow: 0 0 40px rgba(99, 102, 241, 0.8); } }
@keyframes float { 0%, 100% { transform: translateY(0px); } 50% { transform: translateY(-8px); } }
@keyframes glowPulse { 0%, 100% { box-shadow: 0 0 20px rgba(99, 102, 241, 0.15); } 50% { box-shadow: 0 0 40px rgba(99, 102, 241, 0.3); } }
@keyframes slideInUp { from { opacity: 0; transform: translateY(40px); } to { opacity: 1; transform: translateY(0); } }
@keyframes countUp { from { opacity: 0; transform: scale(0.8); } to { opacity: 1; transform: scale(1); } }
@keyframes borderGlow { 0%, 100% { border-color: rgba(99, 102, 241, 0.3); } 50% { border-color: rgba(168, 85, 247, 0.6); } }
@keyframes shimmer { 0% { background-position: -200% center; } 100% { background-position: 200% center; } }

/* PÁGINA OCULTA */
.page-hidden { display: none !important; }

/* HERO LANDING */
.hero-landing { min-height: 100vh; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 40px; position: relative; }
.hero-section { background: linear-gradient(135deg, rgba(15, 15, 35, 0.95), rgba(25, 25, 55, 0.9)); padding: 100px; border-radius: 30px; border: 1px solid rgba(99, 102, 241, 0.2); backdrop-filter: blur(20px); max-width: 1600px; width: 100%; position: relative; overflow: hidden; }
.hero-section::before { content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: radial-gradient(circle at 20% 80%, rgba(99, 102, 241, 0.15) 0%, transparent 50%), radial-gradient(circle at 80% 20%, rgba(168, 85, 247, 0.15) 0%, transparent 50%); pointer-events: none; }
.hero-content { position: relative; z-index: 2; display: flex; align-items: center; justify-content: space-between; gap: 60px; flex-direction: row-reverse; }
.hero-text { flex: 1; }
.hero-badge { display: inline-flex; align-items: center; gap: 8px; background: rgba(99, 102, 241, 0.15); border: 1px solid rgba(99, 102, 241, 0.3); padding: 6px 14px; border-radius: 50px; margin-bottom: 20px; font-size: 0.75rem; color: rgba(255, 255, 255, 0.8); letter-spacing: 1px; text-transform: uppercase; }
.hero-badge-dot { width: 8px; height: 8px; background: #10b981; border-radius: 50%; animation: pulse 2s infinite; }
.hero-title { font-size: 3.5rem; font-weight: 700; color: #fff; margin-bottom: 20px; line-height: 1.2; }
.hero-title-accent { background: linear-gradient(135deg, #6366f1, #a855f7, #ec4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.hero-description { font-size: 1.2rem; color: rgba(255, 255, 255, 0.6); line-height: 1.7; margin-bottom: 35px; max-width: 600px; }
.hero-visual { flex: 0 0 400px; }
.hero-globe { width: 380px; height: 380px; }
.hero-globe svg { width: 100%; height: 100%; filter: drop-shadow(0 0 30px rgba(99, 102, 241, 0.4)); }

/* BOTONES DE NAVEGACIÓN HERO */
.hero-buttons { display: flex; gap: 20px; margin-top: 30px; flex-wrap: wrap; }
.hero-btn { display: inline-flex; align-items: center; gap: 12px; padding: 18px 32px; border-radius: 16px; font-size: 1rem; font-weight: 600; cursor: pointer; transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1); border: 2px solid transparent; text-decoration: none; position: relative; overflow: hidden; }
.hero-btn::before { content: ''; position: absolute; top: 0; left: -100%; width: 100%; height: 100%; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent); transition: left 0.5s; }
.hero-btn:hover::before { left: 100%; }
.hero-btn-primary { background: linear-gradient(135deg, #6366f1, #8b5cf6); color: #fff; box-shadow: 0 8px 30px rgba(99, 102, 241, 0.4); }
.hero-btn-primary:hover { transform: translateY(-4px) scale(1.02); box-shadow: 0 12px 40px rgba(99, 102, 241, 0.6); }
.hero-btn-secondary { background: rgba(30, 30, 60, 0.8); color: #fff; border: 2px solid rgba(99, 102, 241, 0.5); }
.hero-btn-secondary:hover { transform: translateY(-4px); border-color: #a855f7; box-shadow: 0 8px 30px rgba(168, 85, 247, 0.3); }
.hero-btn svg { width: 24px; height: 24px; }

/* KPIs EN HERO - PEQUEÑOS */
.hero-kpis { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-top: 30px; padding-top: 25px; border-top: 1px solid rgba(255, 255, 255, 0.1); }
.hero-kpi { text-align: center; padding: 15px; background: rgba(20, 20, 50, 0.5); border-radius: 12px; border: 1px solid rgba(99, 102, 241, 0.2); transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1); }
.hero-kpi:hover { transform: scale(1.05); border-color: rgba(99, 102, 241, 0.5); }
.hero-kpi-value { font-size: 1.5rem; font-weight: 700; background: linear-gradient(135deg, #6366f1, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.hero-kpi-label { font-size: 0.7rem; color: rgba(255, 255, 255, 0.5); text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }

/* BOTÓN VOLVER */
.back-button { position: fixed; top: 20px; left: 20px; z-index: 1000; display: flex; align-items: center; gap: 8px; padding: 12px 20px; background: rgba(25, 25, 55, 0.95); border: 1px solid rgba(99, 102, 241, 0.4); border-radius: 12px; color: #fff; font-size: 0.9rem; font-weight: 500; cursor: pointer; transition: all 0.3s ease; backdrop-filter: blur(10px); }
.back-button:hover { background: rgba(99, 102, 241, 0.3); border-color: #a855f7; transform: translateX(-3px); }
.back-button svg { width: 18px; height: 18px; }

/* HEADER DE SECCIÓN */
.section-page-header { background: linear-gradient(135deg, rgba(25, 25, 55, 0.95), rgba(35, 35, 70, 0.9)); padding: 30px 40px; border-radius: 20px; margin-bottom: 30px; border: 1px solid rgba(99, 102, 241, 0.25); display: flex; align-items: center; gap: 20px; }
.section-page-icon { width: 60px; height: 60px; border-radius: 16px; display: flex; align-items: center; justify-content: center; }
.section-page-icon.global { background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(16, 185, 129, 0.1)); color: #34d399; }
.section-page-icon.pais { background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(99, 102, 241, 0.1)); color: #818cf8; }
.section-page-icon svg { width: 30px; height: 30px; }
.section-page-title { font-size: 1.8rem; font-weight: 700; color: #fff; margin: 0; }
.section-page-subtitle { font-size: 0.95rem; color: rgba(255, 255, 255, 0.5); margin-top: 5px; }

/* KPIs DASHBOARD - GRANDES CON ANIMACIÓN */
.dashboard-kpis { display: grid; grid-template-columns: repeat(5, 1fr); gap: 20px; margin-bottom: 30px; }
.dashboard-kpi { background: linear-gradient(145deg, rgba(25, 25, 55, 0.9), rgba(35, 35, 70, 0.8)); border-radius: 20px; padding: 25px 20px; border: 1px solid rgba(99, 102, 241, 0.25); position: relative; overflow: hidden; opacity: 0; animation: slideInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1) forwards; transition: all 0.3s ease; }
.dashboard-kpi:nth-child(1) { animation-delay: 0.1s; }
.dashboard-kpi:nth-child(2) { animation-delay: 0.2s; }
.dashboard-kpi:nth-child(3) { animation-delay: 0.3s; }
.dashboard-kpi:nth-child(4) { animation-delay: 0.4s; }
.dashboard-kpi:nth-child(5) { animation-delay: 0.5s; }
.dashboard-kpi::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, #6366f1, #a855f7, #ec4899); }
.dashboard-kpi:hover { transform: translateY(-5px); border-color: rgba(99, 102, 241, 0.5); box-shadow: 0 10px 40px rgba(99, 102, 241, 0.2); }
.dashboard-kpi-icon { width: 50px; height: 50px; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-bottom: 15px; }
.dashboard-kpi-icon svg { width: 26px; height: 26px; }
.dashboard-kpi-icon.casos { background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(99, 102, 241, 0.1)); color: #818cf8; }
.dashboard-kpi-icon.muertes { background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(239, 68, 68, 0.1)); color: #f87171; }
.dashboard-kpi-icon.paises { background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(16, 185, 129, 0.1)); color: #34d399; }
.dashboard-kpi-icon.letalidad { background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(245, 158, 11, 0.1)); color: #fbbf24; }
.dashboard-kpi-icon.salud { background: linear-gradient(135deg, rgba(6, 182, 212, 0.2), rgba(6, 182, 212, 0.1)); color: #22d3ee; }
.dashboard-kpi-value { font-size: 2.2rem; font-weight: 700; margin-bottom: 5px; animation: countUp 0.8s ease-out forwards; }
.dashboard-kpi-value.casos { color: #818cf8; }
.dashboard-kpi-value.muertes { color: #f87171; }
.dashboard-kpi-value.paises { color: #34d399; }
.dashboard-kpi-value.letalidad { color: #fbbf24; }
.dashboard-kpi-value.salud { color: #22d3ee; }
.dashboard-kpi-label { font-size: 0.85rem; color: rgba(255, 255, 255, 0.6); text-transform: uppercase; letter-spacing: 1.5px; }
.dashboard-kpi-change { display: flex; align-items: center; gap: 5px; margin-top: 10px; font-size: 0.75rem; color: rgba(255, 255, 255, 0.5); }

@media (max-width: 1200px) { .dashboard-kpis { grid-template-columns: repeat(3, 1fr); } }
@media (max-width: 768px) { .dashboard-kpis { grid-template-columns: repeat(2, 1fr); } }

/* GRID DE GRÁFICOS */
.charts-row { display: grid; grid-template-columns: 1fr 1fr; gap: 25px; margin-bottom: 25px; }
.charts-row .chart-section { margin-bottom: 0; }
.charts-row .chart-section .js-plotly-plot, .charts-row .chart-section .plotly-graph-div { display: flex; justify-content: center; }
@media (max-width: 1200px) { .charts-row { grid-template-columns: 1fr; } }

/* FILTROS STICKY */
.filter-panel { background: linear-gradient(145deg, rgba(35, 35, 70, 0.95), rgba(25, 25, 55, 0.98)); border-radius: 16px; padding: 20px 25px; margin-bottom: 25px; border: 1px solid rgba(99, 102, 241, 0.3); position: sticky; top: 10px; z-index: 100; backdrop-filter: blur(20px); }
.filter-header { display: flex; align-items: center; gap: 10px; margin-bottom: 15px; padding-bottom: 12px; border-bottom: 1px solid rgba(99, 102, 241, 0.2); }
.filter-title { font-size: 1rem; font-weight: 600; color: #fff; margin: 0; }

/* CHART SECTIONS */
.chart-section { background: linear-gradient(145deg, rgba(25, 25, 55, 0.7), rgba(15, 15, 45, 0.8)); border-radius: 20px; padding: 25px 15px; margin-bottom: 25px; border: 1px solid rgba(255, 255, 255, 0.08); backdrop-filter: blur(10px); animation: glowPulse 4s ease-in-out infinite; scroll-margin-top: 80px; transition: all 0.3s ease; }
.chart-section:hover { border-color: rgba(99, 102, 241, 0.3); }
.chart-section .js-plotly-plot { width: 100% !important; }
.chart-section .plotly-graph-div { width: 100% !important; }
.chart-section .svg-container { width: 100% !important; }
.chart-section .main-svg { width: 100% !important; }
.chart-section.map-section { padding: 15px 0 10px 0; overflow: hidden; margin-left: auto; margin-right: auto; width: 100%; border-radius: 20px; }
.chart-section.map-section .section-header { padding-left: 25px; padding-right: 25px; }
.chart-section.map-section .js-plotly-plot, .chart-section.map-section .plotly-graph-div { width: 100% !important; display: flex; justify-content: center; }
.chart-section.map-section .svg-container { width: 100% !important; }
.chart-section.map-section .main-svg { width: 100% !important; }
.section-header { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid rgba(99, 102, 241, 0.2); padding-left: 10px; }
.section-number { font-size: 2.5rem; font-weight: 800; background: linear-gradient(135deg, rgba(99, 102, 241, 0.3), rgba(168, 85, 247, 0.3)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-right: 10px; line-height: 1; }
.section-title { font-size: 1.4rem; font-weight: 600; color: #fff; margin: 0; }
.section-subtitle { font-size: 0.85rem; color: rgba(255, 255, 255, 0.5); margin-top: 3px; }

/* INPUTS */
.form-select, .form-control, .selectize-input { background: rgba(30, 30, 60, 0.9) !important; border: 1px solid rgba(99, 102, 241, 0.3) !important; color: #fff !important; border-radius: 10px !important; padding: 8px 12px !important; }
.form-select:focus, .form-control:focus, .selectize-input.focus { border-color: #6366f1 !important; box-shadow: 0 0 15px rgba(99, 102, 241, 0.3) !important; }
.form-label, .control-label, label { color: #fff !important; font-weight: 500 !important; font-size: 0.85rem !important; margin-bottom: 6px !important; }
.selectize-input, .selectize-input input, .selectize-input .item { color: #fff !important; }
.selectize-dropdown { background: rgba(30, 30, 60, 0.98) !important; border: 1px solid rgba(99, 102, 241, 0.3) !important; border-radius: 10px !important; }
.selectize-dropdown-content .option { color: #fff !important; padding: 8px 12px !important; }
.selectize-dropdown-content .option:hover { background: rgba(99, 102, 241, 0.3) !important; }
input[type="date"] { background: rgba(30, 30, 60, 0.9) !important; border: 1px solid rgba(99, 102, 241, 0.3) !important; color: #fff !important; border-radius: 10px !important; }
input[type="date"]::-webkit-calendar-picker-indicator { filter: invert(1); }

/* SCROLLBAR */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: rgba(20, 20, 50, 0.5); }
::-webkit-scrollbar-thumb { background: linear-gradient(135deg, #6366f1, #a855f7); border-radius: 8px; }

/* FOOTER */
.footer { text-align: center; padding: 30px; color: rgba(255, 255, 255, 0.4); font-size: 0.85rem; border-top: 1px solid rgba(255, 255, 255, 0.05); margin-top: 30px; }

/* PLOTLY */
.js-plotly-plot { border-radius: 12px; overflow: visible; width: 100% !important; }
.js-plotly-plot .updatemenu-button { pointer-events: all !important; cursor: pointer !important; }
.js-plotly-plot .slider { pointer-events: all !important; }
.js-plotly-plot .slider-container { pointer-events: all !important; }
.js-plotly-plot .modebar { pointer-events: all !important; }
.chart-section.map-section .js-plotly-plot { overflow: visible !important; }
.chart-section.map-section { overflow: visible !important; }

/* DASHBOARD SECTION */
.dashboard-section { padding: 40px 20px; min-height: 100vh; }

/* GRID DE GRÁFICOS 2x2 */
.charts-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 25px; margin-top: 25px; }
.charts-grid .chart-section { margin-bottom: 0; display: flex; flex-direction: column; min-height: 550px; }
.charts-grid .chart-section .js-plotly-plot, .charts-grid .chart-section .plotly-graph-div { width: 100% !important; }
.charts-grid .chart-section .section-header { padding-bottom: 10px; margin-bottom: 15px; flex-shrink: 0; }
.charts-grid .chart-section .section-number { font-size: 1.8rem; }
.charts-grid .chart-section .section-title { font-size: 1.1rem; }
.charts-grid .chart-section .section-subtitle { font-size: 0.75rem; }
.charts-grid .chart-section .js-plotly-plot { flex: 1; width: 100% !important; }
.charts-grid .chart-section .plotly-graph-div { width: 100% !important; height: 100% !important; }
.charts-grid .chart-section .svg-container { width: 100% !important; height: 100% !important; }
.charts-grid .chart-section .main-svg { width: 100% !important; }

@media (max-width: 1200px) { .charts-grid { grid-template-columns: 1fr; } }

@media (max-width: 992px) {
    .hero-content { flex-direction: column; text-align: center; }
    .hero-text { text-align: center; }
    .hero-description { margin: 0 auto 30px; }
    .hero-kpis { grid-template-columns: repeat(2, 1fr); }
    .hero-visual { display: none; }
    .hero-buttons { justify-content: center; }
    .dashboard-kpis { grid-template-columns: repeat(2, 1fr); }
    .section-page-header { flex-direction: column; text-align: center; }
    .charts-grid { grid-template-columns: 1fr; }
}
</style>
"""

# ═══════════════════════════════════════════════════════════════════════════════
# UI
# ═══════════════════════════════════════════════════════════════════════════════
app_ui = ui.page_fluid(
    ui.HTML(css),
    # ═══════════════════════════════════════════════════════════════════════════
    # PÁGINA DE INICIO
    # ═══════════════════════════════════════════════════════════════════════════
    ui.output_ui("pagina_inicio"),
    # ═══════════════════════════════════════════════════════════════════════════
    # PÁGINA GLOBAL
    # ═══════════════════════════════════════════════════════════════════════════
    ui.output_ui("pagina_global"),
    # ═══════════════════════════════════════════════════════════════════════════
    # PÁGINA POR PAÍS
    # ═══════════════════════════════════════════════════════════════════════════
    ui.output_ui("pagina_pais"),
)


# ═══════════════════════════════════════════════════════════════════════════════
# SERVER
# ═══════════════════════════════════════════════════════════════════════════════
def server(input, output, session):
    # Estado de la página actual
    pagina_actual = reactive.value(PAGINA_INICIO)

    def fmt(n):
        if n >= 1e9:
            return f"{n / 1e9:.2f}B"
        if n >= 1e6:
            return f"{n / 1e6:.2f}M"
        if n >= 1e3:
            return f"{n / 1e3:.1f}K"
        return f"{n:,.0f}"

    # ═══════════════════════════════════════════════════════════════════════════
    # NAVEGACIÓN
    # ═══════════════════════════════════════════════════════════════════════════
    @reactive.effect
    @reactive.event(input.btn_global)
    def ir_global():
        pagina_actual.set(PAGINA_GLOBAL)

    @reactive.effect
    @reactive.event(input.btn_pais)
    def ir_pais():
        pagina_actual.set(PAGINA_PAIS)

    @reactive.effect
    @reactive.event(input.btn_volver_global)
    def volver_inicio_global():
        pagina_actual.set(PAGINA_INICIO)

    @reactive.effect
    @reactive.event(input.btn_volver_pais)
    def volver_inicio_pais():
        pagina_actual.set(PAGINA_INICIO)

    # ═══════════════════════════════════════════════════════════════════════════
    # PÁGINA DE INICIO
    # ═══════════════════════════════════════════════════════════════════════════
    @output
    @render.ui
    def pagina_inicio():
        if pagina_actual() != PAGINA_INICIO:
            return ui.div()

        total_casos = int(df_ultimo["confirmados"].sum())
        total_muertes = int(df_ultimo["muertes"].sum())
        n_paises = df_ultimo["pais"].nunique()
        avg_letalidad = df_ultimo["letalidad_CFR_pct"].mean()

        return ui.div(
            ui.div(
                ui.HTML("""
                <div class="hero-content">
                    <div class="hero-text">
                        <div class="hero-badge">
                            <span class="hero-badge-dot"></span>
                            <span>Dashboard Interactivo</span>
                        </div>
                        <h1 class="hero-title">
                            COVID-19<br>
                            <span class="hero-title-accent">Panel de Análisis 2020</span>
                        </h1>
                        <p class="hero-description">
                            Análisis integral del impacto del COVID-19 correlacionado con indicadores 
                            económicos y de salud. Explora la evolución temporal y compara datos de más de 190 países.
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
                                <!-- Pulmón izquierdo -->
                                <path d="M75,70 Q55,75 50,95 Q45,125 55,150 Q65,170 80,165 Q90,160 90,130 Q90,100 85,85 Q82,75 75,70" fill="url(#lungGrad)" opacity="0.7" filter="url(#glow)">
                                    <animate attributeName="opacity" values="0.6;0.8;0.6" dur="3s" repeatCount="indefinite"/>
                                </path>
                                <!-- Pulmón derecho -->
                                <path d="M125,70 Q145,75 150,95 Q155,125 145,150 Q135,170 120,165 Q110,160 110,130 Q110,100 115,85 Q118,75 125,70" fill="url(#lungGrad)" opacity="0.7" filter="url(#glow)">
                                    <animate attributeName="opacity" values="0.7;0.9;0.7" dur="2.8s" repeatCount="indefinite"/>
                                </path>
                                <!-- Tráquea -->
                                <path d="M100,40 L100,85 M90,85 L100,70 L110,85" stroke="#f97316" stroke-width="4" fill="none" stroke-linecap="round"/>
                                <!-- Virus principal -->
                                <circle cx="140" cy="55" r="20" fill="url(#virusGrad)" filter="url(#glow)">
                                    <animate attributeName="r" values="20;22;20" dur="2s" repeatCount="indefinite"/>
                                </circle>
                                <!-- Spikes del virus -->
                                <g stroke="#a855f7" stroke-width="2" fill="none">
                                    <line x1="140" y1="35" x2="140" y2="25"/><circle cx="140" cy="22" r="4" fill="#a855f7"/>
                                    <line x1="140" y1="75" x2="140" y2="85"/><circle cx="140" cy="88" r="4" fill="#c084fc"/>
                                    <line x1="120" y1="55" x2="110" y2="55"/><circle cx="107" cy="55" r="4" fill="#818cf8"/>
                                    <line x1="160" y1="55" x2="170" y2="55"/><circle cx="173" cy="55" r="4" fill="#a855f7"/>
                                    <line x1="126" y1="41" x2="118" y2="33"/><circle cx="115" cy="30" r="3" fill="#c084fc"/>
                                    <line x1="154" y1="41" x2="162" y2="33"/><circle cx="165" cy="30" r="3" fill="#818cf8"/>
                                    <line x1="126" y1="69" x2="118" y2="77"/><circle cx="115" cy="80" r="3" fill="#a855f7"/>
                                    <line x1="154" y1="69" x2="162" y2="77"/><circle cx="165" cy="80" r="3" fill="#c084fc"/>
                                </g>
                                <!-- Virus secundario pequeño -->
                                <circle cx="55" cy="50" r="12" fill="url(#virusGrad)" opacity="0.6">
                                    <animate attributeName="opacity" values="0.4;0.7;0.4" dur="2.5s" repeatCount="indefinite"/>
                                </circle>
                                <g stroke="#a855f7" stroke-width="1.5" fill="none" opacity="0.6">
                                    <line x1="55" y1="38" x2="55" y2="32"/><circle cx="55" cy="30" r="2.5" fill="#a855f7"/>
                                    <line x1="55" y1="62" x2="55" y2="68"/><circle cx="55" cy="70" r="2.5" fill="#c084fc"/>
                                    <line x1="43" y1="50" x2="37" y2="50"/><circle cx="35" cy="50" r="2.5" fill="#818cf8"/>
                                    <line x1="67" y1="50" x2="73" y2="50"/><circle cx="75" cy="50" r="2.5" fill="#a855f7"/>
                                </g>
                                <!-- Partículas flotantes -->
                                <circle cx="170" cy="140" r="6" fill="#ef4444" opacity="0.4">
                                    <animate attributeName="cy" values="140;130;140" dur="4s" repeatCount="indefinite"/>
                                </circle>
                                <circle cx="35" cy="130" r="4" fill="#f97316" opacity="0.3">
                                    <animate attributeName="cy" values="130;140;130" dur="3.5s" repeatCount="indefinite"/>
                                </circle>
                                <circle cx="160" cy="170" r="5" fill="#a855f7" opacity="0.3">
                                    <animate attributeName="opacity" values="0.2;0.5;0.2" dur="3s" repeatCount="indefinite"/>
                                </circle>
                            </svg>
                        </div>
                    </div>
                </div>
                """),
                # Botones de navegación
                ui.div(
                    ui.input_action_button(
                        "btn_global",
                        ui.HTML(
                            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg> Visualización Global'
                        ),
                        class_="hero-btn hero-btn-primary",
                    ),
                    ui.input_action_button(
                        "btn_pais",
                        ui.HTML(
                            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 2v2m0 16v2M4.93 4.93l1.41 1.41m11.32 11.32l1.41 1.41M2 12h2m16 0h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/></svg> Análisis por País'
                        ),
                        class_="hero-btn hero-btn-secondary",
                    ),
                    class_="hero-buttons",
                ),
                # KPIs pequeños
                ui.HTML(f"""
                <div class="hero-kpis">
                    <div class="hero-kpi">
                        <div class="hero-kpi-value">{fmt(total_casos)}</div>
                        <div class="hero-kpi-label">Casos Totales</div>
                    </div>
                    <div class="hero-kpi">
                        <div class="hero-kpi-value">{fmt(total_muertes)}</div>
                        <div class="hero-kpi-label">Muertes</div>
                    </div>
                    <div class="hero-kpi">
                        <div class="hero-kpi-value">{n_paises}</div>
                        <div class="hero-kpi-label">Países</div>
                    </div>
                    <div class="hero-kpi">
                        <div class="hero-kpi-value">{avg_letalidad:.2f}%</div>
                        <div class="hero-kpi-label">Letalidad</div>
                    </div>
                </div>
                """),
                class_="hero-section",
            ),
            class_="hero-landing",
        )

    # ═══════════════════════════════════════════════════════════════════════════
    # PÁGINA GLOBAL
    # ═══════════════════════════════════════════════════════════════════════════
    @output
    @render.ui
    def pagina_global():
        if pagina_actual() != PAGINA_GLOBAL:
            return ui.div()

        total_casos = int(df_ultimo["confirmados"].sum())
        total_muertes = int(df_ultimo["muertes"].sum())
        n_paises = df_ultimo["pais"].nunique()
        avg_letalidad = df_ultimo["letalidad_CFR_pct"].mean()

        return ui.div(
            # Botón volver
            ui.input_action_button(
                "btn_volver_global",
                ui.HTML(
                    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg> Volver al Inicio'
                ),
                class_="back-button",
            ),
            # Header
            ui.HTML("""
            <div class="section-page-header">
                <div class="section-page-icon global">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
                </div>
                <div>
                    <h1 class="section-page-title">Visualización Global</h1>
                    <p class="section-page-subtitle">Análisis comparativo de todos los países del mundo</p>
                </div>
            </div>
            """),
            # KPIs
            ui.HTML(f"""
            <div class="dashboard-kpis">
                <div class="dashboard-kpi">
                    <div class="dashboard-kpi-icon casos"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 2v4m0 12v4M2 12h4m12 0h4"/></svg></div>
                    <div class="dashboard-kpi-value casos">{fmt(total_casos)}</div>
                    <div class="dashboard-kpi-label">Casos Confirmados</div>
                </div>
                <div class="dashboard-kpi">
                    <div class="dashboard-kpi-icon muertes"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg></div>
                    <div class="dashboard-kpi-value muertes">{fmt(total_muertes)}</div>
                    <div class="dashboard-kpi-label">Muertes Totales</div>
                </div>
                <div class="dashboard-kpi">
                    <div class="dashboard-kpi-icon paises"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M2 12h20"/></svg></div>
                    <div class="dashboard-kpi-value paises">{n_paises}</div>
                    <div class="dashboard-kpi-label">Países Analizados</div>
                </div>
                <div class="dashboard-kpi">
                    <div class="dashboard-kpi-icon letalidad"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg></div>
                    <div class="dashboard-kpi-value letalidad">{avg_letalidad:.2f}%</div>
                    <div class="dashboard-kpi-label">Tasa de Letalidad</div>
                </div>
            </div>
            """),
            # Gráficos globales - Mapa grande (fila completa)
            ui.div(
                ui.div(
                    ui.span("01", class_="section-number"),
                    ui.div(
                        ui.div("Mapa Global de Incidencia", class_="section-title"),
                        ui.div(
                            "Distribución geográfica de casos por 100.000 habitantes",
                            class_="section-subtitle",
                        ),
                    ),
                    class_="section-header",
                ),
                ui.output_ui("chart_mapa_global"),
                class_="chart-section map-section",
            ),
            # Grid 2x2 de gráficos
            ui.div(
                # Olas de Contagio (Ridgeline)
                ui.div(
                    ui.div(
                        ui.span("02", class_="section-number"),
                        ui.div(
                            ui.div("Olas de Contagio", class_="section-title"),
                            ui.div(
                                "Comparación de olas entre países (normalizado)",
                                class_="section-subtitle",
                            ),
                        ),
                        class_="section-header",
                    ),
                    ui.row(
                        ui.column(
                            12,
                            ui.input_selectize(
                                "paises_wave",
                                "Seleccionar países:",
                                choices=paises,
                                selected=paises[:5],
                                multiple=True,
                            ),
                        ),
                    ),
                    output_widget("chart_wave_global"),
                    class_="chart-section",
                ),
                # Dumbbell - Incremento de Incidencia
                ui.div(
                    ui.div(
                        ui.span("03", class_="section-number"),
                        ui.div(
                            ui.div("Incremento de Incidencia", class_="section-title"),
                            ui.div(
                                "Crecimiento desde inicio a fin del período",
                                class_="section-subtitle",
                            ),
                        ),
                        class_="section-header",
                    ),
                    ui.row(
                        ui.column(
                            6,
                            ui.input_selectize(
                                "paises_dumbbell",
                                "Seleccionar países:",
                                choices=paises,
                                selected=paises[:10],
                                multiple=True,
                            ),
                        ),
                        ui.column(
                            3,
                            ui.input_date(
                                "fecha_inicio_dumbbell",
                                "Fecha inicio:",
                                value=fecha_min,
                                min=fecha_min,
                                max=fecha_max,
                            ),
                        ),
                        ui.column(
                            3,
                            ui.input_date(
                                "fecha_fin_dumbbell",
                                "Fecha fin:",
                                value=fecha_max,
                                min=fecha_min,
                                max=fecha_max,
                            ),
                        ),
                    ),
                    output_widget("chart_dumbbell_global"),
                    class_="chart-section",
                ),
                # Matriz de Eficiencia Sanitaria
                ui.div(
                    ui.div(
                        ui.span("04", class_="section-number"),
                        ui.div(
                            ui.div(
                                "Gasto en Salud vs Letalidad", class_="section-title"
                            ),
                            ui.div(
                                "Inversión sanitaria y tasa de letalidad",
                                class_="section-subtitle",
                            ),
                        ),
                        class_="section-header",
                    ),
                    output_widget("chart_salud_global"),
                    class_="chart-section",
                ),
                ui.div(
                    ui.div(
                        ui.span("05", class_="section-number"),
                        ui.div(
                            ui.div(
                                "Matriz de Eficiencia Sanitaria", class_="section-title"
                            ),
                            ui.div(
                                "Incidencia vs Letalidad por país",
                                class_="section-subtitle",
                            ),
                        ),
                        class_="section-header",
                    ),
                    ui.row(
                        ui.column(
                            12,
                            ui.input_selectize(
                                "paises_efficiency",
                                "Filtrar países (vacío = todos):",
                                choices=paises,
                                selected=[],
                                multiple=True,
                            ),
                        ),
                    ),
                    output_widget("chart_efficiency_global"),
                    class_="chart-section",
                ),
                class_="charts-grid",
            ),
            ui.HTML(
                '<div class="footer">Dashboard COVID-19 2020 | Datos: WHO & World Bank | Shiny for Python + Plotly</div>'
            ),
            class_="container-fluid px-4 dashboard-section",
            style="padding-top: 80px;",
        )

    # ═══════════════════════════════════════════════════════════════════════════
    # PÁGINA POR PAÍS
    # ═══════════════════════════════════════════════════════════════════════════
    @output
    @render.ui
    def pagina_pais():
        if pagina_actual() != PAGINA_PAIS:
            return ui.div()

        return ui.div(
            # Botón volver
            ui.input_action_button(
                "btn_volver_pais",
                ui.HTML(
                    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg> Volver al Inicio'
                ),
                class_="back-button",
            ),
            # Header
            ui.HTML("""
            <div class="section-page-header">
                <div class="section-page-icon pais">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 2v2m0 16v2M4.93 4.93l1.41 1.41m11.32 11.32l1.41 1.41M2 12h2m16 0h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/></svg>
                </div>
                <div>
                    <h1 class="section-page-title">Análisis por País</h1>
                    <p class="section-page-subtitle">Explora los datos detallados de cada país</p>
                </div>
            </div>
            """),
            # Filtros
            ui.div(
                ui.div(
                    ui.HTML(
                        '<div class="filter-title"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:18px;height:18px;vertical-align:middle;margin-right:8px"><path d="M22 3H2l8 9.46V19l4 2v-8.54L22 3z"/></svg>Selecciona un País</div>'
                    ),
                    class_="filter-header",
                ),
                ui.row(
                    ui.column(
                        4,
                        ui.input_selectize(
                            "pais_select",
                            "País:",
                            choices=paises,
                            selected=paises[0] if paises else None,
                        ),
                    ),
                    ui.column(
                        4,
                        ui.input_date(
                            "fecha_inicio",
                            "Fecha inicio:",
                            value=fecha_min,
                            min=fecha_min,
                            max=fecha_max,
                        ),
                    ),
                    ui.column(
                        4,
                        ui.input_date(
                            "fecha_fin",
                            "Fecha fin:",
                            value=fecha_max,
                            min=fecha_min,
                            max=fecha_max,
                        ),
                    ),
                ),
                class_="filter-panel",
            ),
            # KPIs del país
            ui.output_ui("kpis_pais"),
            # Gráficos por país - Primera fila con dos gráficos
            ui.div(
                ui.div(
                    ui.div(
                        ui.span("01", class_="section-number"),
                        ui.div(
                            ui.div("Evolución Temporal", class_="section-title"),
                            ui.div(
                                "Evolución de casos confirmados a lo largo del tiempo",
                                class_="section-subtitle",
                            ),
                        ),
                        class_="section-header",
                    ),
                    output_widget("chart_temporal_pais"),
                    class_="chart-section",
                ),
                ui.div(
                    ui.div(
                        ui.span("02", class_="section-number"),
                        ui.div(
                            ui.div("Comparativa Mundial", class_="section-title"),
                            ui.div(
                                "Comparación del país con la media mundial",
                                class_="section-subtitle",
                            ),
                        ),
                        class_="section-header",
                    ),
                    output_widget("chart_gauge_pais"),
                    class_="chart-section",
                ),
                class_="charts-row",
            ),
            # Fila: Casos y Muertes lado a lado
            ui.div(
                ui.div(
                    ui.div(
                        ui.span("03", class_="section-number"),
                        ui.div(
                            ui.div("Casos por Mes", class_="section-title"),
                            ui.div(
                                "Nuevos contagios mensuales",
                                class_="section-subtitle",
                            ),
                        ),
                        class_="section-header",
                    ),
                    output_widget("chart_casos_mes"),
                    class_="chart-section",
                ),
                ui.div(
                    ui.div(
                        ui.span("04", class_="section-number"),
                        ui.div(
                            ui.div("Muertes por Mes", class_="section-title"),
                            ui.div(
                                "Fallecimientos mensuales",
                                class_="section-subtitle",
                            ),
                        ),
                        class_="section-header",
                    ),
                    output_widget("chart_muertes_mes"),
                    class_="chart-section",
                ),
                class_="charts-row",
            ),
            # Mensaje de relación entre casos y muertes
            ui.div(
                ui.output_ui("mensaje_relacion_picos"),
                style="text-align: center; margin-top: -10px; margin-bottom: 20px;",
            ),
            ui.HTML(
                '<div class="footer">Dashboard COVID-19 2020 | Datos: WHO & World Bank | Shiny for Python + Plotly</div>'
            ),
            class_="container-fluid px-4 dashboard-section",
            style="padding-top: 80px;",
        )

    # ═══════════════════════════════════════════════════════════════════════════
    # DATOS FILTRADOS POR PAÍS
    # ═══════════════════════════════════════════════════════════════════════════
    @reactive.calc
    def datos_pais_filtrados():
        if pagina_actual() != PAGINA_PAIS:
            return df.head(0)
        try:
            pais_sel = input.pais_select()
            data = df[df["pais"] == pais_sel].copy()
            if input.fecha_inicio() and input.fecha_fin():
                data = data[
                    (data["fecha"] >= pd.to_datetime(input.fecha_inicio()))
                    & (data["fecha"] <= pd.to_datetime(input.fecha_fin()))
                ]
            return data
        except:
            return df.head(0)

    # ═══════════════════════════════════════════════════════════════════════════
    # KPIs DEL PAÍS
    # ═══════════════════════════════════════════════════════════════════════════
    @output
    @render.ui
    def kpis_pais():
        data = datos_pais_filtrados()
        if len(data) == 0:
            return ui.div()

        ultimo = data.loc[data["fecha"].idxmax()]
        total_casos = int(ultimo["confirmados"])
        total_muertes = int(ultimo["muertes"])
        incidencia = ultimo["IA_100k"]
        letalidad = ultimo["letalidad_CFR_pct"]
        gasto_salud = ultimo["gasto_salud_pib"] if "gasto_salud_pib" in ultimo else 0

        return ui.HTML(f"""
        <div class="dashboard-kpis">
            <div class="dashboard-kpi">
                <div class="dashboard-kpi-icon casos"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 2v4m0 12v4M2 12h4m12 0h4"/></svg></div>
                <div class="dashboard-kpi-value casos">{fmt(total_casos)}</div>
                <div class="dashboard-kpi-label">Casos Confirmados</div>
            </div>
            <div class="dashboard-kpi">
                <div class="dashboard-kpi-icon muertes"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg></div>
                <div class="dashboard-kpi-value muertes">{fmt(total_muertes)}</div>
                <div class="dashboard-kpi-label">Muertes Totales</div>
            </div>
            <div class="dashboard-kpi">
                <div class="dashboard-kpi-icon paises"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg></div>
                <div class="dashboard-kpi-value paises">{incidencia:,.1f}</div>
                <div class="dashboard-kpi-label">Incidencia/100k</div>
            </div>
            <div class="dashboard-kpi">
                <div class="dashboard-kpi-icon letalidad"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg></div>
                <div class="dashboard-kpi-value letalidad">{letalidad:.2f}%</div>
                <div class="dashboard-kpi-label">Tasa de Letalidad</div>
            </div>
            <div class="dashboard-kpi">
                <div class="dashboard-kpi-icon salud"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/></svg></div>
                <div class="dashboard-kpi-value salud">{gasto_salud:.1f}%</div>
                <div class="dashboard-kpi-label">Gasto Salud/PIB</div>
            </div>
        </div>
        """)

    # ═══════════════════════════════════════════════════════════════════════════
    # GRÁFICOS GLOBALES
    # ═══════════════════════════════════════════════════════════════════════════
    @render.ui
    def chart_mapa_global():
        # Prepare data for animation - group by week for smoother playback
        data_anim = df.copy()
        data_anim["semana"] = (
            data_anim["fecha"].dt.to_period("W").apply(lambda x: x.start_time)
        )
        data_anim["semana_str"] = data_anim["semana"].dt.strftime("%Y-%m-%d")

        # Calculate weekly incidence properly:
        # Sum daily cases for the week, then calculate incidence per 100k
        data_weekly = (
            data_anim.groupby(["pais", "iso3c", "semana_str"])
            .agg(
                {
                    "confirmados_dia": "sum",  # Sum of daily cases in the week
                    "muertes_dia": "sum",  # Sum of daily deaths in the week
                    "confirmados": "max",  # Cumulative cases at end of week
                    "muertes": "max",  # Cumulative deaths at end of week
                    "letalidad_CFR_pct": "last",  # Lethality at end of week
                    "poblacion": "first",
                }
            )
            .reset_index()
        )

        # Calculate weekly incidence per 100k population
        data_weekly["IA_100k_semanal"] = (
            data_weekly["confirmados_dia"] / data_weekly["poblacion"] * 100000
        ).fillna(0)

        # Sort by date for proper animation order
        data_weekly = data_weekly.sort_values("semana_str")

        # Get max value for consistent color scale (use 95th percentile to avoid outliers)
        max_incidencia = data_weekly["IA_100k_semanal"].quantile(0.95)
        if max_incidencia == 0:
            max_incidencia = data_weekly["IA_100k_semanal"].max()
        if max_incidencia == 0:
            max_incidencia = 100  # Default fallback

        # Get sorted unique weeks
        weeks = sorted(data_weekly["semana_str"].unique())

        # Create frames for animation
        frames = []
        for week in weeks:
            week_data = data_weekly[data_weekly["semana_str"] == week]
            frames.append(
                go.Frame(
                    data=[
                        go.Choropleth(
                            locations=week_data["iso3c"],
                            z=week_data["IA_100k_semanal"],
                            text=week_data["pais"],
                            colorscale=[
                                [0, "#0f0a2e"],
                                [0.1, "#1e1b4b"],
                                [0.25, "#3730a3"],
                                [0.4, "#4f46e5"],
                                [0.55, "#6366f1"],
                                [0.7, "#818cf8"],
                                [0.85, "#a5b4fc"],
                                [1, "#e0e7ff"],
                            ],
                            zmin=0,
                            zmax=max_incidencia,
                            colorbar=dict(
                                title=dict(
                                    text="Incidencia<br>Semanal/100k",
                                    font=dict(size=11, color="white"),
                                ),
                                thickness=18,
                                len=0.75,
                                x=0.98,
                                bgcolor="rgba(15,15,40,0.9)",
                                bordercolor="rgba(99,102,241,0.4)",
                                borderwidth=1,
                                tickfont=dict(color="rgba(255,255,255,0.8)", size=10),
                                tickformat=",.1f",
                            ),
                            hovertemplate="<b>%{text}</b><br>Incidencia: %{z:,.1f}/100k<extra></extra>",
                        )
                    ],
                    name=week,
                )
            )

        # Initial data (first week)
        first_week_data = data_weekly[data_weekly["semana_str"] == weeks[0]]

        fig = go.Figure(
            data=[
                go.Choropleth(
                    locations=first_week_data["iso3c"],
                    z=first_week_data["IA_100k_semanal"],
                    text=first_week_data["pais"],
                    colorscale=[
                        [0, "#0f0a2e"],
                        [0.1, "#1e1b4b"],
                        [0.25, "#3730a3"],
                        [0.4, "#4f46e5"],
                        [0.55, "#6366f1"],
                        [0.7, "#818cf8"],
                        [0.85, "#a5b4fc"],
                        [1, "#e0e7ff"],
                    ],
                    zmin=0,
                    zmax=max_incidencia,
                    colorbar=dict(
                        title=dict(
                            text="Incidencia<br>Semanal/100k",
                            font=dict(size=11, color="white"),
                        ),
                        thickness=18,
                        len=0.75,
                        x=0.98,
                        bgcolor="rgba(15,15,40,0.9)",
                        bordercolor="rgba(99,102,241,0.4)",
                        borderwidth=1,
                        tickfont=dict(color="rgba(255,255,255,0.8)", size=10),
                        tickformat=",.1f",
                    ),
                    hovertemplate="<b>%{text}</b><br>Incidencia: %{z:,.1f}/100k<extra></extra>",
                )
            ],
            frames=frames,
        )

        # Create slider steps
        sliders = [
            dict(
                active=0,
                yanchor="top",
                xanchor="left",
                currentvalue=dict(
                    font=dict(size=14, color="white"),
                    prefix="Semana: ",
                    visible=True,
                    xanchor="center",
                ),
                transition=dict(duration=200),
                pad=dict(b=10, t=30),
                len=0.85,
                x=0.1,
                y=0,
                steps=[
                    dict(
                        args=[
                            [week],
                            dict(
                                frame=dict(duration=200, redraw=True),
                                mode="immediate",
                                transition=dict(duration=200),
                            ),
                        ],
                        label=week,
                        method="animate",
                    )
                    for week in weeks
                ],
            )
        ]

        fig.update_geos(
            showframe=False,
            showcoastlines=True,
            coastlinecolor="rgba(99,102,241,0.5)",
            coastlinewidth=0.5,
            projection_type="natural earth",
            bgcolor="rgba(0,0,0,0)",
            landcolor="rgba(20,20,45,0.95)",
            oceancolor="rgba(8,8,25,1)",
            showland=True,
            showcountries=True,
            countrycolor="rgba(99,102,241,0.25)",
            countrywidth=0.3,
        )

        fig.update_layout(
            height=600,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="rgba(255,255,255,0.8)"),
            margin=dict(l=0, r=0, t=10, b=100),
            sliders=sliders,
            updatemenus=[
                dict(
                    type="buttons",
                    showactive=False,
                    y=0,
                    x=0.02,
                    xanchor="left",
                    yanchor="top",
                    pad=dict(t=30, r=10),
                    buttons=[
                        dict(
                            label="▶ Play",
                            method="animate",
                            args=[
                                None,
                                dict(
                                    frame=dict(duration=400, redraw=True),
                                    fromcurrent=True,
                                    transition=dict(
                                        duration=200, easing="quadratic-in-out"
                                    ),
                                ),
                            ],
                        ),
                        dict(
                            label="⏸ Pause",
                            method="animate",
                            args=[
                                [None],
                                dict(
                                    frame=dict(duration=0, redraw=False),
                                    mode="immediate",
                                    transition=dict(duration=0),
                                ),
                            ],
                        ),
                    ],
                    font=dict(color="white", size=11),
                    bgcolor="rgba(99,102,241,0.9)",
                    bordercolor="rgba(168,85,247,0.8)",
                    borderwidth=2,
                )
            ],
        )

        # Return HTML directly to support animations (FigureWidget doesn't support frames)
        return ui.HTML(fig.to_html(include_plotlyjs="cdn", full_html=False))

    @render_widget
    def chart_wave_global():
        """Ridgeline Plot - Olas de Contagio"""
        selected_countries = input.paises_wave()
        if not selected_countries or len(selected_countries) == 0:
            selected_countries = paises[:5]

        data = df[df["pais"].isin(selected_countries)].copy()

        if len(data) == 0:
            fig = go.Figure()
            fig.add_annotation(
                text="No hay datos disponibles",
                x=0.5,
                y=0.5,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=16, color="rgba(255,255,255,0.6)"),
            )
            fig.update_layout(
                height=500, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
            )
            return fig

        # Agrupar por semana
        data["semana"] = data["fecha"].dt.to_period("W").apply(lambda x: x.start_time)
        data_semanal = (
            data.groupby(["pais", "semana"])
            .agg({"confirmados_dia": "sum"})
            .reset_index()
        )

        # Normalizar por país
        max_by_country = data_semanal.groupby("pais")["confirmados_dia"].transform(
            "max"
        )
        data_semanal["confirmados_norm"] = data_semanal[
            "confirmados_dia"
        ] / max_by_country.replace(0, 1)

        fig = go.Figure()
        country_colors = px.colors.qualitative.Set2
        countries = list(reversed(selected_countries))
        offset_step = 1.0

        for i, country in enumerate(countries):
            country_data = data_semanal[data_semanal["pais"] == country].sort_values(
                "semana"
            )
            if len(country_data) == 0:
                continue
            offset = i * offset_step
            color = country_colors[i % len(country_colors)]
            x_vals = country_data["semana"].tolist()
            y_vals = (country_data["confirmados_norm"] + offset).tolist()
            y_base = [offset] * len(x_vals)
            fig.add_trace(
                go.Scatter(
                    x=x_vals + x_vals[::-1],
                    y=y_vals + y_base[::-1],
                    fill="toself",
                    fillcolor=color.replace("rgb", "rgba").replace(")", ",0.4)")
                    if "rgb" in color
                    else color + "66",
                    line=dict(color=color, width=1.5),
                    name=country,
                    hovertemplate=f"<b>{country}</b><br>Semana: %{{x|%Y-%m-%d}}<br>Casos: %{{customdata:,.0f}}<extra></extra>",
                    customdata=country_data["confirmados_dia"].tolist()
                    + country_data["confirmados_dia"].tolist()[::-1],
                )
            )

        fig.update_layout(
            autosize=True,
            height=None,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="rgba(255,255,255,0.8)"),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                bgcolor="rgba(20,20,50,0.7)",
                bordercolor="rgba(99,102,241,0.3)",
                borderwidth=1,
            ),
            xaxis=dict(
                title=dict(text="Tiempo", font=dict(size=13, color="rgba(255,255,255,0.9)")),
                gridcolor="rgba(255,255,255,0.1)",
                showline=True,
                linecolor="rgba(99,102,241,0.3)",
                tickfont=dict(size=12, color="rgba(255,255,255,0.9)"),
            ),
            yaxis=dict(
                title=dict(text="Intensidad (normalizado)", font=dict(size=13, color="rgba(255,255,255,0.9)")),
                gridcolor="rgba(255,255,255,0.05)",
                showticklabels=False,
            ),
            margin=dict(l=60, r=30, t=50, b=60),
        )
        return fig

    @render_widget
    def chart_dumbbell_global():
        """Dumbbell Plot - Incremento de Incidencia"""
        selected_countries = input.paises_dumbbell()
        if not selected_countries or len(selected_countries) == 0:
            selected_countries = paises[:10]

        # Get date filters
        fecha_inicio_sel = pd.to_datetime(input.fecha_inicio_dumbbell())
        fecha_fin_sel = pd.to_datetime(input.fecha_fin_dumbbell())

        # Filter by countries and date range
        data = df[
            (df["pais"].isin(selected_countries))
            & (df["fecha"] >= fecha_inicio_sel)
            & (df["fecha"] <= fecha_fin_sel)
        ].copy()

        if len(data) == 0:
            fig = go.Figure()
            fig.add_annotation(
                text="No hay datos disponibles para el rango seleccionado",
                x=0.5,
                y=0.5,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=16, color="rgba(255,255,255,0.6)"),
            )
            fig.update_layout(
                height=500, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
            )
            return fig

        data_inicio = data.loc[data.groupby("pais")["fecha"].idxmin()][
            ["pais", "IA_100k", "fecha"]
        ].copy()
        data_inicio.columns = ["pais", "IA_100k_inicio", "fecha_inicio"]
        data_fin = data.loc[data.groupby("pais")["fecha"].idxmax()][
            ["pais", "IA_100k", "fecha"]
        ].copy()
        data_fin.columns = ["pais", "IA_100k_fin", "fecha_fin"]
        data_dumbbell = data_inicio.merge(data_fin, on="pais")
        data_dumbbell["incremento"] = (
            data_dumbbell["IA_100k_fin"] - data_dumbbell["IA_100k_inicio"]
        )
        data_dumbbell = data_dumbbell.sort_values("IA_100k_fin", ascending=True)

        fig = go.Figure()
        for _, row in data_dumbbell.iterrows():
            fig.add_trace(
                go.Scatter(
                    x=[row["IA_100k_inicio"], row["IA_100k_fin"]],
                    y=[row["pais"], row["pais"]],
                    mode="lines",
                    line=dict(color="rgba(148,163,184,0.6)", width=2),
                    showlegend=False,
                    hoverinfo="skip",
                )
            )
        fig.add_trace(
            go.Scatter(
                x=data_dumbbell["IA_100k_inicio"],
                y=data_dumbbell["pais"],
                mode="markers",
                marker=dict(
                    color="#10b981", size=12, line=dict(color="white", width=1)
                ),
                name="Inicio",
                hovertemplate="<b>%{y}</b><br>Incidencia Inicio: %{x:.1f}/100k<extra></extra>",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=data_dumbbell["IA_100k_fin"],
                y=data_dumbbell["pais"],
                mode="markers",
                marker=dict(
                    color="#ef4444", size=12, line=dict(color="white", width=1)
                ),
                name="Fin",
                hovertemplate="<b>%{y}</b><br>Incidencia Final: %{x:.1f}/100k<br>Incremento: +%{customdata:.1f}/100k<extra></extra>",
                customdata=data_dumbbell["incremento"],
            )
        )
        fig.update_layout(
            autosize=True,
            height=None,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="rgba(255,255,255,0.8)"),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                bgcolor="rgba(20,20,50,0.7)",
                bordercolor="rgba(99,102,241,0.3)",
                borderwidth=1,
            ),
            xaxis=dict(
                title="Incidencia Acumulada (por 100k)",
                gridcolor="rgba(255,255,255,0.1)",
                showline=True,
                linecolor="rgba(99,102,241,0.3)",
            ),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont=dict(size=10)),
            margin=dict(l=100, r=30, t=50, b=60),
        )
        return fig

    @render_widget
    def chart_salud_global():
        data = df_ultimo[df_ultimo["gasto_salud_pib"] > 0].copy()

        fig = px.scatter(
            data,
            x="gasto_salud_pib",
            y="letalidad_CFR_pct",
            size="poblacion",
            color="pib_per_capita_2019",
            hover_name="pais",
            color_continuous_scale=["#10b981", "#fbbf24", "#ef4444"],
            labels={
                "gasto_salud_pib": "Gasto Salud (%PIB)",
                "letalidad_CFR_pct": "Letalidad (%)",
            },
        )
        fig.update_layout(
            autosize=True,
            height=None,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="rgba(255,255,255,0.9)", size=12),
            xaxis=dict(gridcolor="rgba(255,255,255,0.1)", tickfont=dict(size=12, color="rgba(255,255,255,0.9)")),
            yaxis=dict(gridcolor="rgba(255,255,255,0.1)", tickfont=dict(size=12, color="rgba(255,255,255,0.9)")),
            margin=dict(l=50, r=15, t=10, b=40),
        )
        return fig

    @render_widget
    def chart_efficiency_global():
        """Matriz de Eficiencia Sanitaria - Incidencia vs Letalidad"""
        selected_countries = input.paises_efficiency()
        data = df_ultimo[
            (df_ultimo["gasto_salud_pib"] > 0) & (df_ultimo["IA_100k"] > 0)
        ].copy()

        if selected_countries and len(selected_countries) > 0:
            data = data[data["pais"].isin(selected_countries)].copy()

        if len(data) == 0:
            fig = go.Figure()
            fig.add_annotation(
                text="No hay datos disponibles",
                x=0.5,
                y=0.5,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=16, color="rgba(255,255,255,0.6)"),
            )
            fig.update_layout(
                height=350, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
            )
            return fig

        median_incidencia = data["IA_100k"].median()
        median_letalidad = data["letalidad_CFR_pct"].median()
        max_pop = data["poblacion"].max()
        data["size"] = (data["poblacion"] / max_pop * 40) + 5

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=data["IA_100k"],
                y=data["letalidad_CFR_pct"],
                mode="markers",
                marker=dict(
                    size=data["size"],
                    color=data["gasto_salud_pib"],
                    colorscale="Viridis",
                    opacity=0.7,
                    line=dict(width=1, color="rgba(255,255,255,0.3)"),
                    colorbar=dict(
                        title="Gasto Salud<br>(% PIB)",
                        thickness=15,
                        len=0.6,
                        bgcolor="rgba(20,20,50,0.8)",
                        bordercolor="rgba(99,102,241,0.3)",
                        tickfont=dict(color="rgba(255,255,255,0.7)"),
                    ),
                    sizemode="diameter",
                ),
                text=data["pais"],
                customdata=data[
                    [
                        "confirmados",
                        "muertes",
                        "poblacion",
                        "gasto_salud_pib",
                        "pib_per_capita_2019",
                    ]
                ].values,
                hovertemplate="<b>%{text}</b><br><br>Incidencia: %{x:.1f}/100k<br>Letalidad: %{y:.2f}%<br>Gasto Salud: %{customdata[3]:.1f}% PIB<br>PIB/cápita: $%{customdata[4]:,.0f}<extra></extra>",
                showlegend=False,
            )
        )
        fig.add_hline(
            y=median_letalidad,
            line=dict(color="rgba(255,255,255,0.4)", width=1, dash="dash"),
            annotation_text=f"Letalidad media: {median_letalidad:.2f}%",
            annotation_position="top right",
            annotation_font=dict(size=9, color="rgba(255,255,255,0.6)"),
        )
        fig.add_vline(
            x=median_incidencia,
            line=dict(color="rgba(255,255,255,0.4)", width=1, dash="dash"),
            annotation_text=f"Incidencia media: {median_incidencia:.0f}",
            annotation_position="top right",
            annotation_font=dict(size=9, color="rgba(255,255,255,0.6)"),
        )

        x_min, x_max = data["IA_100k"].min(), data["IA_100k"].max()
        y_min, y_max = data["letalidad_CFR_pct"].min(), data["letalidad_CFR_pct"].max()
        x_padding = (x_max - x_min) * 0.1
        y_padding = (y_max - y_min) * 0.15

        fig.update_layout(
            autosize=True,
            height=None,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="rgba(255,255,255,0.8)", size=10),
            xaxis=dict(
                title="Incidencia (por 100k)",
                gridcolor="rgba(255,255,255,0.1)",
                showline=True,
                linecolor="rgba(99,102,241,0.3)",
                range=[max(0, x_min - x_padding), x_max + x_padding],
            ),
            yaxis=dict(
                title="Letalidad (%)",
                gridcolor="rgba(255,255,255,0.1)",
                showline=True,
                linecolor="rgba(99,102,241,0.3)",
                range=[max(0, y_min - y_padding), y_max + y_padding],
            ),
            margin=dict(l=50, r=15, t=10, b=40),
        )
        return fig

    # ═══════════════════════════════════════════════════════════════════════════
    # GRÁFICOS POR PAÍS
    # ═══════════════════════════════════════════════════════════════════════════
    @render_widget
    def chart_temporal_pais():
        data = datos_pais_filtrados()
        if len(data) == 0:
            fig = go.Figure()
            fig.update_layout(
                height=500, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
            )
            return fig

        data = data.copy()
        data["mes"] = data["fecha"].dt.to_period("M").astype(str)
        data_mes = data.groupby("mes").agg({"confirmados": "max"}).reset_index()

        fig = px.line(
            data_mes,
            x="mes",
            y="confirmados",
            labels={"mes": "Mes", "confirmados": "Casos Acumulados"},
            color_discrete_sequence=["#6366f1"],
            markers=True,
        )
        fig.update_layout(
            height=400,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="rgba(255,255,255,0.9)", size=12),
            xaxis=dict(gridcolor="rgba(255,255,255,0.1)", tickangle=-45, tickfont=dict(size=12, color="rgba(255,255,255,0.9)")),
            yaxis=dict(gridcolor="rgba(255,255,255,0.1)", tickfont=dict(size=12, color="rgba(255,255,255,0.9)")),
            margin=dict(l=50, r=20, t=30, b=80),
        )
        return fig

    @render_widget
    def chart_gauge_pais():
        data = datos_pais_filtrados()
        if len(data) == 0:
            fig = go.Figure()
            fig.update_layout(
                height=500, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
            )
            return fig

        # Datos del país seleccionado
        ultimo = data.loc[data["fecha"].idxmax()]
        pais_letalidad = ultimo["letalidad_CFR_pct"]
        pais_incidencia = ultimo["IA_100k"]
        pais_mortalidad = ultimo["tasa_mortalidad_100k"]
        pais_gasto_salud = ultimo["gasto_salud_pib"] if "gasto_salud_pib" in ultimo else 0
        pais_nombre = input.pais_select()

        # Medias mundiales
        media_letalidad = df_ultimo["letalidad_CFR_pct"].mean()
        media_incidencia = df_ultimo["IA_100k"].mean()
        media_mortalidad = df_ultimo["tasa_mortalidad_100k"].mean()
        media_gasto_salud = df_ultimo["gasto_salud_pib"].mean()

        # Datos para el gráfico
        categorias = ["Letalidad (%)", "Incidencia/100k", "Mort./100k", "Gasto Salud (%)"]
        valores_pais = [pais_letalidad, pais_incidencia / 100, pais_mortalidad / 10, pais_gasto_salud]
        valores_media = [media_letalidad, media_incidencia / 100, media_mortalidad / 10, media_gasto_salud]

        fig = go.Figure()

        # Barras del país
        fig.add_trace(go.Bar(
            name=pais_nombre,
            x=categorias,
            y=valores_pais,
            marker_color="#6366f1",
            marker_line_color="#818cf8",
            marker_line_width=2,
            text=[f"{pais_letalidad:.2f}%", f"{pais_incidencia:,.0f}", f"{pais_mortalidad:,.0f}", f"{pais_gasto_salud:.1f}%"],
            textposition="outside",
            textfont=dict(color="#818cf8", size=13, weight="bold"),
        ))

        # Barras de la media mundial
        fig.add_trace(go.Bar(
            name="Media Mundial",
            x=categorias,
            y=valores_media,
            marker_color="#a855f7",
            marker_line_color="#c084fc",
            marker_line_width=2,
            text=[f"{media_letalidad:.2f}%", f"{media_incidencia:,.0f}", f"{media_mortalidad:,.0f}", f"{media_gasto_salud:.1f}%"],
            textposition="outside",
            textfont=dict(color="#c084fc", size=13, weight="bold"),
        ))

        fig.update_layout(
            barmode="group",
            height=500,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="rgba(255,255,255,0.8)"),
            xaxis=dict(
                gridcolor="rgba(255,255,255,0.1)",
                tickfont=dict(size=13, color="rgba(255,255,255,0.95)"),
                tickangle=0,
            ),
            yaxis=dict(
                gridcolor="rgba(255,255,255,0.1)",
                title="Valor (normalizado)",
                showticklabels=False,
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                bgcolor="rgba(0,0,0,0)",
            ),
            margin=dict(l=40, r=20, t=60, b=60),
            bargap=0.3,
            bargroupgap=0.1,
        )
        return fig

    @render_widget
    def chart_casos_mes():
        """Gráfico de barras: casos por mes"""
        data = datos_pais_filtrados()
        if len(data) == 0:
            fig = go.Figure()
            fig.update_layout(
                height=500, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
            )
            return fig

        data = data.sort_values("fecha").copy()
        data["mes"] = data["fecha"].dt.to_period("M")
        data_mes = data.groupby("mes").agg({"confirmados_dia": "sum"}).reset_index()
        data_mes["mes_str"] = data_mes["mes"].dt.strftime("%b")
        
        # Encontrar el máximo
        idx_max = data_mes["confirmados_dia"].idxmax()
        colores = ["#a855f7" if i != idx_max else "#22c55e" for i in range(len(data_mes))]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=data_mes["mes_str"],
            y=data_mes["confirmados_dia"],
            marker_color=colores,
            marker_line_color="#c084fc",
            marker_line_width=1,
            hovertemplate="<b>%{x}</b><br>Casos: %{y:,.0f}<extra></extra>",
            text=[f"{v/1000:.0f}k" if v >= 1000 else str(int(v)) for v in data_mes["confirmados_dia"]],
            textposition="outside",
            textfont=dict(color="rgba(255,255,255,0.95)", size=13, weight="bold"),
        ))

        max_val = data_mes["confirmados_dia"].max()
        mes_pico = data_mes.loc[idx_max, "mes_str"]

        fig.update_layout(
            autosize=True,
            height=500,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="rgba(255,255,255,0.9)", size=12),
            xaxis=dict(
                title=dict(text="Mes 2020", font=dict(size=13)),
                gridcolor="rgba(255,255,255,0.05)",
                tickfont=dict(size=13, color="rgba(255,255,255,0.95)"),
            ),
            yaxis=dict(
                title=dict(text="Casos", font=dict(size=13)),
                gridcolor="rgba(255,255,255,0.1)",
                tickfont=dict(size=11, color="rgba(255,255,255,0.8)"),
            ),
            margin=dict(l=60, r=20, t=40, b=60),
            bargap=0.3,
            annotations=[
                dict(
                    x=mes_pico,
                    y=max_val,
                    text="▲ PICO",
                    showarrow=False,
                    font=dict(color="#22c55e", size=12, weight="bold"),
                    yshift=25,
                )
            ]
        )
        return fig

    @render_widget
    def chart_muertes_mes():
        """Gráfico de barras: muertes por mes"""
        data = datos_pais_filtrados()
        if len(data) == 0:
            fig = go.Figure()
            fig.update_layout(
                height=500, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
            )
            return fig

        data = data.sort_values("fecha").copy()
        data["mes"] = data["fecha"].dt.to_period("M")
        data_mes = data.groupby("mes").agg({"muertes_dia": "sum"}).reset_index()
        data_mes["mes_str"] = data_mes["mes"].dt.strftime("%b")
        
        # Encontrar el máximo
        idx_max = data_mes["muertes_dia"].idxmax()
        colores = ["#ef4444" if i != idx_max else "#f97316" for i in range(len(data_mes))]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=data_mes["mes_str"],
            y=data_mes["muertes_dia"],
            marker_color=colores,
            marker_line_color="#f87171",
            marker_line_width=1,
            hovertemplate="<b>%{x}</b><br>Muertes: %{y:,.0f}<extra></extra>",
            text=[f"{v/1000:.1f}k" if v >= 1000 else str(int(v)) for v in data_mes["muertes_dia"]],
            textposition="outside",
            textfont=dict(color="rgba(255,255,255,0.95)", size=13, weight="bold"),
        ))

        max_val = data_mes["muertes_dia"].max()
        mes_pico = data_mes.loc[idx_max, "mes_str"]

        fig.update_layout(
            autosize=True,
            height=500,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="rgba(255,255,255,0.9)", size=12),
            xaxis=dict(
                title=dict(text="Mes 2020", font=dict(size=13)),
                gridcolor="rgba(255,255,255,0.05)",
                tickfont=dict(size=13, color="rgba(255,255,255,0.95)"),
            ),
            yaxis=dict(
                title=dict(text="Muertes", font=dict(size=13)),
                gridcolor="rgba(255,255,255,0.1)",
                tickfont=dict(size=11, color="rgba(255,255,255,0.8)"),
            ),
            margin=dict(l=60, r=20, t=40, b=60),
            bargap=0.3,
            annotations=[
                dict(
                    x=mes_pico,
                    y=max_val,
                    text="▲ PICO",
                    showarrow=False,
                    font=dict(color="#f97316", size=12, weight="bold"),
                    yshift=25,
                )
            ]
        )
        return fig

    @output
    @render.ui
    def mensaje_relacion_picos():
        """Mensaje que relaciona los picos de casos y muertes"""
        data = datos_pais_filtrados()
        if len(data) == 0:
            return ui.div()

        data = data.sort_values("fecha").copy()
        data["mes"] = data["fecha"].dt.to_period("M")
        data_mes = data.groupby("mes").agg({
            "confirmados_dia": "sum",
            "muertes_dia": "sum"
        }).reset_index()
        data_mes["mes_str"] = data_mes["mes"].dt.strftime("%b")
        
        idx_max_casos = data_mes["confirmados_dia"].idxmax()
        idx_max_muertes = data_mes["muertes_dia"].idxmax()
        mes_casos = data_mes.loc[idx_max_casos, "mes_str"]
        mes_muertes = data_mes.loc[idx_max_muertes, "mes_str"]
        
        meses_orden = list(data_mes["mes_str"])
        diff = meses_orden.index(mes_muertes) - meses_orden.index(mes_casos)
        
        if diff == 0:
            texto = f"Casos y muertes alcanzaron su pico en el mismo mes: {mes_casos}"
            color = "#22c55e"
        elif diff > 0:
            texto = f"El pico de muertes ({mes_muertes}) ocurrió {diff} mes(es) DESPUÉS del pico de casos ({mes_casos})"
            color = "#f97316"
        else:
            texto = f"El pico de muertes ({mes_muertes}) ocurrió {abs(diff)} mes(es) ANTES del pico de casos ({mes_casos})"
            color = "#3b82f6"
        
        return ui.HTML(f'''
            <div style="
                background: linear-gradient(90deg, rgba(99,102,241,0.2), rgba(168,85,247,0.2));
                border: 1px solid rgba(168,85,247,0.4);
                border-radius: 12px;
                padding: 15px 30px;
                display: inline-block;
                font-size: 15px;
                color: {color};
                font-weight: 500;
            ">
                {texto}
            </div>
        ''')


app = App(app_ui, server)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
