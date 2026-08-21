from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.autonomedia.web.api.comments import router as comments_router
from src.autonomedia.web.api.content import router as content_router
from src.autonomedia.web.api.likes import router as likes_router

app = FastAPI()


@app.get("/")
async def root():
    """Root endpoint - API welcome."""
    return JSONResponse({
        "status": "ok",
        "service": "autonomedia-api",
        "endpoints": ["/content", "/comments", "/likes", "/health"]
    })


@app.get("/health")
async def health():
    """Health check endpoint."""
    return JSONResponse({
        "status": "healthy",
        "timestamp": "2026-07-09T00:00:00Z"
    })


app.include_router(comments_router)
app.include_router(likes_router)
app.include_router(content_router)