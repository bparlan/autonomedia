# AUTONOMEDIA — FRAMEWORK.md

# TECHNOLOGY STACK

## Language

Python 3.12+

Reasoning:
- mature Playwright ecosystem
- async ecosystem strong
- AI integrations trivial
- good tooling
- compatible with pi workflows

---

# PACKAGE MANAGEMENT

Use uv.

Never use:
- pip directly
- poetry initially

Reasoning:
- faster
- cleaner dependency resolution
- modern workflow
- reproducible environments

Installation:

```bash
brew install uv
````

Project init:

```bash
mkdir -p ~/devcode/autonomedia
cd ~/devcode/autonomedia
uv init
```

---

# CORE DEPENDENCIES

```bash
uv add playwright
uv add redis
uv add sqlalchemy
uv add psycopg[binary]
uv add pydantic
uv add fastapi
uv add uvicorn
uv add apscheduler
uv add structlog
uv add pandas
uv add openai
```

Install browser:

```bash
playwright install chromium
```

---

# ASYNC DESIGN EXPLANATION

## Why Async?

Browser automation spends most time waiting:

* pages loading
* selectors appearing
* network responses
* AI requests
* queue events

This is IO-bound work.

Async allows:

* one runtime handling many operations efficiently
* future concurrency
* scalable scheduling
* lower resource waste

Example:

Without async:

```text
wait browser
wait network
wait AI
wait queue
```

With async:

```text
multiple tasks progress simultaneously
```

This becomes critical later for:

* client accounts
* multiple workers
* analytics jobs
* background rewriting

---

# PLAYWRIGHT PHILOSOPHY

## Accessibility-First Selectors

Playwright excels at semantic selectors.

Preferred APIs:

```python
page.get_by_role()
page.get_by_label()
page.get_by_text()
```

Advantages:

* resilient to redesigns
* aligned with accessibility metadata
* easier debugging
* more readable automation

Example:

Bad:

```python
page.locator("div > div:nth-child(4) button")
```

Good:

```python
page.get_by_role("button", name="Post")
```

---

# DATABASE

Use PostgreSQL.

Installed locally.

Postgres should become source-of-truth immediately.

Google Sheets only acts as ingestion source.

---

# LOCAL PROCESS PHILOSOPHY

Use native local runtime.

Avoid Docker initially.

Reasoning:

* browser automation simpler
* macOS compatibility easier
* lower debugging complexity
* persistent profiles easier

Recommended local tooling:

* uv
* tmux
* launchd
* native processes

---

# LOGGING STACK

Use structlog.

All logs JSON structured.

Reason:

* machine readable
* pi-compatible
* searchable
* future analytics friendly

---

# BROWSER PROFILE MANAGEMENT

Each platform profile isolated.

Profiles stored under:

```text
browser/profiles/
```

Never share browser state across platforms.

---

# FUTURE STACK EXPANSIONS

Planned future capabilities:

* newsletter publishing
* blog publishing
* semantic memory
* client account isolation
* analytics intelligence
* knowledge retrieval

Current architecture must preserve compatibility.
