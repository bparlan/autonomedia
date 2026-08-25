# AUTONOMEDIA - ROADMAP.md

## Vision

Autonomedia aims to be the premier local-first autonomous publishing runtime, empowering solo creators and small teams to reliably distribute their content across multiple social platforms. It prioritizes user control, inspectability, and intelligent automation, acting as a personal media assistant.

## Core Principles

- **Local-First:** User retains full control over data and execution.
- **Modular & Extensible:** Designed for easy integration of new platforms, AI models, and agents.
- **Inspectable Runtime:** Transparency in operations, logging, and decision-making.
- **Reliable Automation:** Consistent and on-schedule content distribution.
- **Human-Centric Design:** Intuitive interfaces and workflows.

## Phased Evolution

### Milestone 0: Foundation & Core Idea Scheduling (MVP)
* **Goal:** Enable a solo developer to define an "Idea" and have it automatically rewritten and published on schedule to a single platform (Mastodon).
* **Status:** Completed

### Milestone 1: Multi-Platform Expansion & Authentication
* **Goal:** Extend publishing capabilities to other platforms (LinkedIn, X, Mastodon) and handle secure platform authentication.
* **Status:** Completed (v0.8.0 / M15)

### Milestone 2: Advanced AI & Content Control
* **Goal:** Enhance AI capabilities for content generation, rewriting presets, and content validation.
* **Status:** Completed / Stabilized

### Milestone 3: Analytics, Monitoring & Refinement
* **Goal:** Provide insights into content performance, system health monitoring, and error handling.
* **Status:** Completed / Stabilized

### Milestone 4: Stabilization, Registry Cleanup & Integration
* **Goal:** Normalize project structure, enforce 3-layer registry patterns, and unify entry points.
* **Status:** Active

## Long-Term Backlog

The following epics represent future growth areas and are currently **[Speculative / Pending Architectural Evaluation]**:

### Epic: Multi-Tenant Account Isolation
* **Description:** Add support for multiple user profiles, isolated credential stores, and per-tenant platform tokens.
* **Status:** Backlog [Speculative / Pending Architectural Evaluation]

### Epic: Agent-to-Agent (A2A) Collaboration Protocol
* **Description:** Enable inter-agent message passing and workflow delegation between specialized agent workers.
* **Status:** Backlog [Speculative / Pending Architectural Evaluation]

### Epic: Extensible Plugin Architecture
* **Description:** Expose standard extension points for 3rd-party platform handlers, AI rewriting engines, and custom analytics processors.
* **Status:** Backlog [Speculative / Pending Architectural Evaluation]

### Epic: Multi-User Role Management (RBAC)
* **Description:** Introduce user identity, session management, and granular permission roles (Creator, Reviewer, Admin).
* **Status:** Backlog [Speculative / Pending Architectural Evaluation]

### Epic: Voice & Multi-Modal Processing (TTS / STT)
* **Description:** Integrate local speech-to-text for idea ingestion and text-to-speech for generating audio posts.
* **Status:** Backlog [Speculative / Pending Architectural Evaluation]

### Epic: Social Trend Awareness & Topic Injection
* **Description:** Monitor social platforms for real-time trending topics and inject contextual prompts into the idea planner.
* **Status:** Backlog [Speculative / Pending Architectural Evaluation]
