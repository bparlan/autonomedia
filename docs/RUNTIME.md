# AUTONOMEDIA — RUNTIME.md

# EXECUTION MODEL

Async First Runtime: asyncio throughout. No synchronous blocking.

Main components:
- scheduler
- queue
- workers
- browser sessions
- AI rewrite layer
- analytics logger

---

# HIGH LEVEL FLOW

```text
Dashboard (User adds Idea)
→ Idea saved to DB (status: 'idea')
→ User approves Idea (status: 'approved')
→ PostingSecretary (Worker) polls 'approved'
→ Secretary generates AI rewrites per platform
→ Secretary validates content via ModerationAdapter
→ Content staged in DB (status: 'prepared')
→ Dashboard (User reviews AI output)
→ User approves specific platform variants (status: 'ready_to_post')
→ PostingExecutor (Worker) polls 'ready_to_post'
→ Executor verifies post_history to prevent duplicates
→ Executor executes browser automation
→ Executor verifies successful post
→ Saves logs/screenshots
→ Promotes content to 'published'
````

---

# LOGGING POLICY

Structured JSON. Required fields:
`timestamp`, `platform`, `task_id`, `worker_id`, `status`, `duration`, `screenshot_path`, `retry_count`, `error_metadata`

---

# BROWSER EXECUTION FLOW

```text
load persistent profile
→ validate auth state
→ open composer
→ inject rewritten content
→ submit
→ verify visible post
→ capture screenshot
→ log success/failure
```

---

# HUMAN-LIKE EXECUTION RULES

Required:

* randomized delays
* pacing jitter
* realistic timing
* avoid robotic execution

Avoid:

* instant interactions
* burst posting
* identical timing

---

# FAILURE POLICY

- Failed post: capture screenshot, logs, DOM snapshot.
- Successful post: capture final screenshot, URL, timestamp.

---

# SESSION RECOVERY

If auth invalid:

* pause posting
* notify operator
* require manual recovery

Avoid automatic re-login systems initially.

---

# PI OPERATIONAL ROLE

Pi should eventually support:

* queue diagnostics
* retry analysis
* selector repair assistance
* analytics interpretation
* rewrite testing
* runtime inspection

This requires:

* structured logs
* machine-readable runtime state
* modular services
