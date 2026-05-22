# AUTONOMEDIA — RUNTIME.md

# EXECUTION MODEL

The runtime is async-first.

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
scheduler
→ select canonical content
→ generate platform rewrite
→ enqueue task
→ worker executes browser automation
→ validate successful post
→ save logs/screenshots
→ analytics update
````

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

# FAILURE HANDLING

On failure:

1. capture screenshot
2. save logs
3. optionally save DOM snapshot
4. increment retry counter
5. requeue if retry policy allows

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
