from pathlib import Path

# Consolidated single template source
TEMPLATE_ROOT = Path("src/web/templates")
PARTIALS_DIR = TEMPLATE_ROOT / "partials"


# All expected templates (single source of truth)
EXPECTED_TEMPLATES = [
    "base.html",
    "content.html",
    "dashboard.html",
    "health_dashboard.html",
    "index.html",
    "platforms.html",
    "registry.html",
    "review.html",
    "rewrites.html",
]
EXPECTED_PARTIALS = [
    "content_row.html",
    "content_status.html",
    "content_edit_form.html",
    "edit_form.html",
    "review_form.html",
    "row.html",
]


# Redundant directories that must NOT exist
FORBIDDEN_TEMPLATE_DIRS = [
    "src/autonomedia/content/templates",
    "src/content/templates",
]


def test_template_directory_consolidated():
    assert TEMPLATE_ROOT.exists(), f"Consolidated template root missing: {TEMPLATE_ROOT}"
    assert PARTIALS_DIR.exists(), f"Partials directory missing: {PARTIALS_DIR}"


def test_all_core_templates_exist():
    for name in EXPECTED_TEMPLATES:
        path = TEMPLATE_ROOT / name
        assert path.exists(), f"Missing core template: {name}"
        assert path.stat().st_size > 0, f"Empty template file: {name}"


def test_all_partials_exist():
    for name in EXPECTED_PARTIALS:
        path = PARTIALS_DIR / name
        assert path.exists(), f"Missing partial: {name}"
        assert path.stat().st_size > 0, f"Empty partial file: {name}"


def test_no_duplicate_template_dirs():
    for forbidden in FORBIDDEN_TEMPLATE_DIRS:
        assert not Path(forbidden).exists(), f"Redundant template dir still present: {forbidden}"


def test_base_template_inherits_consistency():
    base_path = TEMPLATE_ROOT / "base.html"
    assert base_path.exists()
    content = base_path.read_text(encoding="utf-8")
    # All templates extend base.html — base must contain block definitions
    assert "{% block content %}" in content or "{% block " in content


def test_partials_referenced_correctly():
    # Verify at least one template includes a partial (confirms structure)
    content_path = TEMPLATE_ROOT / "content.html"
    if content_path.exists():
        content = content_path.read_text(encoding="utf-8")
        assert "partials/" in content, "Content template should reference partials"