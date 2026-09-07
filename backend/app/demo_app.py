"""Public demo surface: synthetic read-only data and isolated capability sessions."""
import asyncio
import hashlib
import time
from urllib.parse import urlsplit
from contextlib import asynccontextmanager, suppress
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from starlette.concurrency import run_in_threadpool
from app.core.config import settings
from app.database.connection import SessionLocal
from app.database.init_db import init_db
from app.services.import_sessions import cleanup_expired
from app.views import dashboard_view, import_view


def maintenance():
    with SessionLocal.begin() as db:
        cleanup_expired(db)


def create_demo_app():
    if not settings.local_demo and not settings.database_url.startswith(("postgresql://", "postgresql+psycopg2://")):
        raise RuntimeError("Public DEMO_MODE requires PostgreSQL. SQLite is only allowed by the loopback local demo launcher.")
    origins = [s.strip().rstrip("/") for s in settings.cors_allowed_origins.split(",") if s.strip()]
    if not origins or "*" in origins:
        raise RuntimeError("Set explicit CORS_ALLOWED_ORIGINS for the demo frontend.")
    if not settings.local_demo:
        for origin in origins:
            parsed = urlsplit(origin)
            if parsed.scheme != "https" or not parsed.netloc or parsed.hostname in {"localhost", "127.0.0.1"} or parsed.path or parsed.query or parsed.fragment or parsed.username:
                raise RuntimeError("Public demo requires CORS_ALLOWED_ORIGINS to contain exact deployed HTTPS frontend origins.")

    @asynccontextmanager
    async def lifespan(app):
        init_db()
        from scripts.seed_demo import seed_demo
        with SessionLocal.begin() as db:
            seed_demo(db)
        await run_in_threadpool(maintenance)
        async def sweep():
            while True:
                await asyncio.sleep(900)
                await run_in_threadpool(maintenance)
        task = asyncio.create_task(sweep())
        yield
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task

    app = FastAPI(title="FinTrack reviewed-data demo", lifespan=lifespan)
    app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["GET", "POST", "DELETE"],
                       allow_headers=["Content-Type", "X-Demo-Session", "X-File-Name"], allow_credentials=False)
    buckets = {}

    @app.middleware("http")
    async def safety_headers(request, call_next):
        # Per-process abuse guard. Hash addresses in memory; never store addresses or financial rows.
        if request.method == "POST":
            size = request.headers.get("content-length", "")
            if not size.isdigit() or int(size) > 5 * 1024 * 1024:
                return JSONResponse({"detail": "A bounded request body of at most 5 MB is required."}, status_code=413)
            now = time.monotonic()
            key = hashlib.sha256((request.client.host if request.client else "unknown").encode()).hexdigest()
            bucket = buckets.setdefault(key, [])
            bucket[:] = [stamp for stamp in bucket if now - stamp < 60]
            if len(bucket) >= 60:
                return JSONResponse({"detail": "Demo request limit reached. Try again in a minute."}, status_code=429)
            bucket.append(now)
            if len(buckets) > 5000:
                buckets.clear()
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    @app.get("/health")
    def health():
        try:
            with SessionLocal() as db:
                db.execute(text("SELECT 1"))
            return {"status": "ok", "service": "FinTrack demo"}
        except Exception:
            return JSONResponse({"status": "unavailable"}, status_code=503)

    app.router.routes.extend(route for route in dashboard_view.router.routes if route.path == "/dashboard/demo")
    app.include_router(import_view.router)
    return app
