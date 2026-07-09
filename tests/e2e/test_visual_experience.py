from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

playwright = pytest.importorskip("playwright.sync_api")
from playwright.sync_api import Error as PlaywrightError  # noqa: E402
from playwright.sync_api import Page, sync_playwright  # noqa: E402


VIEWPORTS = {
    "desktop": {"width": 1440, "height": 1000},
    "laptop": {"width": 1366, "height": 768},
    "tablet": {"width": 1024, "height": 768},
}


@pytest.fixture(scope="session")
def e2e_server(tmp_path_factory: pytest.TempPathFactory) -> str:
    tmp_path = tmp_path_factory.mktemp("control_tower_e2e")
    database_url = f"sqlite:///{tmp_path / 'control_tower_e2e.db'}"
    env = os.environ.copy()
    env["CONTROL_TOWER_DATABASE_URL"] = database_url
    env["CONTROL_TOWER_REPORT_OUTPUT_DIR"] = str(tmp_path / "reports")
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "control_tower.api.app:create_app",
            "--factory",
            "--host",
            "127.0.0.1",
            "--port",
            "8010",
        ],
        cwd=Path(__file__).resolve().parents[2],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    base_url = "http://127.0.0.1:8010"
    try:
        _wait_for_health(base_url)
        _seed_company(base_url)
        yield base_url
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()


@pytest.fixture()
def dashboard_page(e2e_server: str) -> Page:
    with sync_playwright() as browser_context:
        try:
            browser = browser_context.chromium.launch()
        except PlaywrightError as exc:
            pytest.skip(f"Playwright Chromium is not installed: {exc}")
        page = browser.new_page()
        page.goto(f"{e2e_server}/dashboard", wait_until="networkidle")
        page.locator("#summary .metric").first.wait_for(timeout=10_000)
        yield page
        browser.close()


def test_visual_dashboard_flows_across_viewports(dashboard_page: Page) -> None:
    artifact_root = Path("e2e-artifacts")
    artifact_root.mkdir(exist_ok=True)
    flows = [
        ("dashboard", "#corporateHome"),
        ("portfolio", "#portfolioExplorer"),
        ("gis", "#corporateGisDashboard"),
        ("wizard", "#enterpriseWizard"),
        ("reporting", "#corporateReporting"),
    ]

    for viewport_name, viewport in VIEWPORTS.items():
        dashboard_page.set_viewport_size(viewport)
        for flow_name, target in flows:
            dashboard_page.locator(f'a[href="{target}"]').click()
            dashboard_page.locator(target).scroll_into_view_if_needed()
            dashboard_page.locator(target).wait_for(timeout=5_000)
            if flow_name == "gis":
                dashboard_page.locator('[data-gis-filter="riesgo"]').click()
                dashboard_page.locator("#gisMapSurface").wait_for(timeout=5_000)
            _assert_no_critical_overlap(dashboard_page)
            dashboard_page.screenshot(path=str(artifact_root / f"{viewport_name}-{flow_name}.png"))


def test_visual_dark_light_mode(dashboard_page: Page) -> None:
    dashboard_page.set_viewport_size(VIEWPORTS["laptop"])

    assert dashboard_page.locator("html").get_attribute("data-theme") == "dark"
    dashboard_page.locator("#theme").click()
    assert dashboard_page.locator("html").get_attribute("data-theme") == "light"
    _assert_no_critical_overlap(dashboard_page)
    dashboard_page.screenshot(path="e2e-artifacts/laptop-light-mode.png")


def test_visual_reporting_preview_is_rendered(dashboard_page: Page) -> None:
    dashboard_page.locator('a[href="#corporateReporting"]').click()
    dashboard_page.locator("#corporateReporting").scroll_into_view_if_needed()

    assert dashboard_page.locator("#reportingPreview .metric").count() >= 2
    assert dashboard_page.locator("#reportingPreview").inner_text()


