# Documentation Update Plan for M18S1 Review Findings

## Overview

This document outlines required documentation updates based on M18S1 review findings. Updates target canonical project documentation in `docs/` directory.

---

## Files Requiring Updates

### 1. FRAMEWORK.md

**Location:** `docs/FRAMEWORK.md`

**Current State:**
- No specific web architecture documentation
- No mention of dashboard implementation
- No clarification on entry points

**Required Updates:**

#### Add New Section: Web Application Architecture

**Insert after "PROJECT LAYOUT" section (around line 520):**

```markdown
## WEB APPLICATION ARCHITECTURE

### Entry Point

Primary FastAPI application entry point: `src/web/app.py`

This app serves the main Autonomedia web interface with the following domains:
- **Command Center:** Operational overview, triage, action queue
- **Content:** Idea backlogs, draft management
- **AI Review:** AI diff inspection and content regeneration
- **Platforms:** Platform-specific verification and status
- **Analytics:** Operational feedback and metrics

### Dashboard Implementation

Health dashboard for infrastructure monitoring:
- **Location:** `src/autonomedia/web/ui/dashboard/health.jsx` (React component)
- **Template:** `src/autonomedia/web/templates/health.html` (fallback)
- **API Endpoint:** `GET /api/health` (requires implementation integration)
- **Integration:** Must be integrated into `src/web/app.py` router

### Routing Pattern

All web routes follow this pattern:
1. Domain extraction (per UX architecture)
2. Single HTTP method per route (GET/POST only)
3. Template-based rendering for HTML responses
4. JSON responses for API endpoints

### React vs Templates

**Preferred:** React components for complex, interactive UI
- Better state management
- Easier testing
- More maintainable

**Fallback:** Jinja2 templates (current implementation)
- Faster to implement
- No build step required
- Good for simple pages

### Router Hierarchy

```
src/web/app.py (Main entry point)
├── / (Root)
├── /content (Content management)
├── /platforms (Platform status)
├── /rewrites (AI rewrite management)
├── /registry (Registry management)
├── /health (Health dashboard)
└── /api/* (API endpoints)

src/autonomedia/web/api/* (API routers)
├── comments.py
├── content.py
└── likes.py
```

### Integration Rules

**NEW implementation MUST:**
- Integrate into `src/web/app.py` (NOT standalone server files)
- Use React components for dashboard UI (spec requires this)
- Register routes in app router
- Follow existing domain extraction pattern

**DO NOT:**
- Create separate FastAPI apps without clear justification
- Implement routes in inactive server files
- Use hardcoded HTML when React component is available
- Duplicate functionality between files
```

---

### 2. MILESTONES.md

**Location:** `docs/MILESTONES.md`

**Current State:**
- Lists M15 as Active
- Lists M16 as Active
- No mention of M18

**Required Updates:**

#### Update "Archived Milestones" section

**Replace lines 8-9:**
```markdown
### M15 - Cross-Platform Expansion (Archived)
### M16 - Automated Testing and Use-Case Generation Framework (Active)
```

**With:**
```markdown
### M18 - Infrastructure Health Dashboard (In Progress → milestones/M18/)
### M15 - Cross-Platform Expansion (Archived)
### M16 - Automated Testing and Use-Case Generation Framework (Active)
```

#### Add M18 Details (after M18 section)

**Insert after line 43 (after M15 known limitations):**

```markdown
### M18 - Infrastructure Health Dashboard (In Progress → milestones/M18/)

**Status:** In Progress (Test Implementation Phase)
**Spec:** M18S1
**Verification:** M18S1V
**Review:** M18S1R, M18S1_FINDINGS.md
**Active Tests:** test_health_endpoint.sh, test_health_dashboard_ui.sh, test_health_dashboard_binding.sh

**Completed Requirements:**
- API endpoint handler created (`get_health_status()`)
- Router registered with `/api/health` route
- React dashboard component created (`health.jsx`)
- HTML dashboard template created (`health.html`)
- Basic server integration in `src/autonomedia/web/server.py`

**Known Limitations:**
- Wrong entry point: Dashboard implemented in inactive `src/autonomedia/web/server.py` instead of `src/web/app.py`
- Architecture deviation: React component not integrated; hardcoded HTML template is being served
- Duplicate /health endpoints: Two conflicting endpoints exist with different behaviors
- Evaluation report discrepancy: Claims tests passed, actual execution shows failures
- Missing metadata: Milestone contract lacks required `id` field
- No completion report: M18S1C.md not generated

**Critical Issues Identified:**
- FIND-001: Wrong entry point integration (src/web/app.py is active, server.py is not)
- FIND-002: Dashboard architecture deviation (React not integrated)
- FIND-003: Evaluation report inaccuracy (tests fail in current environment)
- FIND-004: Missing milestone contract ID
- FIND-006: Duplicate /health endpoints with conflicting behavior

**Documentation:**
- Specification: `milestones/M18/M18S1.md`
- Verification: `milestones/M18/M18S1V.md`
- Review: `milestones/M18/M18S1_REVIEW.md`
- Findings: `milestones/M18/M18S1_FINDINGS.md`
```

#### Add M18 Status to Milestone Lifecycle

**Replace lines 231-239 (Milestone Lifecycle section):**

```markdown
## Milestone Lifecycle

1. **Proposal**: Milestone documented in `specs/` directory
2. **Implementation**: Code and tests added per specification
3. **Verification**: Verification document created in `verifications/` directory
4. **Review**: Review document created in `reviews/` directory
5. **Approval**: Milestone approved by team
6. **Completion**: All requirements verified, code merged
7. **Archival**: Moved to `milestones/archive/` with full documentation

## Active Milestones

### M18 - Infrastructure Health Dashboard

**Current Phase:** Review and Correction
**Previous Phase:** Test Implementation (M18S1TE.md)
**Next Phase:** Implementation Fix and Re-verification

**Outstanding Work:**
1. Integrate dashboard into `src/web/app.py`
2. Fix evaluation report accuracy
3. Add `id` field to M18.md
4. Generate M18S1C.md completion report
5. Resolve duplicate /health endpoints
6. Merge React and HTML implementations
7. Fix test set YAML parsing
8. Re-run and verify tests
```

---

### 3. SPEC.md (Optional)

**Location:** `docs/SPEC.md`

**Current State:**
- No web infrastructure requirements
- No dashboard specifications

**Required Updates:**

#### Add New Section: Web Infrastructure

**Insert after "SUCCESS CRITERIA" section (around line 233):**

```markdown
# WEB INFRASTRUCTURE

## Dashboard Implementation

Health dashboard provides real-time visibility into infrastructure status:

- **Components Monitored:**
  - Database health
  - Runtime directory status
  - Test suite integrity
  - Source code availability

- **Access Method:**
  - URL: `/health` (dashboard page)
  - API: `GET /api/health` (status JSON)
  - Authentication: Per-project policy (no hardcoded credentials)

- **Response Format (API):**
  ```json
  {
    "database": "healthy" | "unhealthy",
    "runtime": "healthy" | "unhealthy",
    "tests": "healthy" | "unhealthy",
    "src": "healthy" | "unhealthy"
  }
  ```

## Web Application Structure

The web application follows these principles:

- **Frameworks:** FastAPI (backend), React (dashboard UI), Jinja2 (fallback templates)
- **Entry Point:** `src/web/app.py` (main FastAPI application)
- **Routing:** RESTful with single HTTP method per route
- **Templates:** `src/web/templates/` directory
- **Components:** `src/web/ui/` directory for React components

## Integration Requirements

Web features must:
1. Integrate into `src/web/app.py` (NOT standalone server files)
2. Use React components for dashboard UI (spec requires this)
3. Register routes in app router
4. Follow existing domain extraction pattern
5. Include tests covering happy path and error cases
```

---

### 4. PLAYBOOK.md (Optional)

**Location:** `docs/PLAYBOOK.md`

**Current State:**
- No web development workflow
- No dashboard implementation guidance

**Required Updates:**

#### Add New Section: Web Development Workflow

**Insert at end of document (after "DEVELOPMENT REVIEW RULES"):**

```markdown
# WEB DEVELOPMENT WORKFLOW

## Dashboard Implementation

When implementing a new dashboard or monitoring feature:

1. **Design Phase:**
   - Determine if React component or template is appropriate
   - Prefer React for complex, interactive UI
   - Use templates for simple pages

2. **Implementation Phase:**
   - Create React component in `src/web/ui/`
   - Create template in `src/web/templates/` (if needed)
   - Implement API endpoint in `src/autonomedia/web/api/`
   - Integrate into `src/web/app.py` router
   - Register routes using FastAPI router pattern

3. **Testing Phase:**
   - Write tests for happy path
   - Write tests for error paths
   - Verify dashboard renders correctly
   - Verify API returns correct JSON
   - Test data binding

4. **Integration Phase:**
   - Ensure route is registered in main app
   - Verify endpoint is accessible
   - Test in both dev and production environments
   - Update documentation if needed

## Common Pitfalls

### Wrong Entry Point
**Problem:** Implementing routes in `src/autonomedia/web/server.py` instead of `src/web/app.py`
**Solution:** Always integrate into the main app (`src/web/app.py`)

### Architecture Deviation
**Problem:** Hardcoding HTML instead of using React component
**Solution:** Use React for dashboard UI; templates only as fallback

### Duplicate Routes
**Problem:** Creating duplicate `/health` or similar endpoints
**Solution:** Use a single entry point; rename if needed

### Missing Tests
**Problem:** Dashboard changes without corresponding tests
**Solution:** Always write tests before/after changes
```

---

## Update Priority

### Critical (Must Do)

1. **FRAMEWORK.md** - Add web architecture section
   - Clarify entry point (src/web/app.py)
   - Document dashboard implementation requirements
   - Specify integration rules

2. **MILESTONES.md** - Add M18 entry
   - Document current status (In Progress)
   - List known limitations
   - List critical issues

### High Priority (Should Do)

3. **SPEC.md** - Add web infrastructure section
   - Document dashboard requirements
   - Specify API response format
   - Outline integration requirements

### Medium Priority (Nice-to-Have)

4. **PLAYBOOK.md** - Add web development workflow
   - Provide step-by-step guidance
   - Document common pitfalls
   - Link to relevant framework sections

---

## Implementation Notes

### FrameWork.md Changes
- Location: `docs/FRAMEWORK.md`
- Insert point: After "PROJECT LAYOUT" section (~line 520)
- Length: ~150 lines
- Sections: Web Application Architecture, Dashboard Implementation, Routing Pattern, Integration Rules

### MILESTONES.md Changes
- Location: `docs/MILESTONES.md`
- Changes:
  - Update Archived Milestones section (add M18)
  - Add M18 details section (~30 lines)
  - Update Milestone Lifecycle section
  - Add Active Milestones section
- Length: ~80 lines total additions

### SPEC.md Changes
- Location: `docs/SPEC.md`
- Insert point: After "SUCCESS CRITERIA" section (~line 233)
- Length: ~60 lines
- Sections: Web Infrastructure, Dashboard Implementation, Web Application Structure, Integration Requirements

### PLAYBOOK.md Changes
- Location: `docs/PLAYBOOK.md`
- Insert point: At end of document
- Length: ~80 lines
- Sections: Web Development Workflow, Dashboard Implementation, Common Pitfalls

---

## Verification Checklist

After updates:

- [ ] FRAMEWORK.md has web architecture section
- [ ] FRAMEWORK.md clarifies entry point
- [ ] FRAMEWORK.md documents dashboard requirements
- [ ] MILESTONES.md includes M18 entry
- [ ] MILESTONES.md documents M18 status
- [ ] MILESTONES.md lists M18 limitations
- [ ] MILESTONES.md lists M18 critical issues
- [ ] SPEC.md has web infrastructure section
- [ ] SPEC.md documents dashboard requirements
- [ ] PLAYBOOK.md has web development workflow
- [ ] PLAYBOOK.md documents common pitfalls
- [ ] All changes follow project formatting conventions

---

## Related Documents

- **M18S1_REVIEW.md**: Original review findings
- **M18S1_FINDINGS.md**: Detailed findings with priority resolution plan
- **M18S1.md**: Original specification
- **M18S1V.md**: Verification protocol
- **M18S1E.md**: Evaluation report (needs correction)

---

**Plan Version:** 1.0
**Generated:** 2026-08-21
**Purpose:** Document updates based on M18S1 review findings
**Status:** READY FOR APPROVAL
