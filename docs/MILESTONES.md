# Milestones

This directory tracks all project milestones, their states, and lifecycle management.


## Archived Milestones

### M15 - Cross-Platform Expansion (Archived)
### M16 - Automated Testing and Use-Case Generation Framework (Active)


**Status:** Completed  
**Spec:** M15  
**Archive:** milestones/archive/M15/  
**Verification:** M15S1V, M15S2V, M15S3V, M15S4V  
**Review:** M15S1R, M15S2R, M15S4R  
**Completion:** M15S1C, M15S2C, M15S3C, M15S4C  

**Completed Requirements:**
- Unified platform abstraction layer with `post()` API for Mastodon, LinkedIn, and X
- Platform-specific task handlers deployed and tested
- Platform requirements documentation created (M15S3)
- Platform constraints API with character limits and validation
- Content adaptation utilities for multi-platform posting
- Reauthentication management script with CLI tools
- Production deployment and monitoring documentation
- Comprehensive platform-specific guidance (M15S2, M15S3)

**Known Limitations:**
- Integration test suite has 29 failing tests (test assertions mismatch implementation signatures)
- OAuth 2.0 browser flows implemented as placeholders in reauth script
- Health check HTTP endpoints documented but not implemented
- Real-time monitoring dashboard documented but not implemented
- Token management via environment variables (no encrypted vault support)

**Critical Issues Identified:**
- Missing return statement in `XHandler.format_tweet()` (M15I1)
- Missing `get_rate_limit_status()` method in handlers (M15I1)
- Incomplete OAuth flow implementations in reauth script (M15I1, M15I2)

**Documentation:**
- Platform requirements: `docs/platform_requirements.md`
- Deployment guide: `docs/deployment_guide.md`
- Troubleshooting guide: `docs/troubleshooting_guide.md`

---

### M14 - Daily Posting Routine with Randomized Intervals (Archived → milestones/archive/M14/)

**Status:** Completed
**Archive:** milestones/archive/M14.md, milestones/archive/M14S1.md, milestones/archive/M14S1V.md, milestones/archive/M14S1R.md
**Verification:** M14S1V  
**Review:** M14S1R  

**Completed Requirements:**
- Randomized delay system (2-10 minutes between batches)
- Verification status filtering for mastodon
- Max 1-2 items per execution with 8-hour window
- `expires_at` TTL field (12 hours default)
- Manual trigger script `run_daily_posting.py`
- Dry-run mode

- Legacy `PostingWorker` still present without verification checks

---

### M13 - Ready to Publish Platform Visibility (Archived → milestones/archive/M13/)

**Status:** Completed  
**Specs:** M13S1, M13S2, M13S3, M13S4  
**Archive:** milestones/archive/M13.md, milestones/archive/M13S1.md, M13S1R.md, M13S1V.md, M13S2.md, M13S2R.md, M13S2V.md, M13S3.md, M13S3R.md, M13S3V.md, M13S4.md, M13S4R.md, M13S4V.md

**Completed Requirements:**
- Per-platform verification status in dashboard
- Verified state badges
- Backend query modifications for `ready_to_post` items
- Frontend ready-to-publish rows
- Platform health filtering

---

### M12 - Granular Platform Verification (Archived → milestones/archive/M12/)

**Status:** Completed  
**Spec:** M12  
**Archive:** milestones/archive/M12.md, milestones/archive/M12-findings.md

**Completed Requirements:**
- `verification_status` JSONB column on `content` table
- Per-platform approval workflow
- `PostingSecretary.process_verified_content()` filtering
- Platform dispatch integration

---

### M11 - Observability & Self-Healing (Archived → milestones/archive/M11/)

**Status:** Completed  
**Archive:** milestones/archive/M11.md, milestones/archive/M11-OBSERVABILITY-AND-SELF-HEALING.md, milestones/archive/M11-Verify.md, milestones/archive/M11-Review.md, milestones/archive/M11.md

**Completed Requirements:**
- Structured runtime logging
- Error resolution and auto-retry
- Session health monitoring
- Failure capture (screenshots, logs, DOM snapshots)

---

### M10 - Autonomous Runtime (Archived → milestones/archive/M10/)

**Status:** Completed  
**Archive:** milestones/archive/M10.md, milestones/archive/M10-AUTONOMOUS-RUNTIME.md, milestones/archive/M10-VERIFICATION.md, milestones/archive/M10-Verify.md, milestones/archive/M10-review.md, milestones/archive/M10.md

