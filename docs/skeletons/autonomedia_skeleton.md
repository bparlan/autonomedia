# Autonomedia Codebase Skeletons
> Use this for low-token code understanding. Prefer over reading full files.

### File: /Users/bparlan/devcode/autonomedia/tests/conftest.py
import sys
from pathlib import Path
import pytest
from src.database.client import DatabaseClient
async def db_pool():

### File: /Users/bparlan/devcode/autonomedia/tests/test_m12_migration.py
import os
import sqlite3
import pytest
def test_verification_status_column_exists():
def test_verification_status_default_empty():

### File: /Users/bparlan/devcode/autonomedia/tests/run_scenarios.py
import asyncio
import json
from src.database.client import DatabaseClient
async def run_scenario_test():

### File: /Users/bparlan/devcode/autonomedia/tests/test_m12_verification.py
import pytest
from playwright.async_api import async_playwright
async def test_m12_verification():

### File: /Users/bparlan/devcode/autonomedia/tests/test_m13_migration.py
from src.database.schema import INIT_SCHEMA
def test_init_schema_has_verification_status():

### File: /Users/bparlan/devcode/autonomedia/tests/test_m13_s3_frontend_rows.py
import json
from pathlib import Path
import pytest
from jinja2 import Environment, FileSystemLoader
class MockRequest:
def __init__(self):
def path(self):
def jinja_env():
def mock_request():
class TestM13S3ReadyToPublishPerPlatformRows:
def test_item_with_two_verified_platforms_shows_two_rows(self, jinja_env, mock_request):
def test_item_with_one_non_verified_platform_shows_neutral_badge(self, jinja_env, mock_request):
def test_content_shorter_than_100_chars_displays_full_text(self, jinja_env, mock_request):
def test_item_with_no_platforms_shows_no_rows(self, jinja_env, mock_request):
def test_content_preview_uses_text_xs_styling(self, jinja_env, mock_request):
def test_review_verify_link_present_for_all_rows(self, jinja_env, mock_request):
def test_row_count_equals_sum_of_platforms(self, jinja_env, mock_request):
def test_long_content_truncated_at_100_chars(self, jinja_env, mock_request):
def test_unknown_verification_status_shows_pending(self, jinja_env, mock_request):

### File: /Users/bparlan/devcode/autonomedia/tests/test_ai_analysis.py
import json
import pytest
from src.autonomedia.ai.analysis import perform_ai_analysis
class MockDatabaseClient:
def __init__(self):
async def get_pool(self):
class MockPool:
async def execute(self, query, *args):
def mock_dependencies(monkeypatch):
def test_perform_ai_analysis_success(mock_dependencies):
def test_perform_ai_analysis_empty_idea(mock_dependencies):
def test_perform_ai_analysis_no_entities(mock_dependencies):
def test_perform_ai_analysis_with_mentions_and_hashtags(mock_dependencies):

### File: /Users/bparlan/devcode/autonomedia/tests/test_ingestion.py
import pytest
from src.autonomedia.ingestion.content_ingestor import capture_content_idea
def test_capture_content_idea_success():
def test_capture_content_idea_empty():
def test_capture_content_idea_whitespace():

### File: /Users/bparlan/devcode/autonomedia/tests/test_m13_s4_verified_state.py
import json
from pathlib import Path
import pytest
from jinja2 import Environment, FileSystemLoader
class MockRequest:
def __init__(self):
def path(self):
def jinja_env():
def mock_request():
class TestM13S4VerifiedStateInQueue:
def test_tc1_single_platform_ready_to_post_shows_verified_badge(self, jinja_env, mock_request):
def test_tc2_multi_platform_mixed_verification_shows_both_badges(self, jinja_env, mock_request):
def test_tc3_ready_to_post_empty_verification_shows_generic_badge(self, jinja_env, mock_request):
def test_tc4_malformed_verification_json_no_ui_crash(self, jinja_env, mock_request):
def test_tc5_review_verify_link_remains_for_ready_to_post(self, jinja_env, mock_request):

### File: /Users/bparlan/devcode/autonomedia/tests/simple_test.py
def test_failing_example():

