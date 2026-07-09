from control_tower.presentation.dashboard_ui import render_dashboard_html


def test_corporate_gis_viewer_has_executive_sections() -> None:
    html = render_dashboard_html()

    for section in [
        "gisExecutiveSummary",
        "gisSpatialSummary",
        "gisSpatialComparisons",
        "gisKpiBridge",
        "gisLayerLegend",
        "gisMapModes",
        "gisServiceSlots",
        "gisProjectDetail",
        "peruAdministrativeMap",
        "peruAdminDetail",
    ]:
        assert section in html


def test_corporate_gis_viewer_exposes_required_views_and_themes() -> None:
    html = render_dashboard_html()

    for view in ["nacional", "regional", "empresa", "programa", "proyecto"]:
        assert f'data-gis-view="{view}"' in html or view in html

    for theme in [
        "estado",
        "riesgo",
        "produccion",
        "cronograma",
        "calidad",
        "ambiental",
        "ssoma",
        "predios",
        "interferencias",
    ]:
        assert f'data-gis-filter="{theme}"' in html or theme in html


def test_corporate_gis_viewer_keeps_websig_boundary_and_service_slots() -> None:
    html = render_dashboard_html()

    assert "No se captura campo" not in html
    assert "No se editan geometr" not in html
    assert "edita geometria ni opera WEB SIG" in html

    for service in ["WMS", "WFS", "WMTS", "Vector Tiles"]:
        assert service in html

    for location_field in ["Region / provincia", "Distrito", "Mapa Administrativo Peru"]:
        assert location_field in html