def _assert_no_critical_overlap(page: Page) -> None:
    overlaps = page.evaluate(
        """
        () => {
          const selectors = [
            "aside input",
            "aside button",
            ".process-nav a",
            "main .metric",
            "main .wizard-step",
            "main .question-card"
          ];
          const nodes = selectors.flatMap(selector => Array.from(document.querySelectorAll(selector)));
          const boxes = nodes
            .map((node, index) => {
              const rect = node.getBoundingClientRect();
              const style = window.getComputedStyle(node);
              return {
                index,
                label: `${node.tagName.toLowerCase()}#${node.id || ""}.${node.className || ""}`.slice(0, 90),
                left: rect.left,
                top: rect.top,
                right: rect.right,
                bottom: rect.bottom,
                width: rect.width,
                height: rect.height,
                visible: style.display !== "none" && style.visibility !== "hidden" && rect.width > 8 && rect.height > 8
              };
            })
            .filter(box => box.visible && box.bottom > 0 && box.right > 0 && box.left < innerWidth && box.top < innerHeight);
          const overlaps = [];
          for (let leftIndex = 0; leftIndex < boxes.length; leftIndex += 1) {
            for (let rightIndex = leftIndex + 1; rightIndex < boxes.length; rightIndex += 1) {
              const left = boxes[leftIndex];
              const right = boxes[rightIndex];
              const overlapX = Math.max(0, Math.min(left.right, right.right) - Math.max(left.left, right.left));
              const overlapY = Math.max(0, Math.min(left.bottom, right.bottom) - Math.max(left.top, right.top));
              const area = overlapX * overlapY;
              const smaller = Math.min(left.width * left.height, right.width * right.height);
              if (area > 144 && area / smaller > 0.04) {
                overlaps.push(`${left.label} overlaps ${right.label}`);
              }
            }
          }
          return overlaps.slice(0, 8);
        }
        """
    )
    assert overlaps == []


def _wait_for_health(base_url: str) -> None:
    deadline = time.time() + 30
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{base_url}/health", timeout=2) as response:
                if response.status == 200:
                    return
        except urllib.error.URLError:
            time.sleep(0.5)
    raise RuntimeError("E2E server did not become healthy")


def _post_json(base_url: str, path: str, payload: dict) -> None:
    request = urllib.request.Request(
        f"{base_url}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=5) as response:
        assert response.status in {200, 201, 202}


def _seed_company(base_url: str) -> None:
    _post_json(
        base_url,
        "/api/v1/companies",
        {"company_id": "CRTG", "legal_name": "CRTG S.A.C.", "display_name": "CRTG"},
    )
    _post_json(
        base_url,
        "/api/v1/companies/CRTG/portfolio/customers",
        {
            "customer_id": "CLI-MTC",
            "company_id": "CRTG",
            "legal_name": "Ministerio de Transportes",
            "display_name": "MTC",
        },
    )
    _post_json(
        base_url,
        "/api/v1/companies/CRTG/portfolio/programs",
        {
            "program_id": "PRG-TRANSPORTE",
            "company_id": "CRTG",
            "customer_id": "CLI-MTC",
            "name": "Programa Transporte",
        },
    )
    _post_json(
        base_url,
        "/api/v1/companies/CRTG/projects",
        {
            "project_id": "PSZ-2026",
            "company_id": "CRTG",
            "customer_id": "CLI-MTC",
            "program_id": "PRG-TRANSPORTE",
            "name": "Proyecto Suiza",
            "status": "active",
            "lifecycle_stage": "execution",
            "websig_instance_id": "WEB-PSZ-2026",
            "websig_url": "https://websig.example.com/psz",
            "nas_root_uri": "nas://CRTG/PSZ-2026",
            "gis_binding_id": "GIS-PSZ-2026",
            "country": "PE",
            "region": "Lima",
            "province": "Lima",
            "district": "Miraflores",
            "latitude": -12.121,
            "longitude": -77.03,
            "location_source": "e2e_seed",
            "location_validation_status": "validated",
        },
    )