### File: /Users/bparlan/devcode/autonomedia/tests/test_m14_routine.py
import json
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, patch
import pytest
from src.autonomedia.core.posting_routine import (
    _apply_randomized_delay,
    _get_last_posted_at,
    _get_verified_content,
    posting_routine,
)
async def reset_db(db_pool):
def make_verification_status(verified=True, verified_at=None, expires_at=None):
async def test_verified_mastodon_content_is_processed(db_pool):
async def test_non_verified_content_skipped(db_pool):
async def test_expired_content_deprioritized(db_pool):
async def test_priority_content_bypasses_expiration(db_pool):
async def test_dry_run_creates_no_post_history(db_pool):
async def test_randomized_delay_range():
async def test_first_execution_posts_one_item(db_pool):
async def test_posts_one_to_two_items(db_pool):
async def test_mixed_verified_unverified_platforms(db_pool):
async def test_second_execution_within_8_hours_no_additional(db_pool):
async def test_execution_after_8_hours_second_item_allowed(db_pool):
def test_manual_trigger_script_exists():
async def test_item_without_verification_status_skipped(db_pool):
async def test_no_verified_content_graceful_exit(db_pool):
async def test_get_verified_content_returns_verified_items(db_pool):
async def test_get_last_posted_at(db_pool):

### File: /Users/bparlan/devcode/autonomedia/tests/test_m13_backend.py
import json
import pytest
from httpx import ASGITransport, AsyncClient
from src.database.schema import INIT_SCHEMA
from src.web.app import app
async def reset_db(db_pool):
async def test_rewrites_includes_ready_to_post(db_pool):
async def test_prepared_content_endpoint(db_pool):
async def test_approve_review_filters_healthy_platforms(db_pool):
async def test_remove_from_queue_clears_verification(db_pool):
async def test_prepared_content_invalid_id_returns_404(db_pool):
async def test_approve_review_all_unhealthy_returns_400(db_pool):
async def test_concurrent_approve_returns_409(db_pool):
async def test_prepared_content_large_payload(db_pool):
async def test_prepared_content_empty_returns_empty_dict(db_pool):

### File: /Users/bparlan/devcode/autonomedia/tests/unit/test_worker_tracking.py
import pytest
from src.database.client import DatabaseClient
async def test_worker_updates_attempt_count():

### File: /Users/bparlan/devcode/autonomedia/tests/unit/test_entity_normalizer.py
from src.autonomedia.content.transforms.entity_normalizer import EntityNormalizer
def test_normalization():

### File: /Users/bparlan/devcode/autonomedia/tests/integration/test_m3_api.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.autonomedia.core.db import get_db
from src.autonomedia.web.main import app
from src.autonomedia.web.models import Base, Comment, Content, Like, User
def override_get_db():
def setup_test_db():
def mock_user():
def test_create_comment():
def test_get_comments_for_content():
def test_create_like():
def test_create_like_duplicate():
def test_delete_like():
def test_create_content():
def test_update_content():
def test_get_all_content():
def test_get_content_by_id():
def test_get_content_by_id_not_found():

### File: /Users/bparlan/devcode/autonomedia/tests/integration/test_m10_runtime.py
import pytest
async def test_migration_and_atomic_claim(db_pool):
async def test_sigterm_handling(db_pool):
async def test_retry_mechanism(db_pool):

### File: /Users/bparlan/devcode/autonomedia/tests/integration/test_m11_self_healing.py
from src.autonomedia.core.error_resolver import ErrorResolver
def test_error_resolver_classifies_transient_vs_fatal():
class MockWorker:
def __init__(self, platform_id):
def test_circuit_breaker_halts_paused_platform():
def test_artifact_generation_triggered_on_exception():

### File: /Users/bparlan/devcode/autonomedia/tests/integration/test_m13_s1_verification_status.py
import json
import pytest
async def test_tc_m13_01_migration_creates_column(db_pool):
async def test_tc_m13_02_migration_is_idempotent(db_pool):
async def test_tc_m13_03_default_jsonb_value(db_pool):
async def test_tc_m13_04_large_json_payload(db_pool):
async def test_tc_m13_05_malformed_json_rejected(db_pool):
async def test_tc_m13_06_concurrent_updates(db_pool):
def test_tc_m13_07_interrupted_migration_recovery():

### File: /Users/bparlan/devcode/autonomedia/tests/integration/test_worker_runtime.py
import asyncio
import json
import logging
from unittest.mock import patch
import pytest
from src.autonomedia.core.worker import poller, worker
from src.database.client import DatabaseClient
async def test_worker_flow():

