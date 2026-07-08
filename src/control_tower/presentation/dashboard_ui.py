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
    }
    @media (max-width: 700px) {
      main { padding: 14px; }
      .summary, .metric-grid, .cockpit { grid-template-columns: 1fr; }
      .topbar { align-items: stretch; flex-direction: column; }
      .toolbar { justify-content: space-between; }
      .toolbar button { flex: 1; min-width: 0; }
      table { font-size: 12px; }
      th:nth-child(4), td:nth-child(4), th:nth-child(5), td:nth-child(5) { display: none; }
      .radar { min-height: 300px; }
      .radar::after { display: none; }
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
      renderPanels();
      renderComparisons();
    }

    function renderCockpit() {
      const portfolio = data.portfolio;
      const instruments = [
        ["ALT", `${portfolio.total_projects ?? 0}`, "Portafolio"],
        ["NAV", `${portfolio.active ?? 0}`, "Proyectos activos"],
        ["COM", `${data.users[0]?.value ?? "0"}`, "Usuarios"],
        ["SYS", `${data.alerts[0]?.value ?? "0"}`, "Alertas"]
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
      const cards = [
        ["Portafolio", portfolio.total_projects ?? 0],
        ["Activos", portfolio.active ?? 0],
        ["Alertas", data.alerts[0]?.value ?? "0"],
        ["Licencias", data.licenses[0]?.value ?? "0"]
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
