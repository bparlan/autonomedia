from fastapi import FastAPI

from src.autonomedia.web.api.comments import router as comments_router
from src.autonomedia.web.api.content import router as content_router
from src.autonomedia.web.api.likes import router as likes_router

app = FastAPI()

app.include_router(comments_router)
app.include_router(likes_router)
app.include_router(content_router)
