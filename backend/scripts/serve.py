"""Render entrypoint; PORT is supplied by the hosting environment."""
import os
import uvicorn


if __name__ == "__main__":
    if os.getenv("DEMO_MODE", "").lower() not in {"1", "true"}:
        raise RuntimeError("Public demo launcher requires DEMO_MODE=true; legacy routes must not be publicly exposed.")
    if os.getenv("LOCAL_DEMO", "").lower() in {"1", "true"}:
        raise RuntimeError("Use scripts.run_demo for local SQLite. LOCAL_DEMO must be false on public hosting.")
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), access_log=False, proxy_headers=True)
