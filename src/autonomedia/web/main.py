from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.autonomedia.web.api.comments import router as comments_router
from src.autonomedia.web.api.content import router as content_router
from src.autonomedia.web.api.likes import router as likes_router
from src.autonomedia.web.router import router as web_router
from src.autonomedia.api.router import api_router

app = FastAPI()


@app.get("/")
async def root():
    """Root endpoint - API welcome."""
    return JSONResponse({
        "status": "ok",
        "service": "autonomedia-api",
        "endpoints": ["/content", "/comments", "/likes", "/api/health", "/health"]
    })


app.include_router(comments_router)
app.include_router(likes_router)
app.include_router(content_router)
app.include_router(web_router)
app.include_router(api_router)