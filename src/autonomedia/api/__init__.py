# src/autonomedia/api/__init__.py

"""
Infrastructure Data Endpoint for Health Dashboard
Provides HTTP GET /api/health endpoint for dashboard data consumption.
"""

__version__ = "1.0.0"

# Django-style URL routing registration
# In a real Django/FastAPI app, this would be registered in urls.py
# For this implementation, we'll provide the endpoint module directly

from .health import get_health_status

__all__ = ["get_health_status"]