### File: /Users/bparlan/devcode/autonomedia/tests/ai/test_rewrite_pipeline.py
import pytest
from src.autonomedia.ai.rewriting.context import RewriteContext
async def test_rewrite_context_serialization():

### File: /Users/bparlan/devcode/autonomedia/tests/ai/test_rewrite.py
import json
import os
import pytest
from dotenv import load_dotenv
from autonomedia.ai.rewriting.context import RewriteContext
from autonomedia.ai.rewriting.gemini import GeminiProvider
async def test_rewrite_golden_master():

### File: /Users/bparlan/devcode/autonomedia/tests/e2e/test_dashboard_crud.py
import asyncio
import json
import pytest
from playwright.async_api import async_playwright
async def test_dashboard_edit_content(db_pool):

### File: /Users/bparlan/devcode/autonomedia/scripts/update_platforms.py
import asyncio
import json
import asyncpg
async def update():

### File: /Users/bparlan/devcode/autonomedia/scripts/test_mastodon_profile.py
from pathlib import Path
from playwright.sync_api import sync_playwright
def main() -> None:

### File: /Users/bparlan/devcode/autonomedia/scripts/ingest_content.py
import asyncio
import csv
import json
import re
import sys
from pathlib import Path
from src.database.client import DatabaseClient
from src.database.schema import INIT_SCHEMA
async def ingest_csv(csv_path: Path):

### File: /Users/bparlan/devcode/autonomedia/scripts/test_mastodon_compose.py
import asyncio
import os
import sys
import time
from datetime import UTC, datetime
from playwright.async_api import async_playwright
def log(level, message, **kwargs):
async def run():

### File: /Users/bparlan/devcode/autonomedia/scripts/test_mastodon_post.py
import asyncio
import os
import sys
import uuid
from datetime import UTC, datetime
from playwright.async_api import async_playwright
def log(level, message, **kwargs):
async def run():

### File: /Users/bparlan/devcode/autonomedia/scripts/clear_content.py
import asyncio
from src.database.client import DatabaseClient
async def main():

### File: /Users/bparlan/devcode/autonomedia/scripts/checks/debug_tables.py
import asyncio
async def check():

### File: /Users/bparlan/devcode/autonomedia/scripts/checks/check_platforms.py
import asyncpg
async def check():

### File: /Users/bparlan/devcode/autonomedia/scripts/checks/check_health.py
import asyncio
import os
import asyncpg
async def check():

### File: /Users/bparlan/devcode/autonomedia/scripts/checks/check_status.py
import asyncio
import asyncpg
async def main():

### File: /Users/bparlan/devcode/autonomedia/scripts/checks/verify_telegram.py
import asyncio
from dotenv import load_dotenv
from src.autonomedia.core.observability.telegram import notifier
async def test_telegram():

### File: /Users/bparlan/devcode/autonomedia/scripts/checks/check_db.py
import asyncio
import asyncpg
async def check():

### File: /Users/bparlan/devcode/autonomedia/scripts/checks/verify_health.py
import asyncio
import os
import asyncpg
async def check():

### File: /Users/bparlan/devcode/autonomedia/scripts/checks/check_data.py
import asyncio
import asyncpg
async def check():

### File: /Users/bparlan/devcode/autonomedia/scripts/checks/check_all_platforms.py
import asyncio
import asyncpg
async def check():

### File: /Users/bparlan/devcode/autonomedia/scripts/checks/run_daily_posting.py
import asyncio
import sys
from src.autonomedia.core.posting_routine import posting_routine
def main():

### File: /Users/bparlan/devcode/autonomedia/scripts/db/migrate_M11_platform_metadata.py
import asyncio
import sys
from pathlib import Path
import asyncpg
async def migrate():

### File: /Users/bparlan/devcode/autonomedia/scripts/db/verify_db.py
import asyncio
import asyncpg
async def verify_ingestion():

### File: /Users/bparlan/devcode/autonomedia/scripts/db/db_migration.py
import asyncio
import os
import asyncpg
async def migrate():

### File: /Users/bparlan/devcode/autonomedia/scripts/db/db_migration_m12.py
async def apply_migration(conn):
async def rollback_migration(conn):

