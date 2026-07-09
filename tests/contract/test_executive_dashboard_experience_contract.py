from control_tower.presentation.dashboard_ui import render_dashboard_html


def test_executive_dashboard_has_rc1_command_sections() -> None:
    html = render_dashboard_html()

    for section in [
        "executiveCommandCenter",
        "executiveSituationSummary",
        "executiveQuickActions",
        "executiveComparisonCards",
        "executiveStatusMatrix",
    ]:
        assert section in html


def test_executive_dashboard_covers_required_business_blocks() -> None:
    html = render_dashboard_html()

    for block in [
        "Estado del portafolio",
        "Empresas",
        "Programas",
        "Proyectos",
        "Riesgos",
        "Produccion",
        "Calidad",
        "Ambiental",
        "SSOMA",
        "Cronograma",
        "GIS",
        "NAS",
        "WEB SIG",
        "Usuarios",
        "Licencias",
        "Reportes",
        "Auditoria",
    ]:
        assert block in html


def test_executive_dashboard_keeps_actions_and_access_states() -> None:
    html = render_dashboard_html()

    for target in [
        "#portfolioExplorer",
        "#corporateGisDashboard",
        "#operationalFlowSection",
        "#corporateReporting",
        "#corporateNotifications",
    ]:
        assert target in html

    assert "no-access" in html
    assert "Sin datos" in html
    assert "Corporate Control Tower / WEB SIG Enterprise" not in html
