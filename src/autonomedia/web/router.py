# src/autonomedia/web/router.py

from fastapi import APIRouter

# Import health router if available
try:
    from autonomedia.web.api.health import router as health_router
except ImportError:
    health_router = None

# Create an APIRouter instance
router = APIRouter()

# Include health router if available
if health_router:
    router.include_router(health_router)

# For the UI route, we'll just define a path operation directly in the server file
# or assume a separate mechanism handles UI routing (e.g., static files).
# This router focuses on API endpoints.

# In a typical FastAPI app, you would include this router in the main app:
# app.include_router(router)
