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
    .gis-workbench {
      display: grid;
      grid-template-columns: 1fr;
      gap: 16px;
      align-items: stretch;
      min-width: 0;
    }
    .gis-map-grid {
      display: grid;
      grid-template-columns: minmax(240px, 320px) minmax(300px, 1fr);
      gap: 14px;
      align-items: start;
      min-width: 0;
    }
    .gis-toolbar {
      display: grid;
      grid-template-columns: minmax(260px, 1fr) minmax(280px, 1fr);
      gap: 12px;
      margin-bottom: 14px;
    }
    .gis-bridge, .gis-layer-stack {
      background: var(--panel-strong);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
    }
    .gis-bridge h3, .gis-layer-stack h3 {
      font-size: 13px;
      margin: 0 0 10px;
    }
    .bridge-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; }
    .bridge-card {
      min-height: 74px;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 9px;
      background: var(--panel);
      color: var(--text);
      width: 100%;
      text-align: left;
      cursor: pointer;
      margin: 0;
    }
    .bridge-card.active { border-color: var(--accent); background: var(--accent-soft); }
    .bridge-card .label { color: var(--muted); font-size: 11px; }
    .bridge-card .value { font-size: 18px; font-weight: 780; margin-top: 5px; }
    .bridge-card .target { color: var(--accent); font-size: 11px; margin-top: 4px; }
    .layer-list { display: grid; gap: 7px; }
    .layer-row {
      display: grid;
      grid-template-columns: 10px minmax(0, 1fr) auto;
      gap: 8px;
      align-items: center;
      color: var(--muted);
      font-size: 12px;
    }
    .layer-dot { width: 10px; height: 10px; border-radius: 50%; background: var(--accent); box-shadow: 0 0 10px var(--accent); }
    .kpi-chart-grid { display: grid; grid-template-columns: repeat(3, minmax(160px, 1fr)); gap: 10px; }
    .kpi-chart {
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      background: var(--panel-strong);
    }
    .kpi-chart .chart-top { display: flex; justify-content: space-between; gap: 12px; align-items: baseline; }
    .kpi-chart .name { color: var(--muted); font-size: 12px; }
    .kpi-chart .value { font-weight: 780; }
    .bar-track {
      height: 10px;
      border-radius: 999px;
      background: rgba(255,255,255,.08);
      overflow: hidden;
      margin-top: 10px;
    }
    .bar-fill {
      height: 100%;
      width: var(--value);
      border-radius: inherit;
      background: linear-gradient(90deg, var(--accent), var(--warn));
    }
    .map-caption {
      color: var(--muted);
      font-size: 12px;
      margin-top: 10px;
      text-align: center;
    }
    .gis-map-surface {
      min-height: 360px;
      position: relative;
      overflow: hidden;
      border: 1px solid var(--line);
      border-radius: 8px;
      background:
        linear-gradient(90deg, rgba(65, 209, 154, .09) 1px, transparent 1px),
        linear-gradient(0deg, rgba(65, 209, 154, .09) 1px, transparent 1px),
        radial-gradient(circle at 28% 34%, rgba(65, 209, 154, .16), transparent 20%),
        radial-gradient(circle at 70% 66%, rgba(214, 169, 74, .12), transparent 22%),
        var(--radar);
      background-size: 42px 42px, 42px 42px, auto, auto, auto;
      box-shadow: inset 0 0 70px rgba(65, 209, 154, .09);
    }
    .gis-map-grid .radar {
      width: min(100%, 320px);
      min-height: 0;
    }
    .peru-admin-map {
      display: grid;
      grid-template-columns: minmax(300px, .8fr) minmax(320px, 1fr);
      gap: 14px;
      margin-top: 16px;
      min-width: 0;
    }
    .peru-map-surface {
      min-height: 430px;
      position: relative;
      overflow: hidden;
      border: 1px solid var(--line);
      border-radius: 8px;
      background:
        linear-gradient(90deg, rgba(65, 209, 154, .07) 1px, transparent 1px),
        linear-gradient(0deg, rgba(65, 209, 154, .07) 1px, transparent 1px),
        radial-gradient(circle at 48% 52%, rgba(65, 209, 154, .13), transparent 28%),
        var(--radar);
      background-size: 44px 44px, 44px 44px, auto, auto;
    }
    .peru-outline {
      position: absolute;
      inset: 28px 34px 34px 34px;
      width: calc(100% - 68px);
      height: calc(100% - 62px);
      opacity: .88;
    }
    .peru-outline path {
      fill: rgba(65, 209, 154, .13);
      stroke: rgba(65, 209, 154, .58);
      stroke-width: 2;
    }
    .peru-marker {
      position: absolute;
      transform: translate(-50%, -50%);
      border: 0;
      background: transparent;
      padding: 0;
      margin: 0;
      color: var(--text);
      cursor: pointer;
    }
    .peru-marker .pin {
      display: block;
      width: 13px;
      height: 13px;
      border-radius: 50%;
      background: #fff;
      border: 2px solid var(--accent);
      box-shadow: 0 0 18px var(--accent);
    }
    .peru-marker.selected .pin {
      background: var(--warn);
      border-color: #fff;
      box-shadow: 0 0 22px var(--warn);
    }
    .peru-marker span {
      display: inline-block;
      margin-top: 5px;
      background: rgba(3, 8, 10, .84);
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 4px 6px;
      font-size: 11px;
      white-space: nowrap;
      pointer-events: none;
    }
    .peru-admin-panel {
      display: grid;
      gap: 10px;
      min-width: 0;
    }
    .admin-region-list {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px;
    }
    .admin-chip {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel-strong);
      color: var(--text);
      padding: 10px;
      text-align: left;
      cursor: pointer;
      margin: 0;
    }
    .admin-chip.active {
      border-color: var(--accent);
      background: var(--accent-soft);
    }
    .admin-chip .label { color: var(--muted); font-size: 11px; }
    .admin-chip .value { font-weight: 780; margin-top: 4px; }
    .admin-detail {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel-strong);
      padding: 14px;
    }
    .admin-detail .name { font-size: 18px; font-weight: 780; margin-bottom: 10px; }
    .admin-detail .row {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      border-top: 1px solid var(--line);
      padding: 9px 0;
      color: var(--muted);
    }
    .admin-detail strong { color: var(--text); text-align: right; }
    .gis-map-surface::after {
      content: "MAPA GIS CORPORATIVO";
      position: absolute;
      left: 16px;
      bottom: 14px;
      color: var(--muted);
      font-size: 11px;
      letter-spacing: 2px;
    }
    .geometry-shape {
      position: absolute;
      border: 2px solid rgba(65, 209, 154, .62);
      background: rgba(65, 209, 154, .12);
      transform: translate(-50%, -50%) rotate(var(--angle));
      box-shadow: 0 0 24px rgba(65, 209, 154, .14);
    }
    .geometry-shape.line {
      height: 9px;
      border-radius: 999px;
      background: rgba(214, 169, 74, .72);
      border-color: rgba(214, 169, 74, .9);
    }
    .geometry-shape.polygon {
      clip-path: polygon(10% 20%, 72% 8%, 96% 54%, 58% 92%, 14% 70%);
    }
    .geometry-shape.selected {
      border-color: #fff;
      background: rgba(65, 209, 154, .24);
      box-shadow: 0 0 32px var(--accent);
      z-index: 4;
    }
    .map-marker {
      position: absolute;
      transform: translate(-50%, -50%);
      z-index: 5;
      display: grid;
      gap: 4px;
      justify-items: center;
      width: auto;
      padding: 0;
      margin: 0;
      background: transparent;
      border: 0;
    }
    .map-marker .pin {
      width: 13px;
      height: 13px;
      border-radius: 50%;
      background: var(--accent);
      border: 2px solid var(--panel);
      box-shadow: 0 0 18px var(--accent);
    }
    .map-marker.selected .pin { background: #fff; box-shadow: 0 0 24px #fff; }
    .map-marker span {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 4px 6px;
      color: var(--text);
      font-size: 11px;
      white-space: nowrap;
    }
    .service-slots {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 8px;
      margin-top: 10px;
    }
    .service-slot {
      border: 1px dashed var(--line);
      border-radius: 8px;
      padding: 9px;
      color: var(--muted);
      font-size: 11px;
      text-align: center;
      background: var(--panel-strong);
    }
    .service-slot.ready { color: var(--accent); border-color: var(--accent); }
    .project-detail {
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      background: var(--panel-strong);
      margin-top: 10px;
    }
    .project-detail .name { font-weight: 780; margin-bottom: 8px; }
    .project-detail .row {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      color: var(--muted);
      font-size: 12px;
      border-top: 1px solid var(--line);
      padding-top: 7px;
      margin-top: 7px;
    }
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
      padding: 0;
      margin: 0;
      transform: translate(-50%, -50%);
      box-shadow: 0 0 18px var(--accent);
      z-index: 2;
    }
    .point.selected { background: #fff; box-shadow: 0 0 26px #fff; }
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
      pointer-events: none;
    }
    .radar-side {
      display: grid;
      align-content: start;
      gap: 10px;
      min-width: 0;
    }
    #radarReadouts {
      display: grid;
      grid-template-columns: repeat(6, minmax(120px, 1fr));
      gap: 10px;
      min-width: 0;
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
      white-space: nowrap;
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
      min-width: 0;
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
      .gis-workbench, .gis-toolbar, .gis-map-grid, .peru-admin-map { grid-template-columns: 1fr; }
      #radarReadouts { grid-template-columns: repeat(3, minmax(120px, 1fr)); }
      .kpi-chart-grid { grid-template-columns: repeat(2, minmax(160px, 1fr)); }
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
      .bridge-grid { grid-template-columns: 1fr; }
      .service-slots { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .notification { grid-template-columns: 1fr; }
      #radarReadouts, .kpi-chart-grid { grid-template-columns: 1fr; }
      .admin-region-list { grid-template-columns: 1fr; }
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
            <div class="gis-toolbar">
              <div class="gis-bridge">
                <h3>Comunicacion KPI -> Mapa</h3>
              <div
                class="bridge-grid"
                id="gisKpiBridge"
                data-kpi-filter-options="produccion,riesgo,ambiental,ssoma,calidad,estado"
              ></div>
              </div>
              <div class="gis-layer-stack">
                <h3>Capas corporativas publicadas</h3>
                <div class="layer-list" id="gisLayerLegend"></div>
              </div>
            </div>
            <div class="map-mode-grid" id="gisMapModes"></div>
            <div class="filter-row" id="gisFilters">
              <button data-gis-filter="estado">Estado</button>
              <button data-gis-filter="riesgo">Riesgo</button>
              <button data-gis-filter="calidad">Calidad</button>
              <button data-gis-filter="ambiental">Ambiental</button>
              <button data-gis-filter="ssoma">SSOMA</button>
              <button data-gis-filter="produccion">Produccion</button>
            </div>
            <div class="gis-workbench">
              <div class="gis-map-grid">
                <div>
                  <div class="radar" id="projectRadar"></div>
                  <div class="map-caption">Radar de proyectos: selecciona senales ejecutivas y comunica el foco al mapa GIS.</div>
                </div>
                <div>
                  <div class="gis-map-surface" id="gisMapSurface"></div>
                  <div class="map-caption">Visor SIG Corporativo / Mapa GIS: recibe geometria publicada desde WEB SIG Enterprise.</div>
                  <div class="service-slots" id="gisServiceSlots"></div>
                  <div class="project-detail" id="gisProjectDetail"></div>
                </div>
              </div>
              <div class="radar-side">
                <div id="radarReadouts"></div>
                <div class="kpi-chart-grid" id="gisKpiCharts"></div>
              </div>
            </div>
            <section class="peru-admin-map" aria-label="Mapa Administrativo Peru">
              <div>
                <h3>Mapa Administrativo Peru</h3>
                <div class="section-kicker">Region / provincia / distrito de proyectos gobernados.</div>
                <div class="peru-map-surface" id="peruAdministrativeMap"></div>
              </div>
              <div class="peru-admin-panel">
                <div>
                  <h3>Ubicacion corporativa</h3>
                  <div class="section-kicker">Selecciona region o proyecto para sincronizar con radar y mapa GIS.</div>
                </div>
                <div class="admin-region-list" id="peruRegionList"></div>
                <div class="admin-detail" id="peruAdminDetail"></div>
              </div>
            </section>
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
    let activePeruRegion = "all";
    let selectedProjectId = null;

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
      const map = document.querySelector("#projectRadar");
      const readouts = document.querySelector("#radarReadouts");
      const modes = ["Mapa Nacional", "Mapa Regional", "Empresa", "Programa", "Proyecto"];
      renderGisKpiBridge();
      renderGisLayerLegend();
      renderGisKpiCharts();
      renderGisServiceSlots();
      document.querySelector("#gisMapModes").innerHTML = modes.map((mode, index) => `
        <div class="mode-pill ${index === 0 ? "active" : ""}">${mode}</div>
      `).join("");
      document.querySelectorAll("[data-gis-filter]").forEach(button => {
        button.classList.toggle("active", button.dataset.gisFilter === activeGisFilter);
      });
      if (!data.map_points.length) {
        map.innerHTML = `<div class="muted" style="padding:16px">Sin proyectos georreferenciados.</div>`;
        readouts.innerHTML = "";
        renderGisMapSurface();
        renderGisProjectDetail();
        renderPeruAdministrativeMap();
        return;
      }
      map.innerHTML = data.map_points.map((point, index) => {
        const projectId = projectKey(point, index);
        selectedProjectId = selectedProjectId || projectId;
        const angle = (index * 58 + 230) * Math.PI / 180;
        const radius = 24 + (index * 13) % 30;
        const left = 50 + Math.cos(angle) * radius;
        const top = 50 + Math.sin(angle) * radius;
        const selected = selectedProjectId === projectId ? " selected" : "";
        return `<button class="point${selected}" data-project-id="${projectId}" style="left:${left}%;top:${top}%" title="Seleccionar ${point.name}"><span>${point.name}</span></button>`;
      }).join("");
      document.querySelectorAll("[data-project-id]").forEach(point => {
        point.addEventListener("click", () => {
          selectedProjectId = point.dataset.projectId;
          renderMap();
        });
      });
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
      renderGisMapSurface();
      renderGisProjectDetail();
      renderPeruAdministrativeMap();
    }

    function renderGisMapSurface() {
      const surface = document.querySelector("#gisMapSurface");
      const points = data.map_points || [];
      if (!points.length) {
        surface.innerHTML = `<div class="muted" style="padding:16px">Sin geometria corporativa publicada.</div>`;
        return;
      }
      surface.innerHTML = points.map((point, index) => {
        const projectId = projectKey(point, index);
        const position = mapPosition(index);
        const selected = selectedProjectId === projectId ? " selected" : "";
        const shape = index % 2 === 0 ? "polygon" : "line";
        const width = 92 + ((index * 17) % 58);
        const height = shape === "line" ? 9 : 62 + ((index * 19) % 42);
        return `
          <div class="geometry-shape ${shape}${selected}" style="left:${position.left}%;top:${position.top}%;width:${width}px;height:${height}px;--angle:${position.angle}deg"></div>
          <button class="map-marker${selected}" data-project-id="${projectId}" style="left:${position.left}%;top:${position.top}%">
            <span class="pin"></span>
            <span>${point.name}</span>
          </button>
        `;
      }).join("");
      document.querySelectorAll("#gisMapSurface [data-project-id]").forEach(marker => {
        marker.addEventListener("click", () => {
          selectedProjectId = marker.dataset.projectId;
          renderMap();
        });
      });
    }

    function renderGisServiceSlots() {
      const layers = gisMap?.layers || [];
      const services = [
        ["WMS", layers.some(layer => String(layer.service_kind || "").toLowerCase() === "wms")],
        ["WFS", layers.some(layer => String(layer.service_kind || "").toLowerCase() === "wfs")],
        ["WMTS", layers.some(layer => String(layer.service_kind || "").toLowerCase() === "wmts")],
        ["Vector Tiles", layers.some(layer => String(layer.service_kind || "").toLowerCase().includes("tile"))]
      ];
      document.querySelector("#gisServiceSlots").innerHTML = services.map(([label, ready]) => `
        <div class="service-slot ${ready ? "ready" : ""}">${label}<br>${ready ? "publicado" : "slot preparado"}</div>
      `).join("");
    }

    function renderGisProjectDetail() {
      const detail = document.querySelector("#gisProjectDetail");
      const selected = selectedProject();
      if (!selected) {
        detail.innerHTML = `<div class="muted">Selecciona un contacto del radar para ver su detalle GIS.</div>`;
        return;
      }
      const governance = (data.portfolio_governance || []).find(item => item.project_id === selected.project_id || item.project_name === selected.name) || {};
      const flow = (data.operational_flow || []).find(item => item.project_id === governance.project_id) || {};
      detail.innerHTML = `
        <div class="name">${selected.name}</div>
        <div class="row"><span>Geometria</span><strong>publicada por WEB SIG</strong></div>
        <div class="row"><span>Estado</span><strong>${governance.governance_status || "observed"}</strong></div>
        <div class="row"><span>Layer activo</span><strong>${activeGisFilter}</strong></div>
        <div class="row"><span>Readiness</span><strong>${flow.readiness_score ?? "pendiente"}%</strong></div>
      `;
    }

    function renderPeruAdministrativeMap() {
      const surface = document.querySelector("#peruAdministrativeMap");
      const regionList = document.querySelector("#peruRegionList");
      const detail = document.querySelector("#peruAdminDetail");
      const points = data.map_points || [];
      if (!points.length) {
        surface.innerHTML = `<div class="muted" style="padding:16px">Sin ubicaciones administrativas registradas.</div>`;
        regionList.innerHTML = "";
        detail.innerHTML = `<div class="muted">La ubicacion se completa desde el Wizard o desde capas corporativas publicadas.</div>`;
        return;
      }
      const locations = points.map((point, index) => ({
        point,
        index,
        projectId: projectKey(point, index),
        admin: administrativeLocation(point, index),
        position: peruMapPosition(point)
      }));
      const visible = activePeruRegion === "all"
        ? locations
        : locations.filter(item => item.admin.region === activePeruRegion);
      surface.innerHTML = `
        <svg class="peru-outline" viewBox="0 0 220 360" role="img" aria-label="Silueta referencial de Peru">
          <path d="M112 8 L139 34 L129 65 L154 92 L145 128 L166 162 L154 204 L176 238 L145 278 L128 340 L96 352 L77 318 L62 286 L74 242 L48 206 L60 166 L42 126 L59 91 L78 58 L84 24 Z"></path>
        </svg>
        ${visible.map(item => `
          <button
            class="peru-marker ${item.projectId === selectedProjectId ? "selected" : ""}"
            data-project-id="${item.projectId}"
            style="left:${item.position.left}%; top:${item.position.top}%"
            title="${item.point.name} / ${item.admin.region}"
          >
            <span class="pin"></span>
            <span>${item.point.name}</span>
          </button>
        `).join("")}
      `;
      const regions = regionCounts(locations);
      regionList.innerHTML = [
        ["all", "Todo Peru", locations.length],
        ...regions.map(item => [item.region, item.region, item.count])
      ].map(([key, label, count]) => `
        <button class="admin-chip ${activePeruRegion === key ? "active" : ""}" data-peru-region="${key}">
          <div class="label">Region</div>
          <div class="value">${label}</div>
          <div class="label">${count} proyecto${count === 1 ? "" : "s"}</div>
        </button>
      `).join("");
      document.querySelectorAll("[data-peru-region]").forEach(chip => {
        chip.addEventListener("click", () => {
          activePeruRegion = chip.dataset.peruRegion;
          renderPeruAdministrativeMap();
        });
      });
      document.querySelectorAll("#peruAdministrativeMap [data-project-id]").forEach(marker => {
        marker.addEventListener("click", () => {
          selectedProjectId = marker.dataset.projectId;
          renderMap();
        });
      });
      const selected = selectedProject();
      const selectedIndex = Math.max(0, points.findIndex((point, index) => projectKey(point, index) === selectedProjectId));
      const admin = administrativeLocation(selected, selectedIndex);
      detail.innerHTML = `
        <div class="name">${selected.name}</div>
        <div class="row"><span>Pais</span><strong>Peru</strong></div>
        <div class="row"><span>Region</span><strong>${admin.region}</strong></div>
        <div class="row"><span>Provincia</span><strong>${admin.province}</strong></div>
        <div class="row"><span>Distrito</span><strong>${admin.district}</strong></div>
        <div class="row"><span>Fuente</span><strong>${admin.source}</strong></div>
      `;
    }

    function selectedProject() {
      const points = data.map_points || [];
      return points.find((point, index) => projectKey(point, index) === selectedProjectId) || points[0];
    }

    function projectKey(point, index) {
      return point.project_id || point.id || point.name || `project-${index}`;
    }

    function mapPosition(index) {
      return {
        left: 22 + ((index * 29) % 56),
        top: 24 + ((index * 37) % 52),
        angle: -18 + ((index * 23) % 42)
      };
    }

    function administrativeLocation(point, index) {
      if (point.region || point.province || point.district) {
        return {
          region: point.region || "Region por registrar",
          province: point.province || "Provincia por registrar",
          district: point.district || "Distrito por registrar",
          source: "dato corporativo"
        };
      }
      const inferred = inferPeruAdminFromCoordinates(point.latitude, point.longitude, index);
      return { ...inferred, source: "estimado desde coordenadas corporativas" };
    }

    function inferPeruAdminFromCoordinates(latitude, longitude, index) {
      if (latitude <= -16 && longitude <= -70) {
        return { region: "Arequipa", province: "Arequipa", district: "Distrito por registrar" };
      }
      if (latitude <= -13.5 && longitude <= -75) {
        return { region: "Ica", province: "Ica", district: "Distrito por registrar" };
      }
      if (latitude <= -12.8 && longitude > -74.5) {
        return { region: "Cusco", province: "Cusco", district: "Distrito por registrar" };
      }
      if (latitude >= -10.2 && longitude <= -76.5) {
        return { region: "Ancash", province: "Huaraz", district: "Distrito por registrar" };
      }
      if (latitude >= -8 && longitude <= -78) {
        return { region: "Cajamarca", province: "Cajamarca", district: "Distrito por registrar" };
      }
      return {
        region: index % 2 === 0 ? "Lima" : "Lima Provincias",
        province: index % 2 === 0 ? "Lima" : "Huaral",
        district: "Distrito por registrar"
      };
    }

    function peruMapPosition(point) {
      const latitude = Number(point.latitude ?? -12.0464);
      const longitude = Number(point.longitude ?? -77.0428);
      const left = ((longitude + 82) / 13) * 100;
      const top = ((latitude + 1) / -18) * 100;
      return {
        left: Math.max(18, Math.min(82, left)),
        top: Math.max(8, Math.min(92, top))
      };
    }

    function regionCounts(locations) {
      const counts = new Map();
      locations.forEach(item => {
        counts.set(item.admin.region, (counts.get(item.admin.region) || 0) + 1);
      });
      return [...counts.entries()]
        .map(([region, count]) => ({ region, count }))
        .sort((left, right) => left.region.localeCompare(right.region));
    }

    function renderGisKpiBridge() {
      const bridge = [
        ["Produccion", data.production[0]?.value ?? "0%", "Capa avance", "produccion"],
        ["Riesgo", data.risks[0]?.value ?? "0", "Capa riesgos", "riesgo"],
        ["Ambiental", data.environmental[0]?.value ?? "0", "Capa ambiental", "ambiental"],
        ["SSOMA", data.ssoma[0]?.value ?? "0", "Capa SSOMA", "ssoma"],
        ["Calidad", data.quality[0]?.value ?? "0%", "Capa calidad", "calidad"],
        ["Cronograma", data.schedule[0]?.value ?? "0", "Capa cronograma", "estado"]
      ];
      document.querySelector("#gisKpiBridge").innerHTML = bridge.map(([label, value, target, filter]) => `
        <button class="bridge-card ${activeGisFilter === filter ? "active" : ""}" data-kpi-filter="${filter}">
          <div class="label">${label}</div>
          <div class="value">${value}</div>
          <div class="target">${target}</div>
        </button>
      `).join("");
      document.querySelectorAll("[data-kpi-filter]").forEach(card => {
        card.addEventListener("click", () => applyGisFilter(card.dataset.kpiFilter));
      });
    }

    function renderGisLayerLegend() {
      const layers = gisMap?.layers?.length
        ? gisMap.layers.slice(0, 8).map(layer => [
            layer.name,
            layer.layer_type || layer.discipline || "corporate"
          ])
        : [
            ["Avance fisico", "avance"],
            ["Riesgos espaciales", "riesgo"],
            ["Calidad QA/QC", "calidad"],
            ["Ambiental", "ambiental"],
            ["SSOMA", "ssoma"],
            ["Produccion", "produccion"],
            ["Predios", "predios"],
            ["Interferencias", "interferencias"]
          ];
      document.querySelector("#gisLayerLegend").innerHTML = layers.map(([name, type]) => `
        <div class="layer-row">
          <span class="layer-dot"></span>
          <span>${name}</span>
          <span>${type}</span>
        </div>
      `).join("");
    }

    function renderGisKpiCharts() {
      const charts = [
        ["Produccion", data.production[0]?.value ?? "0%", "avance"],
        ["Salud portafolio", data.kpis[0]?.value ?? "0%", "portfolio"],
        ["Cobertura WEB SIG", data.kpis[2]?.value ?? "0%", "websig"],
        ["Avance espacial", `${data.gis_intelligence?.aggregated_spatial_progress ?? 0}%`, "gis"],
        ["Calidad", data.quality[0]?.value ?? "0%", "quality"]
      ];
      document.querySelector("#gisKpiCharts").innerHTML = charts.map(([name, value, layer]) => {
        const percent = normalizePercent(value);
        return `
          <article class="kpi-chart">
            <div class="chart-top">
              <div class="name">${name}</div>
              <div class="value">${value}</div>
            </div>
            <div class="bar-track"><div class="bar-fill" style="--value:${percent}%"></div></div>
            <div class="muted">Comunica con ${layer}</div>
          </article>
        `;
      }).join("");
    }

    function normalizePercent(value) {
      const parsed = Number(String(value).replace("%", ""));
      if (Number.isNaN(parsed)) return 0;
      return Math.max(0, Math.min(100, parsed));
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
          kind: auditKind(event.action || event.event_type),
          message: auditMessage(event),
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

    function auditKind(action) {
      const value = String(action || "Auditoria").toLowerCase();
      if (value.includes("wizard")) return "Wizard";
      if (value.includes("workflow")) return "Workflow";
      if (value.includes("lifecycle")) return "Lifecycle";
      if (value.includes("provision")) return "Provisioning";
      if (value.includes("gis")) return "GIS";
      if (value.includes("nas")) return "NAS";
      if (value.includes("security") || value.includes("user")) return "Security";
      return "Audit";
    }

    function auditMessage(event) {
      const action = event.action || event.event_type || "Evento corporativo";
      const entity = event.entity_id || event.description || event.actor || "sin entidad";
      return `${readableAction(action)} / ${entity}`;
    }

    function readableAction(action) {
      return String(action)
        .replaceAll("_", " ")
        .replaceAll(".", " ")
        .toLowerCase()
        .replace(/\\b\\w/g, letter => letter.toUpperCase());
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
