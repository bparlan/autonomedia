# AUTONOMEDIA — DATA.md

# DATABASE PHILOSOPHY

PostgreSQL is the canonical data layer.

Google Sheets is temporary ingestion layer only.

The database must support:
- scheduling
- analytics
- retries
- platform tracking
- client support later

---

# INITIAL DATABASE SETUP

PostgreSQL currently running locally on:

```text
localhost:5432
````

Default databases observed:

* postgres
* template1
* bparlan

---

# INITIAL DATABASE CREATION

Connect:

```bash
psql postgres
```

Create database:

```sql
CREATE DATABASE autonomedia;
```

Connect:

```bash
psql autonomedia
```

---

# INITIAL TABLES

## content

```sql
CREATE TABLE IF NOT EXISTS content (
    id TEXT PRIMARY KEY,
    topic TEXT NOT NULL,
    type TEXT NOT NULL,
    status TEXT NOT NULL,  -- 'idea', 'approved', 'prepared', 'ready_to_post', 'published', 'failed'
    source_idea TEXT,
    link_url TEXT,
    hashtags JSONB DEFAULT '[]',
    mentions JSONB DEFAULT '{}',
    ai_rewrites JSONB DEFAULT '[]',
    prepared_content JSONB DEFAULT '{}',
    platforms JSONB DEFAULT '[]',
    scheduled_at TIMESTAMP WITH TIME ZONE,
    error_log TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### Schema Notes
* `content.status`: Determines UI visibility and processing flow.
  * `idea`: Draft state, visible in `/content` view.
  * `prepared`: Ready/Approved state, triggers rewrite workflow, visible in `/rewrites`.

---

## post_history

Tracks execution safely to avoid duplicates across worker restarts.

```sql
CREATE TABLE IF NOT EXISTS post_history (
    id SERIAL PRIMARY KEY,
    content_id TEXT NOT NULL,
    platform TEXT NOT NULL,
    status TEXT NOT NULL,
    error_log TEXT,
    published_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (content_id, platform)
);
```

---

## browser_sessions

```sql
CREATE TABLE browser_sessions (
    id UUID PRIMARY KEY,
    platform TEXT UNIQUE,
    profile_path TEXT,
    last_validated_at TIMESTAMP,
    status TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## verifications

```sql
CREATE TABLE verifications (
    id TEXT PRIMARY KEY,
    content_id TEXT NOT NULL REFERENCES content(id),
    platform TEXT NOT NULL,
    status TEXT NOT NULL, -- 'pending', 'approved', 'rejected', 'posted'
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Schema Notes
* `verifications.status`: Tracks per-platform approval state.
  * `pending`: Created when AI generates content for a platform.
  * `approved`: User has verified; eligible for posting queue.
  * `rejected`: User has rejected; excluded from queue.
  * `posted`: Successfully published.

---

# CONTENT INGESTION STRATEGY

Initial source:
* Dashboard-managed Content Domain UI (Backlog/Ideas)
* HTMX-powered forms for quick triage

Future source:
* API endpoints for external capture (e.g. browser extensions)
* Ingestion pipelines from notes or RSS

---

# TRACKING STRATEGY

Every platform should receive:

* unique UTM parameters
* per-platform analytics attribution

Example:

```text
?utm_source=x
?utm_source=linkedin
```

---

# ANALYTICS PHILOSOPHY

Analytics is an operational feedback engine, not vanity charts.

Track Operational Metrics:
* publish success/failure rates
* session health status
* token cost efficiency
* worker uptime

Track Content Performance:
* which AI rewrites were approved
* platform underperformance
* scheduling quality

Future analytics may include:
* impressions
* engagement (likes, shares) post-publish

---

# STORAGE POLICY

All screenshots stored locally.

Recommended structure:

```text
storage/screenshots/
```

All logs stored locally.

Recommended structure:

```text
storage/logs/
```

---

# FAILURE OBSERVABILITY

Every failure must include:

* structured log
* screenshot
* platform metadata
* error details

No silent failures allowed.
