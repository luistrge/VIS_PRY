from shiny import App, ui, render, reactive
from shinywidgets import output_widget, render_widget
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ═══════════════════════════════════════════════════════════════════════════════
# CARGA DE DATOS
# ═══════════════════════════════════════════════════════════════════════════════
df = pd.read_csv("panel_2025_paises_sin_nan_R_clean.csv")
df['fecha'] = pd.to_datetime(df['fecha'])

# Columnas numéricas
numeric_cols = ['confirmados', 'muertes', 'IA_100k', 'tasa_mortalidad_por_millon', 
                'letalidad_CFR_pct', 'confirmados_dia', 'muertes_dia', 
                'pib_per_capita_2019', 'gasto_salud_pib', 'poblacion']
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# Datos agregados
df_ultimo = df.loc[df.groupby('pais')['fecha'].idxmax()]
paises = sorted(df['pais'].dropna().unique().tolist())
fecha_min = df['fecha'].min()
fecha_max = df['fecha'].max()

# ═══════════════════════════════════════════════════════════════════════════════
# ESTILOS CSS CON TRANSICIONES DE KPIs
# ═══════════════════════════════════════════════════════════════════════════════
css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
    --primary: #6366f1;
    --secondary: #8b5cf6;
    --accent: #a855f7;
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
    --cyan: #06b6d4;
    --bg-dark: #0f0f1a;
    --bg-card: rgba(20, 20, 40, 0.9);
    --text: #ffffff;
    --text-muted: rgba(255,255,255,0.6);
}

* { font-family: 'Inter', sans-serif; box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
    background: linear-gradient(135deg, #0a0a15 0%, #12122a 50%, #0a0a18 100%);
    background-attachment: fixed;
    min-height: 100vh;
    margin: 0;
    color: var(--text);
}

/* ═══════════════════════════════════════════════════════════════════════════════
   PANTALLA DE INICIO
   ═══════════════════════════════════════════════════════════════════════════════ */
.intro-screen {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px;
    animation: fadeIn 0.8s ease;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(30px); }
    to { opacity: 1; transform: translateY(0); }
}

.intro-content {
    text-align: center;
    max-width: 900px;
}

.intro-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(99, 102, 241, 0.15);
    border: 1px solid rgba(99, 102, 241, 0.3);
    padding: 8px 20px;
    border-radius: 50px;
    margin-bottom: 30px;
    font-size: 0.85rem;
    color: var(--text-muted);
}

