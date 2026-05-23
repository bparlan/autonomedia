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

## canonical_posts

```sql
CREATE TABLE canonical_posts (
    id UUID PRIMARY KEY,
    canonical_text TEXT NOT NULL,
    referral_url TEXT,
    category TEXT,
    tags TEXT[],
    approved BOOLEAN DEFAULT FALSE,
    active BOOLEAN DEFAULT TRUE,
    cooldown_days INTEGER DEFAULT 14,
    platforms TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## post_events

Tracks every publish attempt.

```sql
CREATE TABLE post_events (
    id UUID PRIMARY KEY,
    canonical_post_id UUID REFERENCES canonical_posts(id),
    platform TEXT NOT NULL,
    generated_variant TEXT,
    scheduled_for TIMESTAMP,
    posted_at TIMESTAMP,
    success BOOLEAN,
    result_url TEXT,
    screenshot_path TEXT,
    retry_count INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
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

# CONTENT INGESTION STRATEGY

Initial source:

* Google Sheets CSV export

Future source:

* dashboard-managed canonical content

Import pipeline:

```text
CSV
→ validation
→ normalization
→ PostgreSQL
```

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

Initially minimal.

Track:

* publish success
* timestamps
* retries
* platform
* generated variants
* cooldown effectiveness

Future analytics may include:

* impressions
* engagement
* CTR
* category performance
* posting-time effectiveness

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
