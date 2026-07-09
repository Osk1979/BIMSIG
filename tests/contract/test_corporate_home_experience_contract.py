from control_tower.presentation.dashboard_ui import render_dashboard_html


def test_corporate_home_operations_center_sections_are_present() -> None:
    html = render_dashboard_html()

    required_sections = [
        "corporateMorningBrief",
        "homeExecutiveSummary",
        "homeBriefTiles",
        "homeQuickActions",
        "homeCriticalAlerts",
        "homeRecentActivity",
        "homeRecommendedActions",
    ]

    for section in required_sections:
        assert section in html


def test_corporate_home_links_to_main_enterprise_flows() -> None:
    html = render_dashboard_html()

    for target in [
        "#portfolioExplorer",
        "#corporateGisDashboard",
        "#enterpriseWizard",
        "#corporateReporting",
    ]:
        assert target in html


def test_corporate_home_keeps_enterprise_boundaries_visible() -> None:
    html = render_dashboard_html()

    assert "No se crean dominios nuevos" not in html
    assert "Centro de Operaciones Corporativo" in html
    assert "WEB SIG Enterprise" in html
