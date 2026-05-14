"""
FastAPI application factory.

Creates and configures the FastAPI application with CORS, exception handlers,
and API routes.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.core.config import settings
from app.api.routes import workflows, tasks, artifacts, health


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        description=(
            "FinAgentFlow — An AI-driven platform for automating banking tasks "
            "through intelligent workflow orchestration."
        ),
        version=settings.app_version,
        docs_url=f"{settings.api_prefix}/docs",
        redoc_url=f"{settings.api_prefix}/redoc",
        openapi_url=f"{settings.api_prefix}/openapi.json",
    )

    # ── CORS ──────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Restrict in production!
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routes ────────────────────────────────────────────────────────────
    app.include_router(health.router, prefix=settings.api_prefix, tags=["Health"])
    app.include_router(workflows.router, prefix=settings.api_prefix, tags=["Workflows"])
    app.include_router(tasks.router, prefix=settings.api_prefix, tags=["Tasks"])
    app.include_router(artifacts.router, prefix=settings.api_prefix, tags=["Artifacts"])

    # ── Convenience redirects ─────────────────────────────────────────────
    @app.get("/docs", include_in_schema=False)
    async def docs_redirect():
        return RedirectResponse(url=f"{settings.api_prefix}/docs")

    @app.get("/redoc", include_in_schema=False)
    async def redoc_redirect():
        return RedirectResponse(url=f"{settings.api_prefix}/redoc")

    return app