### File: /Users/bparlan/devcode/autonomedia/scripts/db/migrate_db.py
import asyncio
import sys
from pathlib import Path
import asyncpg
async def migrate():

### File: /Users/bparlan/devcode/autonomedia/scripts/db/db_update.py
import asyncio
from src.database.client import DatabaseClient
from src.database.schema import INIT_SCHEMA
async def update():

### File: /Users/bparlan/devcode/autonomedia/scripts/db/migrate_M13_verification_status.py
import asyncio
import os
import asyncpg
async def migrate():

### File: /Users/bparlan/devcode/autonomedia/scripts/db/db_migration_v2.py
import asyncio
import os
import asyncpg
async def migrate():

### File: /Users/bparlan/devcode/autonomedia/scripts/db/init_verifications.sql.py
import os
import sqlite3
def migrate():

### File: /Users/bparlan/devcode/autonomedia/scripts/db/db_migration_settings.py
import asyncio
import os
import asyncpg
async def migrate():

### File: /Users/bparlan/devcode/autonomedia/scripts/db/migrate_m10.py
import asyncio
import sys
from pathlib import Path
import asyncpg
async def migrate():

### File: /Users/bparlan/devcode/autonomedia/scripts/db/create_db.py
import asyncio
import asyncpg
async def create_db():

### File: /Users/bparlan/devcode/autonomedia/src/database/client.py
import os
import asyncpg
class DatabaseClient:
async def get_pool(cls):
async def close(cls):

