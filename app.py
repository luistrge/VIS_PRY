from shiny import App, ui, render, reactive
from shinywidgets import output_widget, render_widget
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ═══════════════════════════════════════════════════════════════════════════════
# CARGA DE DATOS
# ═══════════════════════════════════════════════════════════════════════════════
df = pd.read_csv("panel_2020_paises_sin_nan_R_clean.csv")
df['fecha'] = pd.to_datetime(df['fecha'])

numeric_cols = ['confirmados', 'muertes', 'IA_100k', 'tasa_mortalidad_por_millon', 
                'letalidad_CFR_pct', 'confirmados_dia', 'muertes_dia', 
                'pib_per_capita_2019', 'gasto_salud_pib', 'poblacion']
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

df_ultimo = df.loc[df.groupby('pais')['fecha'].idxmax()]
paises = sorted(df['pais'].dropna().unique().tolist())
fecha_min = df['fecha'].min()
fecha_max = df['fecha'].max()

# ═══════════════════════════════════════════════════════════════════════════════
# CSS PROFESIONAL CON HERO Y NAVEGACIÓN
# ═══════════════════════════════════════════════════════════════════════════════
css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif; box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body { background: linear-gradient(135deg, #0c0c1e 0%, #1a1a3e 50%, #0d0d2b 100%); min-height: 100vh; background-attachment: fixed; }

/* NAV LATERAL */
.nav-menu { position: fixed; top: 50%; right: 20px; transform: translateY(-50%); z-index: 1000; display: flex; flex-direction: column; gap: 10px; }
.nav-dot { width: 12px; height: 12px; border-radius: 50%; background: rgba(99, 102, 241, 0.3); border: 2px solid rgba(99, 102, 241, 0.5); cursor: pointer; transition: all 0.3s ease; position: relative; }
.nav-dot:hover { background: #6366f1; transform: scale(1.3); box-shadow: 0 0 15px rgba(99, 102, 241, 0.6); }
.nav-dot::before { content: attr(data-tooltip); position: absolute; right: 25px; top: 50%; transform: translateY(-50%); background: rgba(20, 20, 50, 0.95); color: #fff; padding: 6px 12px; border-radius: 6px; font-size: 0.75rem; white-space: nowrap; opacity: 0; pointer-events: none; transition: all 0.3s ease; border: 1px solid rgba(99, 102, 241, 0.3); }
.nav-dot:hover::before { opacity: 1; right: 30px; }
.nav-dot.active { background: linear-gradient(135deg, #6366f1, #a855f7); border-color: #a855f7; box-shadow: 0 0 12px rgba(99, 102, 241, 0.5); }

/* ANIMACIONES */
@keyframes pulse { 0%, 100% { box-shadow: 0 0 20px rgba(99, 102, 241, 0.4); } 50% { box-shadow: 0 0 40px rgba(99, 102, 241, 0.8); } }
@keyframes float { 0%, 100% { transform: translateY(0px); } 50% { transform: translateY(-8px); } }
@keyframes glowPulse { 0%, 100% { box-shadow: 0 0 20px rgba(99, 102, 241, 0.15); } 50% { box-shadow: 0 0 40px rgba(99, 102, 241, 0.3); } }

/* HERO LANDING */
.hero-landing { min-height: 100vh; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 40px; position: relative; }
.hero-section { background: linear-gradient(135deg, rgba(15, 15, 35, 0.95), rgba(25, 25, 55, 0.9)); padding: 60px; border-radius: 30px; border: 1px solid rgba(99, 102, 241, 0.2); backdrop-filter: blur(20px); max-width: 1200px; width: 100%; position: relative; overflow: hidden; }
.hero-section::before { content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: radial-gradient(circle at 20% 80%, rgba(99, 102, 241, 0.15) 0%, transparent 50%), radial-gradient(circle at 80% 20%, rgba(168, 85, 247, 0.15) 0%, transparent 50%); pointer-events: none; }
.hero-content { position: relative; z-index: 2; display: flex; align-items: center; justify-content: space-between; gap: 50px; }
.hero-text { flex: 1; }
.hero-badge { display: inline-flex; align-items: center; gap: 8px; background: rgba(99, 102, 241, 0.15); border: 1px solid rgba(99, 102, 241, 0.3); padding: 6px 14px; border-radius: 50px; margin-bottom: 20px; font-size: 0.75rem; color: rgba(255, 255, 255, 0.8); letter-spacing: 1px; text-transform: uppercase; }
.hero-badge-dot { width: 8px; height: 8px; background: #10b981; border-radius: 50%; animation: pulse 2s infinite; }
.hero-title { font-size: 3rem; font-weight: 700; color: #fff; margin-bottom: 15px; line-height: 1.2; }
.hero-title-accent { background: linear-gradient(135deg, #6366f1, #a855f7, #ec4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.hero-description { font-size: 1.1rem; color: rgba(255, 255, 255, 0.6); line-height: 1.7; margin-bottom: 30px; max-width: 500px; }
.hero-visual { flex: 0 0 280px; }
.hero-globe { width: 250px; height: 250px; }
.hero-globe svg { width: 100%; height: 100%; filter: drop-shadow(0 0 30px rgba(99, 102, 241, 0.4)); }

/* KPIs EN HERO - PEQUEÑOS */
.hero-kpis { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-top: 30px; padding-top: 25px; border-top: 1px solid rgba(255, 255, 255, 0.1); }
.hero-kpi { text-align: center; padding: 15px; background: rgba(20, 20, 50, 0.5); border-radius: 12px; border: 1px solid rgba(99, 102, 241, 0.2); transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1); }
.hero-kpi:hover { transform: scale(1.05); border-color: rgba(99, 102, 241, 0.5); }
.hero-kpi-value { font-size: 1.5rem; font-weight: 700; background: linear-gradient(135deg, #6366f1, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.hero-kpi-label { font-size: 0.7rem; color: rgba(255, 255, 255, 0.5); text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }

/* KPIs DASHBOARD - GRANDES CON ANIMACIÓN */
@keyframes slideInUp { from { opacity: 0; transform: translateY(40px); } to { opacity: 1; transform: translateY(0); } }
@keyframes countUp { from { opacity: 0; transform: scale(0.8); } to { opacity: 1; transform: scale(1); } }
@keyframes borderGlow { 0%, 100% { border-color: rgba(99, 102, 241, 0.3); } 50% { border-color: rgba(168, 85, 247, 0.6); } }

.dashboard-kpis { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px; }
.dashboard-kpi { background: linear-gradient(145deg, rgba(25, 25, 55, 0.9), rgba(35, 35, 70, 0.8)); border-radius: 20px; padding: 25px 20px; border: 1px solid rgba(99, 102, 241, 0.25); position: relative; overflow: hidden; opacity: 0; animation: slideInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1) forwards; }
.dashboard-kpi:nth-child(1) { animation-delay: 0.1s; }
.dashboard-kpi:nth-child(2) { animation-delay: 0.2s; }
.dashboard-kpi:nth-child(3) { animation-delay: 0.3s; }
.dashboard-kpi:nth-child(4) { animation-delay: 0.4s; }
.dashboard-kpi::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, #6366f1, #a855f7, #ec4899); }
.dashboard-kpi:hover { transform: translateY(-5px); border-color: rgba(99, 102, 241, 0.5); box-shadow: 0 10px 40px rgba(99, 102, 241, 0.2); }
.dashboard-kpi-icon { width: 50px; height: 50px; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-bottom: 15px; }
.dashboard-kpi-icon svg { width: 26px; height: 26px; }
.dashboard-kpi-icon.casos { background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(99, 102, 241, 0.1)); color: #818cf8; }
.dashboard-kpi-icon.muertes { background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(239, 68, 68, 0.1)); color: #f87171; }
.dashboard-kpi-icon.paises { background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(16, 185, 129, 0.1)); color: #34d399; }
.dashboard-kpi-icon.letalidad { background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(245, 158, 11, 0.1)); color: #fbbf24; }
.dashboard-kpi-value { font-size: 2.2rem; font-weight: 700; margin-bottom: 5px; animation: countUp 0.8s ease-out forwards; }
.dashboard-kpi-value.casos { color: #818cf8; }
.dashboard-kpi-value.muertes { color: #f87171; }
.dashboard-kpi-value.paises { color: #34d399; }
.dashboard-kpi-value.letalidad { color: #fbbf24; }
.dashboard-kpi-label { font-size: 0.85rem; color: rgba(255, 255, 255, 0.6); text-transform: uppercase; letter-spacing: 1.5px; }
.dashboard-kpi-change { display: flex; align-items: center; gap: 5px; margin-top: 10px; font-size: 0.75rem; color: rgba(255, 255, 255, 0.5); }

@media (max-width: 992px) { .dashboard-kpis { grid-template-columns: repeat(2, 1fr); } }

/* SCROLL INDICATOR */
.scroll-indicator { position: absolute; bottom: 30px; left: 50%; transform: translateX(-50%); animation: float 2s ease-in-out infinite; cursor: pointer; }
.scroll-arrow { width: 24px; height: 24px; border-right: 2px solid rgba(255, 255, 255, 0.4); border-bottom: 2px solid rgba(255, 255, 255, 0.4); transform: rotate(45deg); transition: all 0.3s ease; }
.scroll-arrow:hover { border-color: #a855f7; }

/* DASHBOARD SECTION */
.dashboard-section { padding: 40px 0; scroll-margin-top: 20px; }

/* FILTROS STICKY */
.filter-panel { background: linear-gradient(145deg, rgba(35, 35, 70, 0.95), rgba(25, 25, 55, 0.98)); border-radius: 16px; padding: 20px 25px; margin-bottom: 25px; border: 1px solid rgba(99, 102, 241, 0.3); position: sticky; top: 10px; z-index: 100; backdrop-filter: blur(20px); }
.filter-header { display: flex; align-items: center; gap: 10px; margin-bottom: 15px; padding-bottom: 12px; border-bottom: 1px solid rgba(99, 102, 241, 0.2); }
.filter-title { font-size: 1rem; font-weight: 600; color: #fff; margin: 0; }

/* CHART SECTIONS */
.chart-section { background: linear-gradient(145deg, rgba(25, 25, 55, 0.7), rgba(15, 15, 45, 0.8)); border-radius: 20px; padding: 25px 15px; margin-bottom: 25px; border: 1px solid rgba(255, 255, 255, 0.08); backdrop-filter: blur(10px); animation: glowPulse 4s ease-in-out infinite; scroll-margin-top: 80px; }
.chart-section:hover { border-color: rgba(99, 102, 241, 0.3); }
.chart-section .js-plotly-plot { width: 100% !important; }
.section-header { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid rgba(99, 102, 241, 0.2); padding-left: 10px; }
.section-number { font-size: 2.5rem; font-weight: 800; background: linear-gradient(135deg, rgba(99, 102, 241, 0.3), rgba(168, 85, 247, 0.3)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-right: 10px; line-height: 1; }
.section-title { font-size: 1.4rem; font-weight: 600; color: #fff; margin: 0; }
.section-subtitle { font-size: 0.85rem; color: rgba(255, 255, 255, 0.5); margin-top: 3px; }

/* CHART CON DETALLE LATERAL */
.chart-with-detail { display: grid; grid-template-columns: 1fr 280px; gap: 20px; }
.chart-main { min-width: 0; }
.chart-detail { background: linear-gradient(145deg, rgba(30, 30, 60, 0.9), rgba(20, 20, 50, 0.95)); border-radius: 16px; padding: 20px; border: 1px solid rgba(99, 102, 241, 0.25); height: fit-content; position: sticky; top: 100px; }
.detail-title { font-size: 0.9rem; font-weight: 600; color: #a5b4fc; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 1px; border-bottom: 1px solid rgba(99, 102, 241, 0.2); padding-bottom: 10px; }
.detail-item { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.05); }
.detail-label { color: rgba(255, 255, 255, 0.6); font-size: 0.8rem; }
.detail-value { color: #fff; font-weight: 600; font-size: 0.9rem; }
.detail-empty { text-align: center; color: rgba(255, 255, 255, 0.4); font-size: 0.85rem; padding: 30px 10px; }
@media (max-width: 1200px) { .chart-with-detail { grid-template-columns: 1fr; } .chart-detail { display: none; } }

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
.js-plotly-plot { border-radius: 12px; overflow: hidden; }

@media (max-width: 992px) {
    .hero-content { flex-direction: column; text-align: center; }
    .hero-text { text-align: center; }
    .hero-description { margin: 0 auto 30px; }
    .hero-kpis { grid-template-columns: repeat(2, 1fr); }
    .hero-visual { display: none; }
    .dashboard-kpis { grid-template-columns: repeat(2, 1fr); }
}
</style>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const sectionId = entry.target.id;
                if (sectionId) {
                    document.querySelectorAll('.nav-dot').forEach(dot => {
                        dot.classList.remove('active');
                        if (dot.getAttribute('data-section') === sectionId) {
                            dot.classList.add('active');
                        }
                    });
                }
            }
        });
    }, { threshold: 0.3 });
    
    setTimeout(() => {
        document.querySelectorAll('[id]').forEach(el => observer.observe(el));
    }, 100);
    
    document.querySelectorAll('.nav-dot').forEach(dot => {
        dot.addEventListener('click', function() {
            const targetId = this.getAttribute('data-section');
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
});
</script>
"""

# ═══════════════════════════════════════════════════════════════════════════════
# UI
# ═══════════════════════════════════════════════════════════════════════════════
app_ui = ui.page_fluid(
    ui.HTML(css),
    
    # NAV LATERAL
    ui.HTML("""
    <div class="nav-menu">
        <div class="nav-dot active" data-section="hero" data-tooltip="Inicio"></div>
        <div class="nav-dot" data-section="dashboard" data-tooltip="Dashboard"></div>
        <div class="nav-dot" data-section="temporal" data-tooltip="Temporal"></div>
        <div class="nav-dot" data-section="mapa" data-tooltip="Mapa"></div>
        <div class="nav-dot" data-section="salud" data-tooltip="Salud"></div>
        <div class="nav-dot" data-section="ranking" data-tooltip="Ranking"></div>
        <div class="nav-dot" data-section="pib" data-tooltip="PIB"></div>
        <div class="nav-dot" data-section="diarios" data-tooltip="Diarios"></div>
    </div>
    """),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # HERO LANDING PAGE
    # ═══════════════════════════════════════════════════════════════════════════
    ui.div(
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
                        <span class="hero-title-accent">Panel de Análisis 2025</span>
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
                                <linearGradient id="globeGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                                    <stop offset="0%" style="stop-color:#6366f1;stop-opacity:0.8" />
                                    <stop offset="50%" style="stop-color:#a855f7;stop-opacity:0.6" />
                                    <stop offset="100%" style="stop-color:#ec4899;stop-opacity:0.4" />
                                </linearGradient>
                            </defs>
                            <circle cx="100" cy="100" r="80" fill="none" stroke="url(#globeGrad)" stroke-width="2"/>
                            <ellipse cx="100" cy="100" rx="80" ry="30" fill="none" stroke="rgba(99,102,241,0.3)" stroke-width="1"/>
                            <ellipse cx="100" cy="100" rx="30" ry="80" fill="none" stroke="rgba(99,102,241,0.3)" stroke-width="1"/>
                            <ellipse cx="100" cy="100" rx="55" ry="80" fill="none" stroke="rgba(99,102,241,0.2)" stroke-width="1"/>
                            <circle cx="60" cy="70" r="4" fill="#6366f1"><animate attributeName="opacity" values="1;0.3;1" dur="2s" repeatCount="indefinite"/></circle>
                            <circle cx="130" cy="85" r="5" fill="#a855f7"><animate attributeName="opacity" values="0.3;1;0.3" dur="2.5s" repeatCount="indefinite"/></circle>
                            <circle cx="85" cy="120" r="3" fill="#ec4899"><animate attributeName="opacity" values="1;0.5;1" dur="1.8s" repeatCount="indefinite"/></circle>
                            <circle cx="145" cy="110" r="4" fill="#06b6d4"><animate attributeName="opacity" values="0.5;1;0.5" dur="2.2s" repeatCount="indefinite"/></circle>
                        </svg>
                    </div>
                </div>
            </div>
            """),
            # KPIs pequeños en el hero
            ui.output_ui("hero_kpis"),
            class_="hero-section"
        ),
        ui.HTML('<div class="scroll-indicator" onclick="document.getElementById(\'dashboard\').scrollIntoView({behavior: \'smooth\'})"><div class="scroll-arrow"></div></div>'),
        class_="hero-landing",
        id="hero"
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # DASHBOARD SECTION
    # ═══════════════════════════════════════════════════════════════════════════
    ui.div(
        # Filtros
        ui.div(
            ui.div(
                ui.HTML('<div class="filter-title"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:18px;height:18px;vertical-align:middle;margin-right:8px"><path d="M22 3H2l8 9.46V19l4 2v-8.54L22 3z"/></svg>Filtros de Visualización</div>'),
                class_="filter-header"
            ),
            ui.row(
                ui.column(4, ui.input_selectize("pais", "País:", choices=["Todos"] + paises, selected="Todos")),
                ui.column(4, ui.input_date("fecha_inicio", "Fecha inicio:", value=fecha_min, min=fecha_min, max=fecha_max)),
                ui.column(4, ui.input_date("fecha_fin", "Fecha fin:", value=fecha_max, min=fecha_min, max=fecha_max))
            ),
            class_="filter-panel"
        ),
        
        # KPIs Dashboard (grandes, con animación)
        ui.output_ui("dashboard_kpis"),
        
        # Gráfico 1: Temporal
        ui.div(
            ui.div(
                ui.span("01", class_="section-number"),
                ui.div(
                    ui.div("Evolución Temporal", class_="section-title"),
                    ui.div("Evolución de casos confirmados a lo largo del tiempo", class_="section-subtitle"),
                ),
                class_="section-header"
            ),
            output_widget("chart_temporal"),
            class_="chart-section",
            id="temporal"
        ),
        
        # Gráfico 2: Mapa
        ui.div(
            ui.div(
                ui.span("02", class_="section-number"),
                ui.div(
                    ui.div("Mapa Global de Incidencia", class_="section-title"),
                    ui.div("Distribución geográfica de casos por 100.000 habitantes", class_="section-subtitle"),
                ),
                class_="section-header"
            ),
            output_widget("chart_mapa"),
            class_="chart-section",
            id="mapa"
        ),
        
        # Gráfico 3: Salud
        ui.div(
            ui.div(
                ui.span("03", class_="section-number"),
                ui.div(
                    ui.div("Gasto en Salud vs Letalidad", class_="section-title"),
                    ui.div("Relación entre inversión sanitaria y tasa de letalidad", class_="section-subtitle"),
                ),
                class_="section-header"
            ),
            output_widget("chart_salud"),
            class_="chart-section",
            id="salud"
        ),
        
        # Gráfico 4: Top países
        ui.div(
            ui.div(
                ui.span("04", class_="section-number"),
                ui.div(
                    ui.div("Top 15 Países más Afectados", class_="section-title"),
                    ui.div("Ranking por número total de casos confirmados", class_="section-subtitle"),
                ),
                class_="section-header"
            ),
            output_widget("chart_top"),
            class_="chart-section",
            id="ranking"
        ),
        
        # Gráfico 5: PIB
        ui.div(
            ui.div(
                ui.span("05", class_="section-number"),
                ui.div(
                    ui.div("PIB per Cápita vs Incidencia", class_="section-title"),
                    ui.div("Correlación entre desarrollo económico e impacto del COVID-19", class_="section-subtitle"),
                ),
                class_="section-header"
            ),
            output_widget("chart_pib"),
            class_="chart-section",
            id="pib"
        ),
        
        # Gráfico 6: Casos diarios
        ui.div(
            ui.div(
                ui.span("06", class_="section-number"),
                ui.div(
                    ui.div("Casos Diarios", class_="section-title"),
                    ui.div("Evolución de nuevos casos por día", class_="section-subtitle"),
                ),
                class_="section-header"
            ),
            output_widget("chart_diarios"),
            class_="chart-section",
            id="diarios"
        ),
        
        # Footer
        ui.HTML('<div class="footer">Dashboard COVID-19 2025 | Datos: WHO & World Bank | Shiny for Python + Plotly</div>'),
        
        class_="container-fluid px-4 dashboard-section",
        id="dashboard"
    )
)

# ═══════════════════════════════════════════════════════════════════════════════
# SERVER
# ═══════════════════════════════════════════════════════════════════════════════
def server(input, output, session):
    
    def fmt(n):
        if n >= 1e9: return f"{n/1e9:.2f}B"
        if n >= 1e6: return f"{n/1e6:.2f}M"
        if n >= 1e3: return f"{n/1e3:.1f}K"
        return f"{n:,.0f}"
    
    @reactive.calc
    def datos_filtrados():
        data = df.copy()
        if input.pais() and input.pais() != "Todos":
            data = data[data['pais'] == input.pais()]
        if input.fecha_inicio() and input.fecha_fin():
            data = data[(data['fecha'] >= pd.to_datetime(input.fecha_inicio())) & 
                       (data['fecha'] <= pd.to_datetime(input.fecha_fin()))]
        return data
    
    @reactive.calc
    def datos_ultimo():
        data = datos_filtrados()
        if len(data) == 0:
            return df_ultimo
        return data.loc[data.groupby('pais')['fecha'].idxmax()]
    
    # KPIs en el Hero (pequeños)
    @output
    @render.ui
    def hero_kpis():
        data = datos_ultimo()
        total_casos = int(data['confirmados'].sum())
        total_muertes = int(data['muertes'].sum())
        n_paises = data['pais'].nunique()
        avg_letalidad = data['letalidad_CFR_pct'].mean()
        
        return ui.HTML(f'''
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
        ''')
    
    # KPIs grandes en el Dashboard con animación
    @output
    @render.ui
    def dashboard_kpis():
        data = datos_ultimo()
        total_casos = int(data['confirmados'].sum())
        total_muertes = int(data['muertes'].sum())
        n_paises = data['pais'].nunique()
        avg_letalidad = data['letalidad_CFR_pct'].mean()
        
        return ui.HTML(f'''
        <div class="dashboard-kpis">
            <div class="dashboard-kpi">
                <div class="dashboard-kpi-icon casos"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 2v4m0 12v4M2 12h4m12 0h4"/><path d="m4.93 4.93 2.83 2.83m8.48 8.48 2.83 2.83m0-14.14-2.83 2.83m-8.48 8.48-2.83 2.83"/></svg></div>
                <div class="dashboard-kpi-value casos">{fmt(total_casos)}</div>
                <div class="dashboard-kpi-label">Casos Confirmados</div>
                <div class="dashboard-kpi-change"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;vertical-align:middle;margin-right:4px"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>Total acumulado global</div>
            </div>
            <div class="dashboard-kpi">
                <div class="dashboard-kpi-icon muertes"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg></div>
                <div class="dashboard-kpi-value muertes">{fmt(total_muertes)}</div>
                <div class="dashboard-kpi-label">Muertes Totales</div>
                <div class="dashboard-kpi-change"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;vertical-align:middle;margin-right:4px"><path d="M3 3v18h18"/><path d="m19 15-5-5-4 4-3-3"/></svg>Impacto global</div>
            </div>
            <div class="dashboard-kpi">
                <div class="dashboard-kpi-icon paises"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg></div>
                <div class="dashboard-kpi-value paises">{n_paises}</div>
                <div class="dashboard-kpi-label">Países Analizados</div>
                <div class="dashboard-kpi-change"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;vertical-align:middle;margin-right:4px"><polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"/><line x1="8" y1="2" x2="8" y2="18"/><line x1="16" y1="6" x2="16" y2="22"/></svg>Cobertura mundial</div>
            </div>
            <div class="dashboard-kpi">
                <div class="dashboard-kpi-icon letalidad"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg></div>
                <div class="dashboard-kpi-value letalidad">{avg_letalidad:.2f}%</div>
                <div class="dashboard-kpi-label">Tasa de Letalidad</div>
                <div class="dashboard-kpi-change"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;vertical-align:middle;margin-right:4px"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>Promedio CFR</div>
            </div>
        </div>
        ''')
    
    @render_widget
    def chart_temporal():
        data = datos_filtrados()
        
        if input.pais() and input.pais() != "Todos":
            # País específico - agrupar por mes
            data = data.copy()
            data['mes'] = data['fecha'].dt.to_period('M').astype(str)
            data_mes = data.groupby('mes').agg({'confirmados': 'max', 'muertes': 'max'}).reset_index()
            fig = px.bar(data_mes, x='mes', y='confirmados',
                        labels={'mes': 'Mes', 'confirmados': 'Casos Confirmados'},
                        color_discrete_sequence=['#6366f1'])
            fig.update_traces(hovertemplate='<b>%{x}</b><br>Casos: %{y:,.0f}<extra></extra>')
        else:
            # Vista global - agrupar por mes todos los países top
            data = data.copy()
            data['mes'] = data['fecha'].dt.to_period('M').astype(str)
            data_mes = data.groupby('mes').agg({'confirmados': 'sum', 'muertes': 'sum'}).reset_index()
            fig = px.area(data_mes, x='mes', y='confirmados',
                         labels={'mes': 'Mes', 'confirmados': 'Casos Acumulados'},
                         color_discrete_sequence=['#6366f1'])
            fig.update_traces(fill='tozeroy', hovertemplate='<b>%{x}</b><br>Casos: %{y:,.0f}<extra></extra>')
        
        fig.update_layout(
            height=420, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='rgba(255,255,255,0.8)'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)', tickangle=-45),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            legend=dict(orientation="h", y=1.02, bgcolor='rgba(0,0,0,0)'),
            margin=dict(l=50, r=20, t=30, b=80)
        )
        return fig
    
    @render_widget
    def chart_mapa():
        data = datos_ultimo().copy()
        
        fig = px.choropleth(
            data, locations='iso3c', color='IA_100k', hover_name='pais',
            color_continuous_scale=['#1e1b4b', '#3730a3', '#6366f1', '#818cf8', '#a5b4fc', '#c7d2fe'],
            labels={'IA_100k': 'Incidencia/100k'}
        )
        fig.update_geos(
            showframe=False, showcoastlines=True, coastlinecolor='rgba(99,102,241,0.4)',
            projection_type='natural earth', bgcolor='rgba(0,0,0,0)',
            landcolor='rgba(25,25,50,0.9)', oceancolor='rgba(8,8,20,1)',
            showland=True, showcountries=True, countrycolor='rgba(99,102,241,0.2)',
            lataxis_range=[-60, 90]
        )
        fig.update_layout(
            height=600, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='rgba(255,255,255,0.8)'), margin=dict(l=0, r=0, t=10, b=0),
            coloraxis_colorbar=dict(
                title='Incidencia/100k',
                thickness=15,
                len=0.6,
                bgcolor='rgba(20,20,50,0.8)',
                bordercolor='rgba(99,102,241,0.3)',
                tickfont=dict(color='rgba(255,255,255,0.7)')
            )
        )
        return fig
    
    @render_widget
    def chart_salud():
        data = datos_ultimo()
        data = data[data['gasto_salud_pib'] > 0].copy()
        
        fig = px.scatter(
            data, x='gasto_salud_pib', y='letalidad_CFR_pct', size='poblacion',
            color='pib_per_capita_2019', hover_name='pais',
            color_continuous_scale=['#10b981', '#fbbf24', '#ef4444'],
            labels={'gasto_salud_pib': 'Gasto en Salud (% PIB)', 'letalidad_CFR_pct': 'Letalidad (%)', 'pib_per_capita_2019': 'PIB/cápita'},
            custom_data=['confirmados', 'muertes', 'poblacion']
        )
        fig.update_traces(
            hovertemplate='<b>%{hovertext}</b><br><br>Gasto Salud: %{x:.1f}% PIB<br>Letalidad: %{y:.2f}%<br>PIB/cápita: $%{marker.color:,.0f}<br>Casos: %{customdata[0]:,.0f}<br>Muertes: %{customdata[1]:,.0f}<extra></extra>'
        )
        fig.update_layout(
            height=450, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='rgba(255,255,255,0.8)'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            margin=dict(l=60, r=20, t=30, b=50)
        )
        return fig
    
    @render_widget
    def chart_top():
        data = datos_ultimo().nlargest(15, 'confirmados').copy()
        data = data.sort_values('confirmados', ascending=True)
        
        # Crear textos personalizados para el hover
        hover_texts = []
        for _, row in data.iterrows():
            hover_texts.append(
                f"<b>{row['pais']}</b><br><br>"
                f"● Casos: {row['confirmados']:,.0f}<br>"
                f"● Muertes: {row['muertes']:,.0f}<br>"
                f"● Incidencia: {row['IA_100k']:,.1f}/100k<br>"
                f"● Letalidad: {row['letalidad_CFR_pct']:.2f}%<br>"
                f"● Población: {row['poblacion']:,.0f}"
            )
        
        fig = go.Figure(go.Bar(
            y=data['pais'], x=data['confirmados'], orientation='h',
            marker=dict(
                color=data['confirmados'], 
                colorscale=[[0, '#4f46e5'], [0.3, '#7c3aed'], [0.6, '#a855f7'], [1, '#ec4899']],
                line=dict(width=1, color='rgba(255,255,255,0.2)')
            ),
            hovertext=hover_texts,
            hoverinfo='text',
            hoverlabel=dict(
                bgcolor='rgba(20,20,50,0.95)',
                bordercolor='rgba(99,102,241,0.5)',
                font=dict(size=12, color='white')
            )
        ))
        fig.update_layout(
            height=550, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='rgba(255,255,255,0.8)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.05)', tickfont=dict(size=11)),
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)', title='Casos Confirmados'),
            margin=dict(l=120, r=20, t=20, b=50),
            bargap=0.15
        )
        return fig
    
    @render_widget
    def chart_pib():
        data = datos_ultimo()
        data = data[data['pib_per_capita_2019'] > 0].copy()
        
        fig = px.scatter(
            data, x='pib_per_capita_2019', y='IA_100k', size='poblacion',
            color='letalidad_CFR_pct', hover_name='pais',
            color_continuous_scale=['#10b981', '#fbbf24', '#ef4444'],
            labels={'pib_per_capita_2019': 'PIB per Cápita ($)', 'IA_100k': 'Incidencia/100k', 'letalidad_CFR_pct': 'Letalidad %'},
            custom_data=['confirmados', 'muertes', 'gasto_salud_pib']
        )
        fig.update_traces(
            hovertemplate='<b>%{hovertext}</b><br><br>PIB/cápita: $%{x:,.0f}<br>Incidencia: %{y:,.1f}/100k<br>Letalidad: %{marker.color:.2f}%<br>Casos: %{customdata[0]:,.0f}<br>Muertes: %{customdata[1]:,.0f}<br>Gasto Salud: %{customdata[2]:.1f}% PIB<extra></extra>'
        )
        fig.update_layout(
            height=450, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='rgba(255,255,255,0.8)'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)', type='log', title='PIB per Cápita ($) - Escala Log'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            margin=dict(l=60, r=20, t=30, b=50)
        )
        return fig
    
    @render_widget
    def chart_diarios():
        data = datos_filtrados().copy()
        
        if input.pais() and input.pais() != "Todos":
            # País específico - por mes
            data['mes'] = data['fecha'].dt.to_period('M').astype(str)
            data_mes = data.groupby('mes').agg({'confirmados_dia': 'sum', 'muertes_dia': 'sum'}).reset_index()
            fig = px.bar(data_mes, x='mes', y='confirmados_dia',
                        labels={'mes': 'Mes', 'confirmados_dia': 'Casos Diarios'},
                        color_discrete_sequence=['#a855f7'])
            fig.update_traces(hovertemplate='<b>%{x}</b><br>Nuevos casos: %{y:,.0f}<extra></extra>')
        else:
            # Global por mes
            data['mes'] = data['fecha'].dt.to_period('M').astype(str)
            data_mes = data.groupby('mes').agg({'confirmados_dia': 'sum'}).reset_index()
            fig = px.area(data_mes, x='mes', y='confirmados_dia',
                         labels={'mes': 'Mes', 'confirmados_dia': 'Casos Diarios'},
                         color_discrete_sequence=['#a855f7'])
            fig.update_traces(fill='tozeroy', hovertemplate='<b>%{x}</b><br>Nuevos casos: %{y:,.0f}<extra></extra>')
        
        fig.update_layout(
            height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='rgba(255,255,255,0.8)'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)', tickangle=-45),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            margin=dict(l=60, r=20, t=30, b=80)
        )
        return fig

app = App(app_ui, server)
