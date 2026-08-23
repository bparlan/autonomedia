# Template Organization Documentation

This document explains the consolidated template structure and explains why certain directories were removed during refactoring.

## Why Template Consolidation Matters
The project had two template directories:
1. `src/web/templates/` - Main template location
2. `src/autonomedia/content/templates/` - Legacy template location

Keeping multiple template locations caused:
- Duplicate partial definitions
- Unpredictable template resolution
- Configuration conflicts in template loading

## Unified Template Structure

**Root Directory**
```
src/web/templates/
├── base.html                # Primary base template for all pages
├── partials/                # Reusable component templates
│   ├── content_row.html     # Table row structure
│   ├── content_status.html  # Status badge components
│   └── ...                 # Other partial templates
├── health_dashboard.html    # Health dashboard view
├── dashboard.html           # Main dashboard layout
├── index.html               # Home/index page
├── platforms.html           # Platform configuration display
├── registry.html            # Dependency registry view
├── review.html              # Content review interface
├── rewrites.html            # URL rewriting management
└── health.html              # Content health status page
```

## Legacy Directory Removal
- **Removed:** `src/autonomedia/content/templates/`
- **Reason:** This directory was empty and contained no active templates. It was a place where duplicate templates could be accidentally placed.

## Reference Usage Pattern
Maintaining consistent template loading throughout the codebase:

```python
# Preferred pattern for template rendering
template = env.get_template("partials/content_row.html")

# All templates live under src/web/templates/
# No absolute or relative path variations allowed
```

## Migration Guidance
When adding new templates:
1. **Location must be** `src/web/templates/` or `src/web/templates/partials/`
2. **No new directories** should be created at the top level
3. **Naming must follow** existing conventions (e.g., `*.html` extension)
4. **References in code** should use path-relative includes:
   ```python
   # Correct
   template = env.get_template("partials/content_row.html")
   
   # Incorrect
   template = env.get_template("../content/templates/partials.html")
   ```

## Verification
This structure is enforced by:
- Automated tests in `tests/unit/test_template_structure.py`
- Linting rules preventing new template directories (`FORBIDDEN_TEMPLATE_DIRS` check)
- CI pipeline validation