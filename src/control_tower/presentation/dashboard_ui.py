"""Corporate dashboard HTML renderer.

ADR references:
- ADR-0018: Corporate executive dashboard.
"""


def render_dashboard_html() -> str:
    """Return the integrated executive dashboard shell."""

    return """<!doctype html>
<html lang="es" data-theme="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>BIMSIG Corporate Dashboard</title>
  <style>
    :root {
      color-scheme: dark;
      --bg: #080d11;
      --panel: #11181f;
      --panel-strong: #1a242d;
      --text: #f3f6f8;
      --muted: #a9b4bf;
      --line: #2b3944;
      --accent: #41d19a;
      --accent-soft: rgba(65, 209, 154, .16);
      --warn: #d6a94a;
      --critical: #d96c6c;
      --radar: #0a1619;
      --glass: rgba(255, 255, 255, .045);
    }
    [data-theme="light"] {
      color-scheme: light;
      --bg: #f4f6f8;
      --panel: #ffffff;
      --panel-strong: #eef2f5;
      --text: #182026;
      --muted: #60707f;
      --line: #dbe2e8;
      --accent: #187a59;
      --accent-soft: rgba(24, 122, 89, .14);
      --warn: #9a6a13;
      --critical: #b84242;
      --radar: #dce8ee;
      --glass: rgba(24, 32, 38, .045);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: Inter, Segoe UI, Arial, sans-serif;
      letter-spacing: 0;
    }
    .shell { min-height: 100vh; display: grid; grid-template-columns: 280px 1fr; }
    aside {
      border-right: 1px solid var(--line);
      background: var(--panel);
      padding: 24px;
      position: sticky;
      top: 0;
      height: 100vh;
    }
    main {
      padding: 24px;
      background:
        radial-gradient(circle at 50% -10%, var(--accent-soft), transparent 42%),
        linear-gradient(180deg, transparent, rgba(0, 0, 0, .22));
    }
    .brand { font-size: 14px; color: var(--muted); margin-bottom: 8px; }
    h1 { font-size: 28px; line-height: 1.1; margin: 0 0 28px; }
    h2 { font-size: 16px; margin: 0 0 14px; }
    .experience-label {
      color: var(--accent);
      font-size: 12px;
      font-weight: 760;
      letter-spacing: 1.6px;
      text-transform: uppercase;
      margin: -16px 0 22px;
    }
    .process-nav { display: grid; gap: 8px; margin: 18px 0; }
    .process-nav a {
      border: 1px solid var(--line);
      background: var(--panel-strong);
      color: var(--text);
      border-radius: 8px;
      padding: 10px 12px;
      text-decoration: none;
      font-weight: 650;
    }
    .process-nav a:hover { border-color: var(--accent); color: var(--accent); }
    .process-nav a.active { background: var(--accent-soft); border-color: var(--accent); color: var(--accent); }
    .experience-header {
      margin-bottom: 14px;
      padding: 14px 16px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: linear-gradient(90deg, var(--accent-soft), transparent 52%), var(--panel);
    }
    .experience-header h2 { margin-bottom: 6px; }
    .section-kicker { color: var(--muted); font-size: 12px; margin: -8px 0 14px; }
    label { display: block; color: var(--muted); font-size: 12px; margin-bottom: 8px; }
    input, button {
      width: 100%;
      border: 1px solid var(--line);
      background: var(--panel-strong);
      color: var(--text);
      border-radius: 8px;
      padding: 11px 12px;
      font: inherit;
    }
    button { cursor: pointer; margin-top: 10px; font-weight: 650; }
    button.primary { background: var(--accent); border-color: var(--accent); color: #fff; }
    .topbar { display: flex; justify-content: space-between; gap: 16px; align-items: center; margin-bottom: 18px; }
    .topbar .title { min-width: 220px; }
    .toolbar { display: flex; gap: 10px; align-items: center; }
    .toolbar button { width: auto; min-width: 112px; margin: 0; }
    .grid { display: grid; gap: 14px; }
    .summary { grid-template-columns: repeat(4, minmax(0, 1fr)); margin-bottom: 14px; }
    .content { grid-template-columns: minmax(0, 1.25fr) minmax(360px, .75fr); align-items: start; }
    .section {
      background: linear-gradient(180deg, var(--glass), transparent), var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
      box-shadow: inset 0 1px 0 rgba(255,255,255,.04), 0 18px 42px rgba(0,0,0,.18);
    }
    .metric-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
    .home-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); margin-bottom: 14px; }
    .metric { min-height: 88px; background: var(--panel-strong); border: 1px solid var(--line); border-radius: 8px; padding: 12px; }
    .metric .label { color: var(--muted); font-size: 12px; }
    .metric .value { font-size: 24px; font-weight: 760; margin-top: 8px; }
    .metric.watch { border-color: var(--warn); }
    .metric.critical { border-color: var(--critical); }
    .cockpit {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin-bottom: 14px;
    }
    .instrument {
      min-height: 118px;
      background: radial-gradient(circle at 50% 0%, var(--accent-soft), transparent 58%), var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
      position: relative;
      overflow: hidden;
    }
    .instrument::after {
      content: "";
      position: absolute;
      inset: auto 12px 12px 12px;
      height: 34px;
      border: 1px solid var(--line);
      border-top: 0;
      border-radius: 0 0 50px 50px;
      opacity: .75;
    }
    .instrument .label { color: var(--muted); font-size: 12px; }
    .instrument .value { font-size: 26px; font-weight: 780; margin-top: 8px; }
    .radar-shell {
      min-height: 520px;
      display: grid;
      grid-template-columns: minmax(320px, 1fr) 220px;
      gap: 16px;
      align-items: stretch;
    }
    .radar {
      min-height: 500px;
      aspect-ratio: 1 / 1;
      position: relative;
      overflow: hidden;
      margin: 0 auto;
      background:
        radial-gradient(circle at 50% 50%, rgba(65, 209, 154, .18), transparent 7%),
        radial-gradient(circle at 50% 50%, transparent 0 18%, rgba(65, 209, 154, .16) 18.4% 18.8%, transparent 19.2% 37%, rgba(65, 209, 154, .14) 37.4% 37.8%, transparent 38.2% 56%, rgba(65, 209, 154, .12) 56.4% 56.8%, transparent 57.2% 75%, rgba(65, 209, 154, .10) 75.4% 75.8%, transparent 76.2%),
        linear-gradient(90deg, transparent 49.8%, rgba(65, 209, 154, .25) 50%, transparent 50.2%),
        linear-gradient(0deg, transparent 49.8%, rgba(65, 209, 154, .25) 50%, transparent 50.2%),
        var(--radar);
      border: 1px solid var(--line);
      border-radius: 50%;
      box-shadow: inset 0 0 70px rgba(65, 209, 154, .14), 0 0 0 10px rgba(255,255,255,.025);
    }
    .radar::before {
      content: "";
      position: absolute;
      left: 50%;
      top: 50%;
      width: 50%;
      height: 50%;
      transform-origin: 0 0;
      background: linear-gradient(35deg, rgba(65, 209, 154, .46), rgba(65, 209, 154, .08) 42%, transparent 65%);
      animation: sweep 5s linear infinite;
      clip-path: polygon(0 0, 100% 0, 0 100%);
    }
    .radar::after {
      content: "CORPORATE RADAR";
      position: absolute;
      left: 50%;
      bottom: 22px;
      transform: translateX(-50%);
      color: var(--muted);
      font-size: 11px;
      letter-spacing: 2px;
    }
    @keyframes sweep {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }
    .point {
      position: absolute;
      width: 14px;
      height: 14px;
      border-radius: 50%;
      background: var(--accent);
      border: 2px solid var(--panel);
      transform: translate(-50%, -50%);
      box-shadow: 0 0 18px var(--accent);
      z-index: 2;
    }
    .point span {
      position: absolute;
      left: 16px;
      top: -8px;
      white-space: nowrap;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 4px 6px;
      font-size: 11px;
    }
    .radar-side {
      display: grid;
      align-content: start;
      gap: 10px;
    }
    .governance-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; }
    .governance-card {
      background: var(--panel-strong);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      min-height: 132px;
    }
    .governance-card .project { font-weight: 760; margin-bottom: 8px; }
    .governance-card .meta { color: var(--muted); font-size: 12px; line-height: 1.45; }
    details.governance-card summary { cursor: pointer; list-style: none; }
    details.governance-card summary::-webkit-details-marker { display: none; }
    details.governance-card[open] { border-color: var(--accent); }
    .portfolio-path {
      display: grid;
      gap: 6px;
      margin-top: 10px;
      font-size: 12px;
      color: var(--muted);
    }
    .portfolio-path strong { color: var(--text); font-weight: 700; }
    .chips { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }
    .chip {
      border: 1px solid var(--line);
      border-radius: 999px;
      color: var(--muted);
      font-size: 11px;
      padding: 4px 7px;
    }
    .chip.ready { color: var(--accent); border-color: var(--accent); }
    .filter-row { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 8px; margin-bottom: 12px; }
    .filter-row input, .filter-row button {
      min-width: 0;
      font-size: 12px;
      padding: 9px 10px;
      margin: 0;
    }
    .filter-row button.active { color: var(--accent); border-color: var(--accent); background: var(--accent-soft); }
    .map-mode-grid { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 8px; margin-bottom: 12px; }
    .mode-pill {
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 9px 10px;
      background: var(--panel-strong);
      color: var(--muted);
      text-align: center;
      font-size: 12px;
      font-weight: 700;
    }
    .mode-pill.active { color: var(--accent); border-color: var(--accent); background: var(--accent-soft); }
    .wizard-steps { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 8px; }
    .wizard-step {
      min-height: 76px;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 10px;
      background: var(--panel-strong);
      display: grid;
      align-content: space-between;
    }
    .wizard-step .number { color: var(--accent); font-weight: 780; font-size: 12px; }
    .wizard-step .name { font-weight: 720; }
    .wizard-step .state { color: var(--muted); font-size: 11px; }
    .notification-list { display: grid; gap: 8px; }
    .notification {
      display: grid;
      grid-template-columns: minmax(150px, .38fr) minmax(0, 1fr) minmax(150px, auto);
      gap: 14px;
      align-items: center;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 10px 12px;
      background: var(--panel-strong);
      font-size: 13px;
    }
    .notification .kind {
      color: var(--accent);
      font-weight: 760;
      text-transform: uppercase;
      font-size: 11px;
      overflow-wrap: anywhere;
      line-height: 1.25;
    }
    .notification .message {
      min-width: 0;
      overflow-wrap: anywhere;
      line-height: 1.35;
    }
    .notification .time { color: var(--muted); font-size: 11px; text-align: right; white-space: nowrap; }
    .question-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
    .question-card {
      min-height: 96px;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      background: var(--panel-strong);
    }
    .question-card .answer { font-size: 24px; font-weight: 780; margin: 8px 0 4px; }
    .question-card a {
      color: var(--accent);
      font-size: 12px;
      font-weight: 720;
      text-decoration: none;
    }
    .flow-grid { display: grid; gap: 10px; }
    .flow-card {
      display: grid;
      grid-template-columns: minmax(180px, .8fr) minmax(220px, 1fr) 92px;
      gap: 12px;
      align-items: center;
      background: var(--panel-strong);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
    }
    .flow-card .state { font-size: 12px; color: var(--accent); text-transform: uppercase; }
    .flow-card .phase { color: var(--muted); font-size: 12px; margin-top: 5px; }
    .flow-card .next { font-size: 13px; line-height: 1.35; }
    .flow-card .pending { color: var(--muted); font-size: 12px; margin-top: 5px; }
    .flow-score {
      display: grid;
      place-items: center;
      min-height: 64px;
      border: 1px solid var(--accent);
      border-radius: 8px;
      color: var(--accent);
      font-weight: 780;
    }
    .operating-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
    .lane-card {
      background: var(--panel-strong);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      min-height: 124px;
    }
    .lane-card .name { font-weight: 760; }
    .lane-card .owner { color: var(--muted); font-size: 12px; margin-top: 4px; }
    .lane-card .score { color: var(--accent); font-size: 22px; font-weight: 780; margin-top: 8px; }
    .actions-list { display: grid; gap: 8px; margin-top: 12px; }
    .action-item {
      background: var(--panel-strong);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 10px 12px;
      color: var(--muted);
      font-size: 13px;
    }
    .readout {
      min-height: 72px;
      background: var(--panel-strong);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
    }
    .readout .label { color: var(--muted); font-size: 11px; text-transform: uppercase; }
    .readout .value { font-size: 22px; font-weight: 780; margin-top: 6px; }
    table { width: 100%; border-collapse: collapse; font-size: 13px; }
    th, td { border-bottom: 1px solid var(--line); padding: 10px 8px; text-align: left; }
    th { color: var(--muted); font-weight: 650; }
    .stack { display: grid; gap: 14px; }
    .tabs { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 14px; }
    .tabs button { margin: 0; padding: 9px; }
    .tabs button.active { background: var(--accent); color: #fff; border-color: var(--accent); }
    .muted { color: var(--muted); }
    @media (max-width: 1100px) {
      .shell { grid-template-columns: 1fr; }
      aside { position: static; height: auto; border-right: 0; border-bottom: 1px solid var(--line); }
      .summary { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .home-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .content { grid-template-columns: 1fr; }
      .cockpit { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .radar-shell { grid-template-columns: 1fr; }
      .radar { min-height: 380px; width: min(100%, 520px); }
      .governance-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }
    @media (max-width: 700px) {
      main { padding: 14px; }
      .summary, .metric-grid, .cockpit, .governance-grid { grid-template-columns: 1fr; }
      .topbar { align-items: stretch; flex-direction: column; }
      .toolbar { justify-content: space-between; }
      .toolbar button { flex: 1; min-width: 0; }
      .process-nav { grid-template-columns: 1fr; }
      table { font-size: 12px; }
      th:nth-child(4), td:nth-child(4), th:nth-child(5), td:nth-child(5) { display: none; }
      .radar { min-height: 300px; }
      .radar::after { display: none; }
      .flow-card { grid-template-columns: 1fr; }
      .operating-grid { grid-template-columns: 1fr; }
      .filter-row, .map-mode-grid, .wizard-steps, .question-grid { grid-template-columns: 1fr; }
      .notification { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="shell">
    <aside>
      <div class="brand">BIMSIG Enterprise</div>
      <h1>Corporate Control Tower</h1>
      <div class="experience-label">Corporate Experience</div>
      <label for="companyId">Empresa</label>
      <input id="companyId" value="CRTG" autocomplete="off">
      <button class="primary" id="load">Actualizar</button>
      <button id="theme">Light Mode</button>
      <nav class="process-nav" aria-label="Corporate Navigation">
        <a class="active" href="#corporateHome">Inicio</a>
        <a href="#portfolioExplorer">Portafolio</a>
        <a href="#corporateGisDashboard">Mapa Corporativo</a>
        <a href="#enterpriseWizard">Provisionamiento</a>
        <a href="#corporateDashboard">Empresas</a>
        <a href="#panels">Usuarios</a>
        <a href="#panels">Licencias</a>
        <a href="#operatingModelSection">Configuracion</a>
        <a href="#corporateNotifications">Auditoria</a>
        <a href="#operationalFlowSection">Administracion</a>
      </nav>
      <p class="muted">Dashboard Ejecutivo Corporativo de BIMSIG Enterprise REV13.</p>
    </aside>
    <main>
      <div class="topbar">
        <div class="title">
          <div class="brand">Corporate Control Tower</div>
          <h1 id="heading">Resumen ejecutivo</h1>
        </div>
        <div class="toolbar">
          <button data-panel="operations" class="active">Inicio</button>
          <button data-panel="governance">Auditoria</button>
          <button data-panel="enterprise">Administracion</button>
        </div>
      </div>
      <section class="experience-header" id="corporateHome">
        <h2>Corporate Home</h2>
        <div class="muted">Centro de Gobierno Corporativo para portafolio, GIS, NAS, provisionamiento, alertas y acciones pendientes.</div>
      </section>
      <section class="grid home-grid" id="corporateHomeCards"></section>
      <section class="experience-header" id="corporateDashboard">
        <h2>Corporate Dashboard / Control Ejecutivo</h2>
        <div class="muted">Estado ejecutivo del portafolio, empresas, programas, proyectos, riesgos y desempeno corporativo.</div>
      </section>
      <section class="cockpit" id="cockpit"></section>
      <section class="grid summary" id="summary"></section>
      <section class="grid content">
        <div class="stack">
          <section class="section" id="corporateGisDashboard">
            <h2>Corporate GIS Dashboard / GIS Corporativo</h2>
            <div class="section-kicker">Mapa corporativo GIS - Solo lectura - Corporate Layers publicadas por WEB SIG Enterprise.</div>
            <div class="map-mode-grid" id="gisMapModes"></div>
            <div class="filter-row" id="gisFilters">
              <button data-gis-filter="estado">Estado</button>
              <button data-gis-filter="riesgo">Riesgo</button>
              <button data-gis-filter="calidad">Calidad</button>
              <button data-gis-filter="ambiental">Ambiental</button>
              <button data-gis-filter="ssoma">SSOMA</button>
              <button data-gis-filter="produccion">Produccion</button>
            </div>
            <div class="radar-shell">
              <div class="radar" id="map"></div>
              <div class="radar-side" id="radarReadouts"></div>
            </div>
          </section>
          <section class="section" id="portfolioExplorer">
            <h2>Explorador de Portafolio</h2>
            <div class="section-kicker">Empresa / Programa / Proyecto / WEB SIG / Estado / Dashboard.</div>
            <div class="filter-row" id="portfolioFilters">
              <button data-portfolio-filter="all" class="active">Empresa</button>
              <button data-portfolio-filter="program">Programa</button>
              <button data-portfolio-filter="active">Estado</button>
              <button data-portfolio-filter="customer">Cliente</button>
              <button data-portfolio-filter="contract">Contrato</button>
              <button data-portfolio-filter="owner">Responsable / Fecha</button>
            </div>
            <div class="governance-grid" id="portfolioGovernance"></div>
          </section>
          <section class="section" id="enterpriseWizard">
            <h2>Corporate Wizard</h2>
            <div class="section-kicker">Flujo visual del Enterprise Wizard con avance parcial, validacion y progreso por etapa.</div>
            <div class="wizard-steps" id="wizardSteps"></div>
          </section>
          <section class="section" id="operationalFlowSection">
            <h2>Flujo Operacional</h2>
            <div class="flow-grid" id="operationalFlow"></div>
          </section>
          <section class="section" id="operatingModelSection">
            <h2>Modelo Operativo Corporativo</h2>
            <div class="operating-grid" id="operatingModel"></div>
            <div class="actions-list" id="priorityActions"></div>
          </section>
          <section class="section">
            <h2>Inteligencia Geoespacial Corporativa</h2>
            <div class="section-kicker">Consulta consolidada de capas corporativas; sin edicion ni digitalizacion.</div>
            <div class="metric-grid" id="gisIntelligence"></div>
          </section>
          <section class="section" id="projectComparisons">
            <h2>Comparativos entre proyectos</h2>
            <table>
              <thead>
                <tr><th>Proyecto</th><th>Estado</th><th>KPI</th><th>Produccion</th><th>Riesgo</th></tr>
              </thead>
              <tbody id="comparisons"></tbody>
            </table>
          </section>
          <section class="section">
            <h2>Executive Dashboard</h2>
            <div class="question-grid" id="executiveQuestions"></div>
          </section>
          <section class="section" id="corporateNotifications">
            <h2>Corporate Notifications</h2>
            <div class="notification-list" id="notifications"></div>
          </section>
        </div>
        <div class="stack" id="panels"></div>
      </section>
    </main>
  </div>
  <script>
    const panelGroups = {
      operations: ["kpis", "production", "schedule", "environmental", "ssoma", "quality"],
      governance: ["risks", "alerts", "ai"],
      enterprise: ["users", "licenses"]
    };
    const titles = {
      kpis: "KPIs",
      risks: "Riesgos",
      production: "Produccion",
      schedule: "Cronograma",
      environmental: "Ambiental",
      ssoma: "SSOMA",
      quality: "Calidad",
      users: "Usuarios",
      licenses: "Licencias",
      ai: "IA",
      alerts: "Alertas"
    };
    let currentPanel = "operations";
    let data = null;
    let gisMap = null;
    let portfolioProjects = [];
    let wizardSessions = [];
    let auditEvents = [];
    let activePortfolioFilter = "all";
    let activeGisFilter = "estado";

    async function loadDashboard() {
      const companyId = document.querySelector("#companyId").value.trim();
      const encodedCompany = encodeURIComponent(companyId);
      const response = await fetch(`/api/v1/companies/${encodedCompany}/dashboard/executive`);
      if (!response.ok) {
        document.querySelector("#heading").textContent = "Empresa no encontrada";
        return;
      }
      data = await response.json();
      gisMap = null;
      portfolioProjects = [];
      wizardSessions = [];
      auditEvents = [];
      try {
        const [gisResponse, projectsResponse, wizardResponse, auditResponse] = await Promise.all([
          fetch(`/api/v1/companies/${encodedCompany}/gis-intelligence/maps/corporate`),
          fetch(`/api/v1/companies/${encodedCompany}/projects`),
          fetch("/api/v1/enterprise-wizard"),
          fetch("/api/v1/audit/events?limit=12")
        ]);
        gisMap = gisResponse.ok ? await gisResponse.json() : null;
        portfolioProjects = projectsResponse.ok ? await projectsResponse.json() : [];
        wizardSessions = wizardResponse.ok ? await wizardResponse.json() : [];
        auditEvents = auditResponse.ok ? await auditResponse.json() : [];
      } catch {
        gisMap = null;
      }
      render();
    }

    function render() {
      document.querySelector("#heading").textContent = `Resumen ejecutivo ${data.company_id}`;
      renderCorporateHome();
      renderSummary();
      renderCockpit();
      renderMap();
      renderPortfolioGovernance();
      renderWizard();
      renderOperationalFlow();
      renderOperatingModel();
      renderGisIntelligence();
      renderExecutiveQuestions();
      renderNotifications();
      renderPanels();
      renderComparisons();
    }

    function renderCorporateHome() {
      const portfolio = data.portfolio;
      const governed = data.portfolio_governance || [];
      const flow = data.operational_flow || [];
      const active = portfolio.active_projects ?? 0;
      const archived = governed.filter(item => item.lifecycle_stage === "archived").length;
      const suspended = governed.filter(item => item.governance_status === "suspended").length;
      const nasReady = governed.filter(item => item.nas !== "pendiente").length;
      const websigReady = governed.filter(item => item.websig !== "pendiente").length;
      const blocked = flow.filter(item => item.pending_controls.length > 0).length;
      const cards = [
        ["Estado general del portafolio", active ? "activo" : "intake", "Portfolio"],
        ["Empresas", 1, "Enterprise"],
        ["Programas", uniqueCount(governed.map(item => item.program).filter(Boolean)), "Portfolio"],
        ["Proyectos activos", active, "Portfolio"],
        ["Proyectos suspendidos", suspended, "Governance"],
        ["Proyectos archivados", archived, "Records"],
        ["Corporate GIS", data.gis_intelligence?.projects_with_active_layers ?? 0, "GIS"],
        ["NAS", nasReady, "Information Center"],
        ["Provisioning", websigReady, "WEB SIG Factory"],
        ["Alertas", data.alerts[0]?.value ?? 0, "Risk"],
        ["Eventos recientes", recentEvents().length, "Audit"],
        ["Acciones pendientes", blocked, "Workflow"]
      ];
      document.querySelector("#corporateHomeCards").innerHTML = cards.map(([label, value, context]) => `
        <article class="metric">
          <div class="label">${label}</div>
          <div class="value">${value}</div>
          <div class="muted">${context}</div>
        </article>
      `).join("");
    }

    function renderCockpit() {
      const portfolio = data.portfolio;
      const governed = data.portfolio_governance || [];
      const websigReady = governed.filter(item => item.websig !== "pendiente").length;
      const gisReady = governed.filter(item => item.gis !== "pendiente").length;
      const instruments = [
        ["ALT", `${portfolio.total_projects ?? 0}`, "Portafolio"],
        ["LFC", `${activeLifecycleCount(governed)}`, "Lifecycle ejecutivo"],
        ["WEB", `${websigReady}`, "WEB SIG gobernadas"],
        ["GIS", `${gisReady}`, "GIS vinculados"]
      ];
      document.querySelector("#cockpit").innerHTML = instruments.map(([code, value, label]) => `
        <article class="instrument">
          <div class="label">${code} / ${label}</div>
          <div class="value">${value}</div>
        </article>
      `).join("");
    }

    function renderSummary() {
      const portfolio = data.portfolio;
      const governed = data.portfolio_governance || [];
      const gisSummary = data.gis_intelligence || {};
      const cards = [
        ["Estado portafolio", portfolio.active_projects ? "activo" : "intake"],
        ["Empresas", 1],
        ["Programas", uniqueCount(governed.map(item => item.program).filter(Boolean))],
        ["Proyectos", portfolio.total_projects ?? 0],
        ["Riesgos", data.risks[0]?.value ?? 0],
        ["Calidad", data.quality[0]?.value ?? "0%"],
        ["Produccion", data.production[0]?.value ?? "0%"],
        ["Ambiental", data.environmental[0]?.value ?? 0],
        ["SSOMA", data.ssoma[0]?.value ?? 0],
        ["GIS", gisSummary.projects_with_active_layers ?? 0]
      ];
      document.querySelector("#summary").innerHTML = cards.map(([label, value]) =>
        `<article class="metric"><div class="label">${label}</div><div class="value">${value}</div></article>`
      ).join("");
    }

    function renderMap() {
      const map = document.querySelector("#map");
      const readouts = document.querySelector("#radarReadouts");
      const modes = ["Mapa Nacional", "Mapa Regional", "Empresa", "Programa", "Proyecto"];
      document.querySelector("#gisMapModes").innerHTML = modes.map((mode, index) => `
        <div class="mode-pill ${index === 0 ? "active" : ""}">${mode}</div>
      `).join("");
      document.querySelectorAll("[data-gis-filter]").forEach(button => {
        button.classList.toggle("active", button.dataset.gisFilter === activeGisFilter);
      });
      if (!data.map_points.length) {
        map.innerHTML = `<div class="muted" style="padding:16px">Sin proyectos georreferenciados.</div>`;
        readouts.innerHTML = "";
        return;
      }
      map.innerHTML = data.map_points.map((point, index) => {
        const angle = (index * 58 + 230) * Math.PI / 180;
        const radius = 24 + (index * 13) % 30;
        const left = 50 + Math.cos(angle) * radius;
        const top = 50 + Math.sin(angle) * radius;
        return `<div class="point" style="left:${left}%;top:${top}%"><span>${point.name}</span></div>`;
      }).join("");
      readouts.innerHTML = [
        ["CONTACTOS", data.map_points.length],
        ["COBERTURA", data.kpis[2]?.value ?? "0%"],
        ["RIESGO", data.risks[0]?.value ?? "0"],
        ["CAPAS", gisMap?.layers?.length ?? 0],
        ["FILTROS", "9"],
        ["MODO", document.documentElement.dataset.theme.toUpperCase()]
      ].map(([label, value]) => `
        <article class="readout"><div class="label">${label}</div><div class="value">${value}</div></article>
      `).join("");
    }

    function renderPortfolioGovernance() {
      const target = document.querySelector("#portfolioGovernance");
      const items = filteredPortfolioItems();
      if (!items.length) {
        target.innerHTML = `<div class="muted">Sin proyectos gobernados.</div>`;
        return;
      }
      document.querySelectorAll("[data-portfolio-filter]").forEach(button => {
        button.classList.toggle("active", button.dataset.portfolioFilter === activePortfolioFilter);
      });
      target.innerHTML = items.map(item => {
        const flow = (data.operational_flow || []).find(flowItem => flowItem.project_id === item.project_id);
        const project = portfolioProjects.find(projectItem => projectItem.project_id === item.project_id) || {};
        return `
        <details class="governance-card" open>
          <summary>
            <div class="project">${item.project_name}</div>
            <div class="meta">${data.company_id} / ${item.program || "Programa pendiente"} / ${item.governance_status}</div>
          </summary>
          <div class="portfolio-path">
            <span><strong>Empresa</strong> ${data.company_id}</span>
            <span><strong>Programa</strong> ${item.program || "pendiente"}</span>
            <span><strong>Proyecto</strong> ${item.project_name}</span>
            <span><strong>WEB SIG Enterprise</strong> ${item.websig}</span>
            <span><strong>Estado</strong> ${item.governance_status}</span>
            <span><strong>Cliente</strong> ${item.customer || "pendiente"}</span>
            <span><strong>Contrato</strong> ${project.contract_id || item.contract || "pendiente"}</span>
            <span><strong>Responsable</strong> ${project.owner || item.owner || "pendiente"}</span>
            <span><strong>Fecha</strong> ${project.created_at || project.updated_at || "pendiente"}</span>
            <span><strong>Dashboard</strong> ${flow ? `${flow.readiness_score}%` : "pendiente"}</span>
          </div>
          <div class="chips">
            ${chip("WEB SIG", item.websig)}
            ${chip("NAS", item.nas)}
            ${chip("GIS", item.gis)}
            <span class="chip ready">Solo lectura</span>
          </div>
        </details>
      `;
      }).join("");
    }

    function filteredPortfolioItems() {
      const items = data.portfolio_governance || [];
      if (activePortfolioFilter === "active") {
        return items.filter(item => item.governance_status === "active" || item.lifecycle_stage === "active");
      }
      if (activePortfolioFilter === "program") {
        return [...items].sort((left, right) => String(left.program || "").localeCompare(String(right.program || "")));
      }
      if (activePortfolioFilter === "customer") {
        return items.filter(item => item.customer);
      }
      if (activePortfolioFilter === "contract") {
        return items.filter(item => {
          const project = portfolioProjects.find(projectItem => projectItem.project_id === item.project_id) || {};
          return project.contract_id || item.contract;
        });
      }
      if (activePortfolioFilter === "owner") {
        return items.filter(item => {
          const project = portfolioProjects.find(projectItem => projectItem.project_id === item.project_id) || {};
          return project.owner || item.owner || project.created_at || project.updated_at;
        });
      }
      return items;
    }

    function renderWizard() {
      const activeSession = wizardSessions[0];
      const steps = activeSession ? wizardSessionSteps(activeSession) : derivedWizardSteps();
      document.querySelector("#wizardSteps").innerHTML = steps.map(([name, ready], index) => `
        <article class="wizard-step">
          <div class="number">Paso ${index + 1}</div>
          <div class="name">${name}</div>
          <div class="state">${ready}</div>
        </article>
      `).join("");
    }

    function wizardSessionSteps(session) {
      const saved = Object.fromEntries((session.steps || []).map(step => [step.step, step]));
      const names = [
        "Empresa", "Programa", "Proyecto", "Ubicacion", "Especialidades",
        "Provisionamiento", "GIS", "NAS", "Usuarios", "Activacion"
      ];
      return names.map(name => {
        const key = wizardKey(name);
        const state = saved[key]?.status === "valid" ? "validado / autosave real" : "reanudable / pendiente";
        return [name, state];
      });
    }

    function wizardKey(name) {
      const map = {
        Empresa: "company",
        Programa: "program",
        Proyecto: "project",
        Ubicacion: "location",
        Especialidades: "specialties",
        Provisionamiento: "web_sig",
        GIS: "gis",
        NAS: "nas",
        Usuarios: "users",
        Activacion: "activation"
      };
      return map[name];
    }

    function derivedWizardSteps() {
      const governed = data.portfolio_governance || [];
      const hasProject = governed.length > 0;
      const websigReady = governed.some(item => item.websig !== "pendiente");
      const gisReady = governed.some(item => item.gis !== "pendiente");
      const nasReady = governed.some(item => item.nas !== "pendiente");
      const usersReady = (data.users || []).length > 0;
      return [
        ["Empresa", "validado / dato corporativo"],
        ["Programa", governed.some(item => item.program) ? "validado / dato real" : "pendiente / reanudable"],
        ["Proyecto", hasProject ? "validado / dato real" : "pendiente / reanudable"],
        ["Ubicacion", data.map_points.length > 0 ? "validado / dato real" : "pendiente / reanudable"],
        ["Especialidades", hasProject ? "validado / dato real" : "pendiente / reanudable"],
        ["Provisionamiento", websigReady ? "validado / WEB SIG registrada" : "pendiente / reanudable"],
        ["GIS", gisReady ? "validado / recurso GIS" : "pendiente / reanudable"],
        ["NAS", nasReady ? "validado / referencia NAS" : "pendiente / reanudable"],
        ["Usuarios", usersReady ? "validado / usuarios reales" : "pendiente / reanudable"],
        ["Activacion", (data.operational_flow || []).some(item => item.readiness_score >= 80) ? "validado / activable" : "pendiente / reanudable"]
      ];
    }

    function renderOperationalFlow() {
      const target = document.querySelector("#operationalFlow");
      const items = data.operational_flow || [];
      if (!items.length) {
        target.innerHTML = `<div class="muted">Sin flujo operacional calculado.</div>`;
        return;
      }
      target.innerHTML = items.map(item => {
        const pending = item.pending_controls.length
          ? item.pending_controls.slice(0, 2).join(" / ")
          : "Sin bloqueos de gobierno";
        return `
          <article class="flow-card">
            <div>
              <div class="project">${item.project_name}</div>
              <div class="state">${item.current_state}</div>
              <div class="phase">${labelPhase(item.active_phase)}</div>
            </div>
            <div>
              <div class="next">${item.next_action}</div>
              <div class="pending">${pending}</div>
            </div>
            <div class="flow-score">${item.readiness_score}%</div>
          </article>
        `;
      }).join("");
    }

    function renderGisIntelligence() {
      const target = document.querySelector("#gisIntelligence");
      const summary = data.gis_intelligence;
      if (!summary) {
        target.innerHTML = `<div class="muted">Sin inteligencia GIS corporativa.</div>`;
        return;
      }
      const cards = [
        ["Proyectos GIS", summary.total_projects_georeferenced],
        ["Capas activas", summary.projects_with_active_layers],
        ["Riesgos espaciales", summary.projects_with_spatial_risks],
        ["Alertas ambientales", summary.projects_with_environmental_alerts],
        ["Restricciones", summary.projects_with_active_restrictions],
        ["Avance espacial", `${summary.aggregated_spatial_progress}%`]
      ];
      const layers = (gisMap?.layers || []).slice(0, 6).map(layer => [
        `Layer ${layer.layer_type}`,
        `${layer.name} / ${layer.status}`
      ]);
      target.innerHTML = [...cards, ...layers].map(([label, value]) => `
        <article class="metric">
          <div class="label">${label}</div>
          <div class="value">${value}</div>
          <div class="muted">Solo lectura</div>
        </article>
      `).join("");
    }

    function renderOperatingModel() {
      const target = document.querySelector("#operatingModel");
      const actions = document.querySelector("#priorityActions");
      const model = data.operating_model;
      if (!model) {
        target.innerHTML = `<div class="muted">Sin modelo operativo calculado.</div>`;
        actions.innerHTML = "";
        return;
      }
      target.innerHTML = model.lanes.map(lane => `
        <article class="lane-card">
          <div class="name">${lane.name}</div>
          <div class="owner">${lane.owner}</div>
          <div class="score">${lane.readiness_score}%</div>
          <div class="muted">${lane.active_items} activos / ${lane.blocked_items} bloqueos</div>
          <div class="chips">${lane.capabilities.map(item => `<span class="chip ready">${item}</span>`).join("")}</div>
        </article>
      `).join("");
      actions.innerHTML = (model.priority_actions || []).map(action => `
        <div class="action-item">${action}</div>
      `).join("");
    }

    function renderExecutiveQuestions() {
      const portfolio = data.portfolio;
      const comparisons = data.comparisons || [];
      const highestRisk = [...comparisons].sort((left, right) => right.risk_score - left.risk_score)[0];
      const lowerProgress = [...comparisons].sort((left, right) => left.production_score - right.production_score)[0];
      const environmental = data.environmental[0]?.value ?? 0;
      const quality = data.quality[1]?.value ?? data.quality[0]?.value ?? 0;
      const questions = [
        ["Cuantos proyectos existen", portfolio.total_projects ?? 0, "#portfolioExplorer"],
        ["Cuantos estan activos", portfolio.active_projects ?? 0, "#portfolioExplorer"],
        ["Mayor riesgo", highestRisk ? highestRisk.name : "sin riesgo", "#corporateNotifications"],
        ["Menor avance", lowerProgress ? lowerProgress.name : "sin avance", "#projectComparisons"],
        ["Conflictos ambientales", environmental, "#corporateGisDashboard"],
        ["NCR / calidad", quality, "#panels"]
      ];
      document.querySelector("#executiveQuestions").innerHTML = questions.map(([question, answer, href]) => `
        <article class="question-card">
          <div class="label">${question}</div>
          <div class="answer">${answer}</div>
          <a href="${href}">Ver detalle accionable</a>
        </article>
      `).join("");
    }

    function renderNotifications() {
      document.querySelector("#notifications").innerHTML = recentEvents().map(event => `
        <article class="notification">
          <div class="kind">${event.kind}</div>
          <div class="message">${event.message}</div>
          <div class="time">${event.time}</div>
        </article>
      `).join("");
    }

    function recentEvents() {
      if (auditEvents.length) {
        return auditEvents.map(event => ({
          kind: event.action || event.event_type || "Auditoria",
          message: event.description || event.entity_id || event.actor || "Evento corporativo registrado",
          time: event.created_at || event.timestamp || "audit"
        }));
      }
      const governed = data.portfolio_governance || [];
      const flow = data.operational_flow || [];
      const first = governed[0];
      const events = [
        ["Provisioning", first ? `WEB SIG ${first.websig}` : "Sin WEB SIG registrada"],
        ["GIS", `${data.gis_intelligence?.projects_with_active_layers ?? 0} proyectos con capas activas`],
        ["NAS", `${governed.filter(item => item.nas !== "pendiente").length} espacios NAS vinculados`],
        ["Seguridad", `${(data.users || []).length} usuarios en gobierno corporativo`],
        ["Estado", first ? `${first.project_name} en ${first.governance_status}` : "Sin cambios de estado"],
        ["Alertas", `${data.alerts[0]?.value ?? 0} alertas corporativas`],
        ["Acciones", `${flow.filter(item => item.pending_controls.length > 0).length} acciones pendientes`]
      ];
      return events.map(([kind, message], index) => ({
        kind,
        message,
        time: `T-${index + 1}`
      }));
    }

    function labelPhase(phase) {
      return phase.replaceAll("_", " ");
    }

    function chip(label, value) {
      const ready = value !== "pendiente";
      return `<span class="chip ${ready ? "ready" : ""}">${label}: ${value}</span>`;
    }

    function uniqueCount(values) {
      return new Set(values).size;
    }

    function activeLifecycleCount(items) {
      return items.filter(item => !["closure", "archived"].includes(item.lifecycle_stage)).length;
    }

    async function applyGisFilter(filter) {
      activeGisFilter = filter;
      const companyId = document.querySelector("#companyId").value.trim();
      const params = new URLSearchParams();
      if (filter === "estado") params.set("estado", "warning");
      if (filter === "riesgo") params.set("riesgo", "medium");
      if (filter === "calidad") params.set("calidad", "true");
      if (filter === "ambiental") params.set("ambiental", "true");
      if (filter === "ssoma") params.set("ssoma", "true");
      if (filter === "produccion") params.set("produccion", "true");
      try {
        const response = await fetch(`/api/v1/companies/${encodeURIComponent(companyId)}/gis-intelligence/maps/filter?${params}`);
        if (response.ok) {
          gisMap = await response.json();
          renderMap();
          renderGisIntelligence();
        }
      } catch {
        renderMap();
      }
    }

    function renderPanels() {
      const keys = panelGroups[currentPanel];
      document.querySelector("#panels").innerHTML = keys.map(key => `
        <section class="section">
          <h2>${titles[key]}</h2>
          <div class="metric-grid">
            ${(data[key] || []).map(metric => `
              <article class="metric ${metric.status}">
                <div class="label">${metric.label}</div>
                <div class="value">${metric.value}</div>
                <div class="muted">${metric.trend}</div>
              </article>
            `).join("")}
          </div>
        </section>
      `).join("");
    }

    function renderComparisons() {
      document.querySelector("#comparisons").innerHTML = data.comparisons.map(project => `
        <tr>
          <td>${project.name}</td>
          <td>${project.governance_status}</td>
          <td>${project.kpi_score}</td>
          <td>${project.production_score}</td>
          <td>${project.risk_score}</td>
        </tr>
      `).join("");
    }

    document.querySelector("#load").addEventListener("click", loadDashboard);
    document.querySelector("#theme").addEventListener("click", () => {
      const root = document.documentElement;
      const next = root.dataset.theme === "dark" ? "light" : "dark";
      root.dataset.theme = next;
      document.querySelector("#theme").textContent = next === "dark" ? "Light Mode" : "Dark Mode";
      if (data) renderMap();
    });
    document.querySelectorAll("[data-panel]").forEach(button => {
      button.addEventListener("click", () => {
        currentPanel = button.dataset.panel;
        document.querySelectorAll("[data-panel]").forEach(item => item.classList.remove("active"));
        button.classList.add("active");
        if (data) renderPanels();
      });
    });
    document.querySelectorAll("[data-portfolio-filter]").forEach(button => {
      button.addEventListener("click", () => {
        activePortfolioFilter = button.dataset.portfolioFilter;
        if (data) renderPortfolioGovernance();
      });
    });
    document.querySelectorAll("[data-gis-filter]").forEach(button => {
      button.addEventListener("click", () => {
        applyGisFilter(button.dataset.gisFilter);
      });
    });
    loadDashboard();
  </script>
</body>
</html>"""