**Completed Requirements:**
- Async Assembly Line architecture
- Browser profile isolation
- Playwright anti-detection profiles
- Human-like pacing and randomized delays

---

### M9 - Platform Health & Analytics (Archived → milestones/archive/M9/)

**Status:** Completed  
**Archive:** milestones/archive/M9.md, milestones/archive/findings_M9.md

**Completed Requirements:**
- Session health tracking
- Failed post logging
- Platform status visibility
- Analytics integration

---

### M8 - Domain Extraction & UX (Archived → milestones/archive/M8/)

**Status:** Completed  
**Archive:** milestones/archive/M8.md

**Completed Requirements:**
- Domain extraction UI
- Command Center (inbox view)
- Content management backlogs
- AI review workflow

---

### M7 - Moderation & Guardrails (Archived → milestones/archive/M7/)

**Status:** Completed  
**Archive:** milestones/archive/M7.md

**Completed Requirements:**
- ModerationAdapter for content validation
- Browser anti-detection profiles
- Duplicate post prevention
- Human-in-the-loop review

---

### M6 - AI & Assembly Line (Archived → milestones/archive/M6/)

**Status:** Completed  
**Archive:** milestones/archive/M6.md

**Completed Requirements:**
- AI rewrite generation with Gemini
- Assembly Line state machine
- PostingSecretary (AI Worker)
- PostingExecutor (Browser Worker)

---

### M5 - Content Generation (Archived → milestones/archive/M5B/, M5C/, M5X/)

**Status:** Completed  
**Archive:** milestones/archive/M5B.md, milestones/archive/M5C.md, milestones/archive/M5X.md

**Completed Requirements:**
- Content idea generation
- AI rewrite generation
- Platform-specific transformations

---

### M4 - Browser Setup (Archived → milestones/archive/M4/)

**Status:** Completed  
**Archive:** milestones/archive/M4.md

**Completed Requirements:**
- Playwright setup
- Browser profile persistence
- Basic routing

---

### M3 - Initial Deployment (Archived → milestones/archive/M3/)

**Status:** Completed  
**Archive:** milestones/archive/M3.md

**Completed Requirements:**
- Initial deployment
- Basic infrastructure

---

### M2 - Schema Design (Archived → milestones/archive/M2/)

**Status:** Completed  
**Archive:** milestones/archive/m2_technical_specifications.md

**Completed Requirements:**
- Database schema design
- Content model definition

---

### M1 - Foundation (Archived → milestones/archive/M1/)

**Status:** Completed  
**Archive:** milestones/archive/M1_Content_Idea_Ingestion_AI_Analysis.md

**Completed Requirements:**
- Project initialization
- Basic structure setup

---

## Milestone Lifecycle

1. **Proposal**: Milestone documented in `specs/` directory
2. **Implementation**: Code and tests added per specification
3. **Verification**: Verification document created in `verifications/` directory
4. **Review**: Review document created in `reviews/` directory
5. **Approval**: Milestone approved by team
6. **Completion**: All requirements verified, code merged
7. **Archival**: Moved to `milestones/archive/` with full documentation

## Notes

- All milestone files are preserved in `milestones/archive/` with complete history
- Archive directory is organized by milestone with separate subdirectories for specs, verifications, and reviews when applicable
- Raw artifacts (test outputs, verification logs) stored in `milestones/archive/raw_artifacts/`

## Known Issues & Lessons Learned

### M14 - Daily Posting Routine with Randomized Intervals





1. **Legacy Code Path Conflict Risk**
   - Issue: `PostingWorker` in `posting_executor.py` exists alongside `posting_routine()`. Both can query `ready_to_post` without coordination. M14S1 spec states old worker "posts content regardless of platform verification state."
   - Recommendation: Either deprecate `PostingWorker` or add a compatibility layer that prevents simultaneous execution.
   - Status: Potential operational hazard if both workers are active.

# DEVELOPMENT REVIEW RULES

If the review fails, the agent must abide by these rules when applying fixes:

1. **The Spec is Law:** You cannot change the `docs/specs/` or `docs/verifications/` files to make the tests pass. If the code cannot meet the spec, the code is wrong.

2. **Surgical Edits Only:** Do not rewrite entire files to fix a minor issue. Use the `edit` tool to specifically target the broken lines.

3. **Iron Law of Debugging:** If tests are failing, diagnose the root cause *before* changing code. Form a hypothesis, and test one hypothesis at a time.

4. **Run Tests After Every Fix:** You must run `just test` and verify the `exitCode` before deciding a revision is complete.


