# src/autonomedia/api/router.py

"""
API Router Module

Provides routing for API endpoints including /api/health.
"""

from fastapi import APIRouter
from .health import get_health_status

# Create API router
api_router = APIRouter()

# Include health endpoint
api_router.add_api_route("/api/health", get_health_status, methods=["GET"])