### File: /Users/bparlan/devcode/autonomedia/src/web/app.py
import asyncio
import json
import logging
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os
import tempfile
from src.database.client import DatabaseClient
def fromjson(value):
async def get_sidebar_data(conn):
async def command_center(request: Request):
async def content_page(request: Request):
async def rewrites_page(request: Request):
async def get_prepared_content(id: str):
async def add_item(
async def edit_content_row(request: Request, id: str):
async def cancel_edit_content(request: Request, id: str):
async def save_content_row(
async def delete_item(id: str):
async def approve_idea(request: Request, id: str):
from src.autonomedia.ai.planner import process_rewrites
async def status_fragment(request: Request, id: str):
async def batch_generate(request: Request):
async def reset_failure(id: str):
async def review_page(request: Request, id: str):
async def approve_review(request: Request, id: str):
async def registry_page(request: Request):
async def platforms_page(request: Request):
async def update_registry(request: Request):
async def remove_from_queue(request: Request, id: str):

### File: /Users/bparlan/devcode/autonomedia/src/autonomedia/platforms/mastodon/selectors.py
from playwright.async_api import Locator, Page
def compose_textbox(page: Page) -> Locator:

### File: /Users/bparlan/devcode/autonomedia/src/autonomedia/platforms/mastodon/task_handler.py
import asyncio
import json
import logging
import os
import random
import re
from datetime import UTC, datetime
from autonomedia.browser.provider import BrowserProvider
from autonomedia.core.config import settings
def log_event(message, task_id, level="info", **kwargs):
async def publish_mastodon(content: str, task_id: str = None):

### File: /Users/bparlan/devcode/autonomedia/src/autonomedia/ingestion/content_ingestor.py
def capture_content_idea(idea_text: str) -> dict:

### File: /Users/bparlan/devcode/autonomedia/src/autonomedia/core/worker.py
import asyncio
import json
import logging
import signal
import sys
from datetime import UTC, datetime
from pathlib import Path
from src.database.client import DatabaseClient
from autonomedia.core.logger import log_post_event
from autonomedia.platforms.mastodon.task_handler import publish_mastodon
from src.autonomedia.core.error_resolver import ErrorResolver
async def is_platform_halted(platform):
async def execute_task(task):
async def worker(name, queue, stop_event):
async def poller(queue, stop_event):
async def main():

### File: /Users/bparlan/devcode/autonomedia/src/autonomedia/core/error_resolver.py
class ErrorResolver:
def classify(self, exception: Exception) -> str:

### File: /Users/bparlan/devcode/autonomedia/src/autonomedia/core/security.py
import datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from src.autonomedia.web.models import UserPydantic
async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserPydantic:

### File: /Users/bparlan/devcode/autonomedia/src/autonomedia/core/logger.py
from src.database.client import DatabaseClient
async def log_post_event(

### File: /Users/bparlan/devcode/autonomedia/src/autonomedia/core/poller.py
class StatusPoller:
def should_process(self, platform: dict) -> bool:

### File: /Users/bparlan/devcode/autonomedia/src/autonomedia/core/posting_routine.py
import asyncio
import json
import random
from datetime import UTC, datetime, timedelta
import structlog
from src.autonomedia.core.utils.verification import (
    get_verified_at_timestamp,
    is_platform_verified,
    parse_verification_status,
)
from src.autonomedia.platforms.mastodon.task_handler import publish_mastodon
from src.database.client import DatabaseClient
def log_event(message: str, level: str = "info", **kwargs):
async def _apply_randomized_delay(
async def _get_verified_content(platform: str) -> list:
async def _get_last_posted_at(platform: str) -> datetime | None:
async def posting_routine(dry_run: bool = False, max_items: int = 2):
import sys

### File: /Users/bparlan/devcode/autonomedia/src/autonomedia/core/config/__init__.py
from .settings import settings as settings

### File: /Users/bparlan/devcode/autonomedia/src/autonomedia/core/config/settings.py
import os
class Settings:

### File: /Users/bparlan/devcode/autonomedia/src/autonomedia/core/utils/verification.py
import json
from typing import Any
def parse_verification_status(value: Any) -> dict:
def get_platform_verification(verification_status: dict, platform: str) -> dict:
def is_platform_verified(verification_status: dict, platform: str) -> bool:
def get_verified_at_timestamp(verification_status: dict, platform: str) -> str:

### File: /Users/bparlan/devcode/autonomedia/src/autonomedia/core/observability/monitor.py
import logging
from src.autonomedia.core.observability.telegram import notifier
from src.database.client import DatabaseClient
class PassiveHealthMonitor:
async def run(cls):
import asyncio

### File: /Users/bparlan/devcode/autonomedia/src/autonomedia/core/observability/telegram.py
import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from src.database.client import DatabaseClient
async def pause_platform(update: Update, context: ContextTypes.DEFAULT_TYPE):
async def resume_platform(update: Update, context: ContextTypes.DEFAULT_TYPE):
class TelegramNotifier:
def __init__(self):
async def start_polling(self):
async def notify(self, message: str):

### File: /Users/bparlan/devcode/autonomedia/src/autonomedia/core/storage/analysis_storage.py
import json
import asyncpg
from src.database.client import DatabaseClient
class StorageError(Exception):
class AnalysisStorage:
def __init__(self):
async def save_analysis_result(self, analysis_data: dict) -> None:

### File: /Users/bparlan/devcode/autonomedia/src/autonomedia/core/db/__init__.py
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
def get_db():

### File: /Users/bparlan/devcode/autonomedia/src/autonomedia/web/models.py
import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
class User(Base):
class Content(Base):
class Comment(Base):
class Like(Base):
class UserPydantic(BaseModel):
class ContentPydantic(BaseModel):
class CommentPydantic(BaseModel):
class LikePydantic(BaseModel):

### File: /Users/bparlan/devcode/autonomedia/src/autonomedia/web/main.py
from fastapi import FastAPI
from src.autonomedia.web.api.comments import router as comments_router
from src.autonomedia.web.api.content import router as content_router
from src.autonomedia.web.api.likes import router as likes_router

### File: /Users/bparlan/devcode/autonomedia/src/autonomedia/web/api/likes.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.autonomedia.core.db import get_db
from src.autonomedia.core.security import get_current_user
from src.autonomedia.web.models import (
    Content,
    Like,
    LikePydantic,
    UserPydantic,
)
class LikeRequest(BaseModel):
class UnlikeRequest(BaseModel):
def create_like(
def delete_like(

### File: /Users/bparlan/devcode/autonomedia/src/autonomedia/web/api/content.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.autonomedia.core.db import get_db
from src.autonomedia.core.security import get_current_user
from src.autonomedia.web.models import (
    Content,
    ContentPydantic,
    UserPydantic,
)
class CreateContentRequest(BaseModel):
class UpdateContentRequest(BaseModel):
def create_content(
def update_content(
def get_all_content(
def get_content_by_id(

### File: /Users/bparlan/devcode/autonomedia/src/autonomedia/web/api/comments.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.autonomedia.core.db import get_db
from src.autonomedia.core.security import get_current_user
from src.autonomedia.web.models import (  # Import Pydantic models
    Comment,
    CommentPydantic,
    Content,
    UserPydantic,
)
class CreateCommentRequest(BaseModel):
def create_comment(comment_data: CreateCommentRequest, db: Session = Depends(get_db), current_user: UserPydantic = Depends(get_current_user)):
def get_comments_for_content(content_id: int, db: Session = Depends(get_db), current_user: UserPydantic = Depends(get_current_user)):

### File: /Users/bparlan/devcode/autonomedia/src/autonomedia/agents/posting_secretary/worker.py
import asyncio
import json
import structlog
from src.autonomedia.ai.moderation import ModerationAdapter
from src.autonomedia.ai.rewriting.context import RewriteContext
from src.autonomedia.ai.rewriting.gemini import GeminiProvider
from src.autonomedia.content.transforms.entity_normalizer import EntityNormalizer
from src.autonomedia.core.utils.verification import (
    is_platform_verified,
    parse_verification_status,
)
from src.database.client import DatabaseClient
class PostingSecretary:
def __init__(self):
async def run(self):
async def process_verified_content(self):
async def process_new_ideas(self):

### File: /Users/bparlan/devcode/autonomedia/src/autonomedia/content/transforms/entity_normalizer.py
import json
import logging
from pathlib import Path
class EntityNormalizer:
def __init__(
def _load_registry(self) -> dict:
def get_handle(self, entity_key: str, platform: str) -> str | None:
def normalize_text(self, text: str, platform: str) -> str:

### File: /Users/bparlan/devcode/autonomedia/src/autonomedia/browser/provider.py
import asyncio
import logging
import random
from playwright.async_api import async_playwright
class BrowserProvider:
def __init__(self, browser_data_dir: str, task_id: str = None):
def _get_random_viewport(self):
async def _human_delay(self):
async def __aenter__(self):
async def __aexit__(self, exc_type, exc_val, exc_tb):
async def _capture_failure(self, exception):

### File: /Users/bparlan/devcode/autonomedia/src/autonomedia/ai/planner.py
import json
import logging
from src.autonomedia.ai.rewriting.context import RewriteContext
from src.autonomedia.ai.rewriting.gemini import GeminiProvider
from src.autonomedia.content.transforms.entity_normalizer import EntityNormalizer
from src.database.client import DatabaseClient
async def process_rewrites():

### File: /Users/bparlan/devcode/autonomedia/src/autonomedia/ai/analysis.py
import json
from src.autonomedia.ai.rewriting.gemini import GeminiAIClient
from src.autonomedia.core.storage.analysis_storage import AnalysisStorage
class AIAnalysisError(Exception):
def perform_ai_analysis(content_idea: dict) -> str:

### File: /Users/bparlan/devcode/autonomedia/src/autonomedia/ai/rewriting/__init__.py
from .base import RewriteProvider
from .gemini import GeminiProvider

### File: /Users/bparlan/devcode/autonomedia/src/autonomedia/ai/rewriting/gemini.py
from src.autonomedia.ai.analysis import AIAnalysisError
class GeminiAIClient:
def analyze_idea(self, idea_text: str) -> dict:

### File: /Users/bparlan/devcode/autonomedia/src/autonomedia/ai/rewriting/context.py
from dataclasses import dataclass, field
class RewriteContext:
def to_prompt_block(self) -> str:

### File: /Users/bparlan/devcode/autonomedia/src/autonomedia/ai/rewriting/base.py
from abc import ABC, abstractmethod
from .context import RewriteContext
class RewriteProvider(ABC):
async def rewrite(self, context: RewriteContext, prompt: str) -> str:

### File: /Users/bparlan/devcode/autonomedia/src/autonomedia/ai/moderation/adapter.py
class ModerationError(Exception):
class ModerationAdapter:
def validate(cls, platform: str, content: str) -> bool:

### File: /Users/bparlan/devcode/autonomedia/src/autonomedia/ai/moderation/__init__.py
from .adapter import ModerationAdapter, ModerationError

### File: /Users/bparlan/devcode/autonomedia/src/autonomedia/apps/worker/posting_executor.py
import asyncio
import json
import structlog
from src.autonomedia.platforms.mastodon.task_handler import publish_mastodon
from src.database.client import DatabaseClient
class PostingWorker:
def __init__(self):
async def run(self):
async def process_prepared_content(self):

