"""Other Us — FastAPI application entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import auth, auth_email, profiles, experiments, chat, users
from app.services.redis_service import close_redis

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown
    await close_redis()


app = FastAPI(
    title="Other Us API",
    description="Backend API for the Other Us social networking platform.",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:8081",
        "http://localhost:19006",
        "http://localhost:3000",
        "exp://localhost:8081",
        "http://localhost:8080",
        "exp://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(auth_email.router)
app.include_router(profiles.router)
app.include_router(experiments.router)
app.include_router(chat.router)
app.include_router(users.router)


@app.get("/health")
async def health_check():
    return {"status": "ok", "app": settings.app_name}
