# AUTONOMEDIA — AGENTS.md

## SYSTEM IDENTITY

Autonomedia is a local-first autonomous publishing runtime.

The system is NOT:
- an AI toy
- a chatbot wrapper
- a workflow spaghetti system
- an experimental multi-agent swarm

The system IS:
- deterministic
- inspectable
- modular
- browser-first
- async-native
- reliability-focused

---

# PRIMARY GOALS

1. Reliable autonomous posting
2. Human-like browser automation
3. Minimal operational overhead
4. Durable architecture
5. Structured observability
6. AI augmentation without AI dependency
7. Long-term extensibility

---

# CORE ENGINEERING PRINCIPLES

## Reliability > Intelligence

The system must continue functioning even if:
- OpenRouter unavailable
- Ollama unavailable
- AI rewrites disabled

AI is augmentation.
Not orchestration.

---

## Deterministic Execution

Every posting task must:
- produce logs
- produce screenshots
- verify post existence
- report structured result

Never allow silent failures.

---

## Browser-First Architecture

The browser is the primary execution environment.

Avoid:
- API-first assumptions
- provider-specific lock-in
- universal abstractions

Prefer:
- Playwright
- persistent sessions
- accessibility selectors
- human-like pacing

---

## Platform Isolation

Each platform has:
- isolated browser profile
- isolated selectors
- isolated posting logic
- isolated validation logic

Never build a universal posting adapter.

---

## Modularity

Every major capability must be independently replaceable.

Examples:
- rewrite provider
- scheduler
- analytics engine
- browser backend
- queue system

---

## Async-First Runtime

Use asyncio-based architecture.

Reasoning:
- browser automation is IO-bound
- queues are IO-bound
- AI requests are IO-bound
- scheduling is IO-bound

Async enables:
- concurrency
- scalable workers
- future multi-account support
- future client support
- efficient browser orchestration

Avoid synchronous blocking design.

---

# PLAYWRIGHT POLICY

## Mandatory Selector Rules

Prefer:
- get_by_role()
- get_by_label()
- get_by_text()
- accessibility selectors

Avoid:
- deep CSS chains
- nth-child selectors
- fragile DOM traversal

Bad:
```python
page.locator("div:nth-child(5) > span > button")
````

Good:

```python
page.get_by_role("button", name="Post")
```

Reasoning:

* accessibility roles change less frequently
* semantic selectors survive redesigns better
* debugging easier
* Playwright optimized for these APIs

This rule is framework policy.
Violations should be treated as architectural debt.

---

# LOGGING POLICY

All logs must be structured JSON.

Every operation should include:

* timestamp
* platform
* task_id
* worker_id
* status
* duration
* screenshot path
* retry count
* error metadata

Reason:
Pi agentic systems must parse runtime events reliably.

---

# AI USAGE POLICY

AI should be used for:

* rewrite generation
* shortening
* tone adaptation
* CTA optimization
* analytics summarization

AI should NOT:

* orchestrate runtime
* manage queues
* control browser state
* perform recursive planning

Avoid over-agentification.

---

# OPERATIONAL PRINCIPLES

Every failed post must capture:

* screenshot
* logs
* DOM snapshot if possible

Every successful post should capture:

* final screenshot
* resulting URL if available
* timestamp

---

# GIT POLICY

* Agents MUST NOT execute `git commit` or `git push`
* Agents MAY suggest `git` commands for human execution
* `CHANGELOG.md` must be updated before staging.
* `progress.md` is operational memory and must track milestone state.
* Runtime directories are never versioned

---

# FUTURE EXPANSION TARGETS

Expected future modules:

* newsletter generation
* blog publishing
* local knowledge memory
* client accounts
* analytics intelligence
* semantic content retrieval

Architecture decisions should preserve compatibility with these expansions.