.intro-badge-dot {
    width: 8px;
    height: 8px;
    background: var(--success);
    border-radius: 50%;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
    50% { box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
}

.intro-title {
    font-size: 4rem;
    font-weight: 800;
    margin: 0 0 20px 0;
    line-height: 1.1;
}

.intro-title span {
    background: linear-gradient(135deg, var(--primary), var(--accent), #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.intro-description {
    font-size: 1.2rem;
    color: var(--text-muted);
    line-height: 1.7;
    margin-bottom: 40px;
    max-width: 700px;
    margin-left: auto;
    margin-right: auto;
}

/* ═══════════════════════════════════════════════════════════════════════════════
   KPIs EN PANTALLA DE INICIO (GRANDES)
   ═══════════════════════════════════════════════════════════════════════════════ */
.intro-kpis {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 25px;
    margin-bottom: 50px;
    width: 100%;
    max-width: 1000px;
}

.intro-kpi {
    background: linear-gradient(145deg, rgba(30, 30, 60, 0.8), rgba(20, 20, 45, 0.9));
    border-radius: 20px;
    padding: 30px 20px;
    text-align: center;
    border: 1px solid rgba(255, 255, 255, 0.1);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    position: relative;
    overflow: hidden;
}

.intro-kpi::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    border-radius: 20px 20px 0 0;
}

.intro-kpi.casos::before { background: linear-gradient(90deg, var(--primary), var(--secondary)); }
.intro-kpi.muertes::before { background: linear-gradient(90deg, var(--danger), #f97316); }
.intro-kpi.paises::before { background: linear-gradient(90deg, var(--cyan), var(--success)); }
.intro-kpi.letalidad::before { background: linear-gradient(90deg, var(--warning), var(--danger)); }

.intro-kpi:hover {
    transform: translateY(-10px);
    box-shadow: 0 25px 50px rgba(99, 102, 241, 0.25);
    border-color: rgba(99, 102, 241, 0.4);
}

.intro-kpi-icon {
    width: 50px;
    height: 50px;
    margin: 0 auto 15px;
    padding: 12px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.intro-kpi.casos .intro-kpi-icon { background: rgba(99, 102, 241, 0.2); color: var(--primary); }
.intro-kpi.muertes .intro-kpi-icon { background: rgba(239, 68, 68, 0.2); color: var(--danger); }
.intro-kpi.paises .intro-kpi-icon { background: rgba(6, 182, 212, 0.2); color: var(--cyan); }
.intro-kpi.letalidad .intro-kpi-icon { background: rgba(245, 158, 11, 0.2); color: var(--warning); }

.intro-kpi-icon svg {
    width: 26px;
    height: 26px;
}

.intro-kpi-value {
    font-size: 2.5rem;
    font-weight: 800;
    margin-bottom: 8px;
    line-height: 1;
}

.intro-kpi.casos .intro-kpi-value { color: var(--primary); }
.intro-kpi.muertes .intro-kpi-value { color: var(--danger); }
.intro-kpi.paises .intro-kpi-value { color: var(--cyan); }
.intro-kpi.letalidad .intro-kpi-value { color: var(--warning); }

.intro-kpi-label {
    font-size: 0.85rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 1px;
}

.intro-kpi-detail {
    font-size: 0.75rem;
    color: rgba(255,255,255,0.4);
    margin-top: 8px;
}

/* Botón de Inicio */
.btn-start {
    display: inline-flex;
    align-items: center;
    gap: 12px;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    color: white;
    border: none;
    padding: 18px 45px;
    border-radius: 50px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 10px 30px rgba(99, 102, 241, 0.4);
}

.btn-start:hover {
    transform: translateY(-3px);
    box-shadow: 0 15px 40px rgba(99, 102, 241, 0.5);
}

.btn-start svg {
    width: 20px;
    height: 20px;
}

/* ═══════════════════════════════════════════════════════════════════════════════
   DASHBOARD
   ═══════════════════════════════════════════════════════════════════════════════ */
.dashboard-screen {
    display: none;
    animation: slideIn 0.6s ease;
}

.dashboard-screen.active {
    display: block;
}

@keyframes slideIn {
    from { opacity: 0; transform: translateX(30px); }
    to { opacity: 1; transform: translateX(0); }
}

/* KPIs STICKY (pequeños, fijos arriba) */
.sticky-kpis {
    position: sticky;
    top: 0;
    z-index: 100;
    background: linear-gradient(180deg, rgba(10, 10, 20, 0.98) 0%, rgba(10, 10, 20, 0.9) 100%);
    backdrop-filter: blur(20px);
    padding: 15px 20px;
    border-bottom: 1px solid rgba(99, 102, 241, 0.2);
    margin-bottom: 25px;
}

.sticky-kpis-inner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    max-width: 1400px;
    margin: 0 auto;
    gap: 15px;
}

.sticky-kpi {
    display: flex;
    align-items: center;
    gap: 12px;
    background: rgba(30, 30, 60, 0.6);
    padding: 10px 18px;
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    transition: all 0.3s ease;
    flex: 1;
    max-width: 280px;
}

.sticky-kpi:hover {
    border-color: rgba(99, 102, 241, 0.3);
    transform: translateY(-2px);
}

.sticky-kpi-icon {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.sticky-kpi.casos .sticky-kpi-icon { background: rgba(99, 102, 241, 0.2); color: var(--primary); }
.sticky-kpi.muertes .sticky-kpi-icon { background: rgba(239, 68, 68, 0.2); color: var(--danger); }
.sticky-kpi.paises .sticky-kpi-icon { background: rgba(6, 182, 212, 0.2); color: var(--cyan); }
.sticky-kpi.letalidad .sticky-kpi-icon { background: rgba(245, 158, 11, 0.2); color: var(--warning); }

.sticky-kpi-icon svg {
    width: 18px;
    height: 18px;
}

.sticky-kpi-info {
    display: flex;
    flex-direction: column;
}

.sticky-kpi-value {
    font-size: 1.3rem;
    font-weight: 700;
    line-height: 1.2;
}

.sticky-kpi.casos .sticky-kpi-value { color: var(--primary); }
.sticky-kpi.muertes .sticky-kpi-value { color: var(--danger); }
.sticky-kpi.paises .sticky-kpi-value { color: var(--cyan); }
.sticky-kpi.letalidad .sticky-kpi-value { color: var(--warning); }

.sticky-kpi-label {
    font-size: 0.7rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.btn-back {
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(99, 102, 241, 0.15);
    border: 1px solid rgba(99, 102, 241, 0.3);
    color: var(--text);
    padding: 10px 20px;
    border-radius: 10px;
    font-size: 0.9rem;
    cursor: pointer;
    transition: all 0.3s ease;
}

.btn-back:hover {
    background: rgba(99, 102, 241, 0.25);
}

.btn-back svg {
    width: 16px;
    height: 16px;
}

/* ═══════════════════════════════════════════════════════════════════════════════
   FILTROS
   ═══════════════════════════════════════════════════════════════════════════════ */
.filter-bar {
    background: linear-gradient(145deg, rgba(25, 25, 55, 0.9), rgba(20, 20, 45, 0.95));
    border-radius: 16px;
    padding: 20px 25px;
    margin: 0 20px 25px;
    border: 1px solid rgba(99, 102, 241, 0.2);
}

.filter-bar-title {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 15px;
    color: var(--text);
}

.filter-bar-title svg {
    width: 18px;
    height: 18px;
    color: var(--primary);
}

/* Inputs */
.form-select, .form-control, .selectize-input {
    background: rgba(25, 25, 50, 0.9) !important;
    border: 1px solid rgba(99, 102, 241, 0.25) !important;
    color: white !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
}

.form-select:focus, .form-control:focus, .selectize-input.focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15) !important;
}

.form-label, .control-label, label {
    color: white !important;
    font-weight: 500 !important;
    margin-bottom: 8px !important;
    font-size: 0.9rem !important;
}

.selectize-input, .selectize-input input, .selectize-input .item { color: white !important; }
.selectize-dropdown {
    background: rgba(25, 25, 50, 0.98) !important;
    border: 1px solid rgba(99, 102, 241, 0.3) !important;
    border-radius: 10px !important;
}
.selectize-dropdown-content .option { color: white !important; padding: 10px 14px !important; }
.selectize-dropdown-content .option:hover { background: rgba(99, 102, 241, 0.25) !important; }

input[type="date"] {
    background: rgba(25, 25, 50, 0.9) !important;
    border: 1px solid rgba(99, 102, 241, 0.25) !important;
    color: white !important;
    border-radius: 10px !important;
    padding: 8px 12px !important;
}

input[type="date"]::-webkit-calendar-picker-indicator { filter: invert(1); }

/* ═══════════════════════════════════════════════════════════════════════════════
   SECCIONES DE GRÁFICOS
   ═══════════════════════════════════════════════════════════════════════════════ */
.chart-section {
    background: linear-gradient(145deg, rgba(20, 20, 45, 0.8), rgba(15, 15, 35, 0.9));
    border-radius: 20px;
    padding: 25px;
    margin: 0 20px 25px;
    border: 1px solid rgba(255, 255, 255, 0.06);
}

.chart-section:hover {
    border-color: rgba(99, 102, 241, 0.2);
}

.section-header {
    display: flex;
    align-items: center;
    gap: 15px;
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 1px solid rgba(99, 102, 241, 0.15);
}

.section-number {
    font-size: 2.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.3), rgba(168, 85, 247, 0.3));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
}

.section-icon {
    width: 40px;
    height: 40px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(99, 102, 241, 0.15);
    color: var(--primary);
}

.section-icon svg {
    width: 22px;
    height: 22px;
}

.section-title {
    font-size: 1.4rem;
    font-weight: 600;
    color: white;
    margin: 0;
}

.section-subtitle {
    font-size: 0.85rem;
    color: var(--text-muted);
    margin-top: 4px;
}

/* Plotly */
.js-plotly-plot {
    border-radius: 12px;
    overflow: hidden;
}

/* Footer */
.footer {
    text-align: center;
    padding: 30px;
    color: var(--text-muted);
    font-size: 0.85rem;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
    margin-top: 30px;
}

/* Responsive */
@media (max-width: 1024px) {
    .intro-kpis { grid-template-columns: repeat(2, 1fr); }
    .intro-title { font-size: 2.8rem; }
    .sticky-kpis-inner { flex-wrap: wrap; }
    .sticky-kpi { max-width: none; }
}

@media (max-width: 768px) {
    .intro-kpis { grid-template-columns: 1fr; }
    .intro-title { font-size: 2.2rem; }
    .sticky-kpi { flex: 1 1 45%; }
}
</style>

<script>
function showDashboard() {
    document.querySelector('.intro-screen').style.display = 'none';
    document.querySelector('.dashboard-screen').classList.add('active');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showIntro() {
    document.querySelector('.intro-screen').style.display = 'flex';
    document.querySelector('.dashboard-screen').classList.remove('active');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}
</script>
"""

# ═══════════════════════════════════════════════════════════════════════════════
# SVG ICONS
# ═══════════════════════════════════════════════════════════════════════════════
SVG = {
    'virus': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 2v4m0 12v4M2 12h4m12 0h4"/><path d="m4.93 4.93 2.83 2.83m8.48 8.48 2.83 2.83m0-14.14-2.83 2.83m-8.48 8.48-2.83 2.83"/></svg>',
    'death': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>',
    'globe': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>',
    'percent': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="6" cy="6" r="3"/><circle cx="18" cy="18" r="3"/><path d="M20 4 4 20"/></svg>',
    'chart': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>',
    'map': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20M2 12h20"/></svg>',
    'health': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/></svg>',
    'bar': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20V10M18 20V4M6 20v-4"/></svg>',
    'pib': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v12M8 10h8M8 14h8"/></svg>',
    'filter': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 3H2l8 9.46V19l4 2v-8.54L22 3z"/></svg>',
    'arrow': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m9 18 6-6-6-6"/></svg>',
    'back': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m15 18-6-6 6-6"/></svg>',
    'daily': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>'
}

# ═══════════════════════════════════════════════════════════════════════════════
# UI DE LA APLICACIÓN
# ═══════════════════════════════════════════════════════════════════════════════
app_ui = ui.page_fluid(
    ui.HTML(css),
    
    # ╔═══════════════════════════════════════════════════════════════════════════╗
    # ║ PANTALLA DE INICIO CON KPIs GRANDES                                       ║
    # ╚═══════════════════════════════════════════════════════════════════════════╝
    ui.div(
        ui.div(
            # Badge
            ui.HTML(f'''
                <div class="intro-badge">
                    <span class="intro-badge-dot"></span>
                    <span>Panel de Análisis COVID-19</span>
                </div>
            '''),
            
            # Título
            ui.HTML('''
                <h1 class="intro-title">
                    COVID-19<br>
                    <span>Dashboard Interactivo 2025</span>
                </h1>
            '''),
            
            # Descripción
            ui.HTML('''
                <p class="intro-description">
                    Explora el impacto global de la pandemia con datos actualizados de más de 190 países. 
                    Analiza tendencias temporales, correlaciones con indicadores económicos y de salud.
                </p>
            '''),
            
            # KPIs GRANDES (informativos previos)
            ui.output_ui("intro_kpis"),
            
            # Botón para entrar
            ui.HTML(f'''
                <button class="btn-start" onclick="showDashboard()">
                    Explorar Dashboard
                    {SVG['arrow']}
                </button>
            '''),
            
            class_="intro-content"
        ),
        class_="intro-screen"
    ),
    
    # ╔═══════════════════════════════════════════════════════════════════════════╗
    # ║ PANTALLA DEL DASHBOARD                                                    ║
    # ╚═══════════════════════════════════════════════════════════════════════════╝
    ui.div(
        # KPIs STICKY (pequeños, fijos arriba)
        ui.div(
            ui.div(
                # Botón volver
                ui.HTML(f'''
                    <button class="btn-back" onclick="showIntro()">
                        {SVG['back']}
                        Inicio
                    </button>
                '''),
                ui.output_ui("sticky_kpis"),
                class_="sticky-kpis-inner"
            ),
            class_="sticky-kpis"
        ),
        
        # Panel de Filtros
        ui.div(
            ui.div(
                ui.HTML(f'''<span class="filter-bar-title">{SVG['filter']} Filtros de Visualización</span>'''),
            ),
            ui.row(
                ui.column(4,
                    ui.input_selectize("pais", "País:", choices=["Todos"] + paises, selected="Todos")
                ),
                ui.column(4,
                    ui.input_date("fecha_inicio", "Fecha inicio:", value=fecha_min, min=fecha_min, max=fecha_max)
                ),
                ui.column(4,
                    ui.input_date("fecha_fin", "Fecha fin:", value=fecha_max, min=fecha_min, max=fecha_max)
                )
            ),
            class_="filter-bar"
        ),
        
        # GRÁFICOS
        # 1. Evolución Temporal
        ui.div(
            ui.div(
                ui.span("01", class_="section-number"),
                ui.HTML(f'<div class="section-icon">{SVG["chart"]}</div>'),
                ui.div(
                    ui.h3("Evolución Temporal de Casos", class_="section-title"),
                    ui.p("Progresión de casos confirmados a lo largo del tiempo", class_="section-subtitle"),
                ),
                class_="section-header"
            ),
            output_widget("grafico_temporal"),
            class_="chart-section"
        ),
        
        # 2. Mapa Mundial
        ui.div(
            ui.div(
                ui.span("02", class_="section-number"),
                ui.HTML(f'<div class="section-icon">{SVG["map"]}</div>'),
                ui.div(
                    ui.h3("Mapa Global de Incidencia", class_="section-title"),
                    ui.p("Distribución geográfica de casos por cada 100.000 habitantes", class_="section-subtitle"),
                ),
                class_="section-header"
            ),
            output_widget("mapa_mundial"),
            class_="chart-section"
        ),
        
        # 3. Gasto en Salud vs Letalidad
        ui.div(
            ui.div(
                ui.span("03", class_="section-number"),
                ui.HTML(f'<div class="section-icon">{SVG["health"]}</div>'),
                ui.div(
                    ui.h3("Gasto en Salud vs Letalidad", class_="section-title"),
                    ui.p("Relación entre inversión sanitaria y tasa de letalidad", class_="section-subtitle"),
                ),
                class_="section-header"
            ),
            output_widget("scatter_salud"),
            class_="chart-section"
        ),
        
        # 4. Top Países
        ui.div(
            ui.div(
                ui.span("04", class_="section-number"),
                ui.HTML(f'<div class="section-icon">{SVG["bar"]}</div>'),
                ui.div(
                    ui.h3("Top 15 Países más Afectados", class_="section-title"),
                    ui.p("Ranking por número total de casos confirmados", class_="section-subtitle"),
                ),
                class_="section-header"
            ),
            output_widget("top_paises"),
            class_="chart-section"
        ),
        
        # 5. PIB vs Incidencia
        ui.div(
            ui.div(
                ui.span("05", class_="section-number"),
                ui.HTML(f'<div class="section-icon">{SVG["pib"]}</div>'),
                ui.div(
                    ui.h3("PIB per Cápita vs Incidencia", class_="section-title"),
                    ui.p("Correlación entre desarrollo económico e impacto del COVID-19", class_="section-subtitle"),
                ),
                class_="section-header"
            ),
            output_widget("scatter_pib"),
            class_="chart-section"
        ),
        
        # 6. Casos Diarios
        ui.div(
            ui.div(
                ui.span("06", class_="section-number"),
                ui.HTML(f'<div class="section-icon">{SVG["daily"]}</div>'),
                ui.div(
                    ui.h3("Evolución de Casos Diarios", class_="section-title"),
                    ui.p("Nuevos casos reportados por día", class_="section-subtitle"),
                ),
                class_="section-header"
            ),
            output_widget("casos_diarios"),
            class_="chart-section"
        ),
        
        # Footer
        ui.HTML('''
            <div class="footer">
                Dashboard COVID-19 2025 | Datos: WHO & World Bank | Shiny for Python + Plotly
            </div>
        '''),
        
        class_="dashboard-screen"
    )
)

# ═══════════════════════════════════════════════════════════════════════════════
# SERVER
# ═══════════════════════════════════════════════════════════════════════════════
def server(input, output, session):
    
    # Función para formatear números
    def fmt(n):
        if n >= 1_000_000_000:
            return f"{n/1_000_000_000:.2f}B"
        elif n >= 1_000_000:
            return f"{n/1_000_000:.2f}M"
        elif n >= 1_000:
            return f"{n/1_000:.1f}K"
        return f"{n:,.0f}"
    
    # ═══════════════════════════════════════════════════════════════════════════
    # DATOS REACTIVOS
    # ═══════════════════════════════════════════════════════════════════════════
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
            return pd.DataFrame()
        return data.loc[data.groupby('pais')['fecha'].idxmax()]
    
    @reactive.calc
    def datos_globales():
        """Datos globales para KPIs de inicio (sin filtros)"""
        return df_ultimo
    
    # ═══════════════════════════════════════════════════════════════════════════
    # KPIs DE INICIO (GRANDES)
    # ═══════════════════════════════════════════════════════════════════════════
    @output
    @render.ui
    def intro_kpis():
        data = datos_globales()
        
        total_casos = int(data['confirmados'].sum())
        total_muertes = int(data['muertes'].sum())
        total_paises = data['pais'].nunique()
        avg_letalidad = data['letalidad_CFR_pct'].mean()
        
        return ui.HTML(f'''
            <div class="intro-kpis">
                <div class="intro-kpi casos">
                    <div class="intro-kpi-icon">{SVG['virus']}</div>
                    <div class="intro-kpi-value">{fmt(total_casos)}</div>
                    <div class="intro-kpi-label">Casos Confirmados</div>
                    <div class="intro-kpi-detail">Total acumulado global</div>
                </div>
                <div class="intro-kpi muertes">
                    <div class="intro-kpi-icon">{SVG['death']}</div>
                    <div class="intro-kpi-value">{fmt(total_muertes)}</div>
                    <div class="intro-kpi-label">Fallecidos</div>
                    <div class="intro-kpi-detail">Muertes confirmadas</div>
                </div>
                <div class="intro-kpi paises">
                    <div class="intro-kpi-icon">{SVG['globe']}</div>
                    <div class="intro-kpi-value">{total_paises}</div>
                    <div class="intro-kpi-label">Países</div>
                    <div class="intro-kpi-detail">Territorios analizados</div>
                </div>
                <div class="intro-kpi letalidad">
                    <div class="intro-kpi-icon">{SVG['percent']}</div>
                    <div class="intro-kpi-value">{avg_letalidad:.2f}%</div>
                    <div class="intro-kpi-label">Letalidad Media</div>
                    <div class="intro-kpi-detail">Tasa CFR promedio</div>
                </div>
            </div>
        ''')
    
    # ═══════════════════════════════════════════════════════════════════════════
    # KPIs STICKY (PEQUEÑOS - EN DASHBOARD)
    # ═══════════════════════════════════════════════════════════════════════════
    @output
    @render.ui
    def sticky_kpis():
        data = datos_ultimo()
        
        if len(data) == 0:
            return ui.HTML("<div>Sin datos</div>")
        
        total_casos = int(data['confirmados'].sum())
        total_muertes = int(data['muertes'].sum())
        total_paises = data['pais'].nunique()
        avg_letalidad = data['letalidad_CFR_pct'].mean()
        
        return ui.HTML(f'''
            <div class="sticky-kpi casos">
                <div class="sticky-kpi-icon">{SVG['virus']}</div>
                <div class="sticky-kpi-info">
                    <div class="sticky-kpi-value">{fmt(total_casos)}</div>
                    <div class="sticky-kpi-label">Casos</div>
                </div>
            </div>
            <div class="sticky-kpi muertes">
                <div class="sticky-kpi-icon">{SVG['death']}</div>
                <div class="sticky-kpi-info">
                    <div class="sticky-kpi-value">{fmt(total_muertes)}</div>
                    <div class="sticky-kpi-label">Muertes</div>
                </div>
            </div>
            <div class="sticky-kpi paises">
                <div class="sticky-kpi-icon">{SVG['globe']}</div>
                <div class="sticky-kpi-info">
                    <div class="sticky-kpi-value">{total_paises}</div>
                    <div class="sticky-kpi-label">Países</div>
                </div>
            </div>
            <div class="sticky-kpi letalidad">
                <div class="sticky-kpi-icon">{SVG['percent']}</div>
                <div class="sticky-kpi-info">
                    <div class="sticky-kpi-value">{avg_letalidad:.2f}%</div>
                    <div class="sticky-kpi-label">Letalidad</div>
                </div>
            </div>
        ''')
    
    # ═══════════════════════════════════════════════════════════════════════════
    # GRÁFICOS
    # ═══════════════════════════════════════════════════════════════════════════
    
    @render_widget
    def grafico_temporal():
        data = datos_filtrados()
        
        if len(data) == 0:
            fig = go.Figure()
            fig.add_annotation(text="Sin datos disponibles", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        elif input.pais() != "Todos":
            fig = px.line(data, x='fecha', y='confirmados',
                         labels={'fecha': 'Fecha', 'confirmados': 'Casos Confirmados'},
                         color_discrete_sequence=['#6366f1'])
            fig.update_traces(line=dict(width=3))
        else:
            top = data.loc[data.groupby('pais')['confirmados'].idxmax()].nlargest(8, 'confirmados')['pais'].tolist()
            data_top = data[data['pais'].isin(top)]
            fig = px.line(data_top, x='fecha', y='confirmados', color='pais',
                         labels={'fecha': 'Fecha', 'confirmados': 'Casos', 'pais': 'País'},
                         color_discrete_sequence=px.colors.qualitative.Set2)
        
        fig.update_layout(
            height=450,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='rgba(255,255,255,0.8)', family='Inter'),
            legend=dict(orientation="h", y=1.02, x=0.5, xanchor="center", bgcolor='rgba(0,0,0,0)'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.08)', linecolor='rgba(255,255,255,0.1)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.08)', linecolor='rgba(255,255,255,0.1)'),
            margin=dict(l=50, r=30, t=30, b=50)
        )
        return fig
    
    @render_widget
    def mapa_mundial():
        data = datos_ultimo()
        
        if len(data) == 0:
            fig = go.Figure()
            fig.add_annotation(text="Sin datos disponibles", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        else:
            fig = px.choropleth(
                data,
                locations='iso3c',
                color='IA_100k',
                hover_name='pais',
                hover_data={'confirmados': ':,.0f', 'muertes': ':,.0f', 'IA_100k': ':,.1f', 'letalidad_CFR_pct': ':.2f'},
                color_continuous_scale=['#ddd6fe', '#a78bfa', '#7c3aed', '#5b21b6'],
                labels={'IA_100k': 'Incidencia/100k'}
            )
            fig.update_geos(
                showframe=False,
                showcoastlines=True,
                coastlinecolor='rgba(99,102,241,0.3)',
                projection_type='natural earth',
                bgcolor='rgba(0,0,0,0)',
                landcolor='rgba(25,25,50,0.8)',
                oceancolor='rgba(10,10,25,1)',
                showland=True,
                showocean=True
            )
        
        fig.update_layout(
            height=500,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='rgba(255,255,255,0.8)', family='Inter'),
            margin=dict(l=0, r=0, t=20, b=0)
        )
        return fig
    
    @render_widget
    def scatter_salud():
        data = datos_ultimo()
        data = data[data['gasto_salud_pib'] > 0]
        
        if len(data) == 0:
            fig = go.Figure()
            fig.add_annotation(text="Sin datos", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        else:
            fig = px.scatter(
                data,
                x='gasto_salud_pib',
                y='letalidad_CFR_pct',
                size='poblacion',
                color='pib_per_capita_2019',
                hover_name='pais',
                color_continuous_scale=['#10b981', '#f59e0b', '#ef4444'],
                labels={
                    'gasto_salud_pib': 'Gasto en Salud (% PIB)',
                    'letalidad_CFR_pct': 'Letalidad (%)',
                    'pib_per_capita_2019': 'PIB/cápita'
                }
            )
        
        fig.update_layout(
            height=450,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='rgba(255,255,255,0.8)', family='Inter'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.08)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.08)'),
            margin=dict(l=50, r=30, t=30, b=50)
        )
        return fig
    
    @render_widget
    def top_paises():
        data = datos_ultimo()
        
        if len(data) == 0:
            fig = go.Figure()
            fig.add_annotation(text="Sin datos", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        else:
            top = data.nlargest(15, 'confirmados')
            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=top['pais'],
                x=top['confirmados'],
                orientation='h',
                marker=dict(color=top['confirmados'], colorscale=[[0, '#6366f1'], [0.5, '#a855f7'], [1, '#ec4899']]),
                hovertemplate='<b>%{y}</b><br>Casos: %{x:,.0f}<extra></extra>'
            ))
        
        fig.update_layout(
            height=500,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='rgba(255,255,255,0.8)', family='Inter'),
            yaxis=dict(categoryorder='total ascending', gridcolor='rgba(255,255,255,0.08)'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.08)', title='Casos Confirmados'),
            margin=dict(l=120, r=30, t=30, b=50)
        )
        return fig
    
    @render_widget
    def scatter_pib():
        data = datos_ultimo()
        data = data[data['pib_per_capita_2019'] > 0]
        
        if len(data) == 0:
            fig = go.Figure()
            fig.add_annotation(text="Sin datos", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        else:
            fig = px.scatter(
                data,
                x='pib_per_capita_2019',
                y='IA_100k',
                size='poblacion',
                color='letalidad_CFR_pct',
                hover_name='pais',
                color_continuous_scale=['#10b981', '#f59e0b', '#ef4444'],
                labels={
                    'pib_per_capita_2019': 'PIB per Cápita ($)',
                    'IA_100k': 'Incidencia/100k hab',
                    'letalidad_CFR_pct': 'Letalidad %'
                }
            )
        
        fig.update_layout(
            height=450,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='rgba(255,255,255,0.8)', family='Inter'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.08)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.08)'),
            margin=dict(l=50, r=30, t=30, b=50)
        )
        return fig
    
    @render_widget
    def casos_diarios():
        data = datos_filtrados()
        
        if len(data) == 0:
            fig = go.Figure()
            fig.add_annotation(text="Sin datos", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        elif input.pais() != "Todos":
            fig = px.area(data, x='fecha', y='confirmados_dia',
                         labels={'fecha': 'Fecha', 'confirmados_dia': 'Casos Diarios'},
                         color_discrete_sequence=['#6366f1'])
        else:
            top = data.loc[data.groupby('pais')['confirmados'].idxmax()].nlargest(5, 'confirmados')['pais'].tolist()
            data_top = data[data['pais'].isin(top)]
            fig = px.line(data_top, x='fecha', y='confirmados_dia', color='pais',
                         labels={'fecha': 'Fecha', 'confirmados_dia': 'Casos Diarios', 'pais': 'País'},
                         color_discrete_sequence=px.colors.qualitative.Set2)
        
        fig.update_layout(
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='rgba(255,255,255,0.8)', family='Inter'),
            legend=dict(orientation="h", y=-0.15, bgcolor='rgba(0,0,0,0)'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.08)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.08)'),
            margin=dict(l=50, r=30, t=30, b=80)
        )
        return fig

# ═══════════════════════════════════════════════════════════════════════════════
# APP
# ═══════════════════════════════════════════════════════════════════════════════
app = App(app_ui, server)
