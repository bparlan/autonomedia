# src/autonomedia/api/health.py

"""
Infrastructure Data Endpoint for Health Dashboard

Provides HTTP GET /api/health endpoint for dashboard data consumption.
Returns JSON with health status for database, runtime, tests, and src components.
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Import the health status integration function
from autonomedia.checks.healthcheck import _get_status_data

# Create FastAPI app instance for the API endpoint
app = FastAPI(
    title="Autonomedia Health API",
    description="Infrastructure health monitoring endpoint for dashboard",
    version="1.0.0"
)


@app.get("/api/health")
async def get_health_status() -> JSONResponse:
    """
    Get infrastructure health status.

    Returns:
        JSONResponse: Status for database, runtime, tests, and src components.
                      Each component returns "healthy" or "unhealthy".
    """
    try:
        # Get status data from healthcheck utility
        status_data = _get_status_data()

        # Return 200 OK with status data
        return JSONResponse(
            status_code=200,
            content=status_data,
            media_type="application/json"
        )

    except Exception as e:
        # Return 500 Internal Server Error on unexpected errors
        return JSONResponse(
            status_code=500,
            content={
                "database": "unhealthy",
                "runtime": "unhealthy",
                "tests": "unhealthy",
                "src": "unhealthy",
                "error": f"Internal server error: {str(e)}"
            },
            media_type="application/json"
        )


