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
    .chips { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }
    .chip {
      border: 1px solid var(--line);
      border-radius: 999px;
      color: var(--muted);
      font-size: 11px;
      padding: 4px 7px;
    }
    .chip.ready { color: var(--accent); border-color: var(--accent); }
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
      table { font-size: 12px; }
      th:nth-child(4), td:nth-child(4), th:nth-child(5), td:nth-child(5) { display: none; }
      .radar { min-height: 300px; }
      .radar::after { display: none; }
      .flow-card { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="shell">
    <aside>
      <div class="brand">BIMSIG Enterprise</div>
      <h1>Dashboard Ejecutivo Corporativo</h1>
      <label for="companyId">Empresa</label>
      <input id="companyId" value="CRTG" autocomplete="off">
      <button class="primary" id="load">Actualizar</button>
      <button id="theme">Light Mode</button>
      <p class="muted">Vista integrada a Corporate Control Tower REV12.</p>
    </aside>
    <main>
      <div class="topbar">
        <div class="title">
          <div class="brand">Corporate Control Tower</div>
          <h1 id="heading">Resumen ejecutivo</h1>
        </div>
        <div class="toolbar">
          <button data-panel="operations" class="active">Operacion</button>
          <button data-panel="governance">Gobierno</button>
          <button data-panel="enterprise">Empresa</button>
        </div>
      </div>
      <section class="cockpit" id="cockpit"></section>
      <section class="grid summary" id="summary"></section>
      <section class="grid content">
        <div class="stack">
          <section class="section">
            <h2>Radar Corporativo</h2>
            <div class="radar-shell">
              <div class="radar" id="map"></div>
              <div class="radar-side" id="radarReadouts"></div>
            </div>
          </section>
          <section class="section">
            <h2>Gobierno de Portafolio</h2>
            <div class="governance-grid" id="portfolioGovernance"></div>
          </section>
          <section class="section">
            <h2>Flujo Operacional</h2>
            <div class="flow-grid" id="operationalFlow"></div>
          </section>
          <section class="section">
            <h2>GIS Intelligence Corporativo</h2>
            <div class="metric-grid" id="gisIntelligence"></div>
          </section>
          <section class="section">
            <h2>Comparativos entre proyectos</h2>
            <table>
              <thead>
                <tr><th>Proyecto</th><th>Estado</th><th>KPI</th><th>Produccion</th><th>Riesgo</th></tr>
              </thead>
              <tbody id="comparisons"></tbody>
            </table>
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

    async function loadDashboard() {
      const companyId = document.querySelector("#companyId").value.trim();
      const response = await fetch(`/api/v1/companies/${encodeURIComponent(companyId)}/dashboard/executive`);
      if (!response.ok) {
        document.querySelector("#heading").textContent = "Empresa no encontrada";
        return;
      }
      data = await response.json();
      render();
    }

    function render() {
      document.querySelector("#heading").textContent = `Resumen ejecutivo ${data.company_id}`;
      renderSummary();
      renderCockpit();
      renderMap();
      renderPortfolioGovernance();
      renderOperationalFlow();
      renderGisIntelligence();
      renderPanels();
      renderComparisons();
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
      const cards = [
        ["Portafolio", portfolio.total_projects ?? 0],
        ["Clientes", uniqueCount(governed.map(item => item.customer).filter(Boolean))],
        ["Programas", uniqueCount(governed.map(item => item.program).filter(Boolean))],
        ["NAS", governed.filter(item => item.nas !== "pendiente").length]
      ];
      document.querySelector("#summary").innerHTML = cards.map(([label, value]) =>
        `<article class="metric"><div class="label">${label}</div><div class="value">${value}</div></article>`
      ).join("");
    }

    function renderMap() {
      const map = document.querySelector("#map");
      const readouts = document.querySelector("#radarReadouts");
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
        ["MODO", document.documentElement.dataset.theme.toUpperCase()]
      ].map(([label, value]) => `
        <article class="readout"><div class="label">${label}</div><div class="value">${value}</div></article>
      `).join("");
    }

    function renderPortfolioGovernance() {
      const target = document.querySelector("#portfolioGovernance");
      const items = data.portfolio_governance || [];
      if (!items.length) {
        target.innerHTML = `<div class="muted">Sin proyectos gobernados.</div>`;
        return;
      }
      target.innerHTML = items.map(item => `
        <article class="governance-card">
          <div class="project">${item.project_name}</div>
          <div class="meta">Cliente: ${item.customer || "pendiente"}</div>
          <div class="meta">Programa: ${item.program || "pendiente"}</div>
          <div class="meta">Lifecycle: ${item.lifecycle_stage}</div>
          <div class="chips">
            ${chip("WEB SIG", item.websig)}
            ${chip("NAS", item.nas)}
            ${chip("GIS", item.gis)}
          </div>
        </article>
      `).join("");
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
      target.innerHTML = cards.map(([label, value]) => `
        <article class="metric">
          <div class="label">${label}</div>
          <div class="value">${value}</div>
        </article>
      `).join("");
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
    loadDashboard();
  </script>
</body>
</html>"""
